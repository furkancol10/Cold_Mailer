"""
Gmail API üzerinden e-mail gönderme servisi.
Google OAuth2 tokeni allauth'un SocialToken tablosundan alır.
"""

import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings

logger = logging.getLogger(__name__)


def _gmail_credentials(user):
    """
    Kullanıcının Google OAuth2 tokenlarını alır ve Credentials nesnesi döner.
    Token süresi dolmuşsa otomatik yeniler.
    """
    from allauth.socialaccount.models import SocialAccount, SocialToken
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    try:
        account = SocialAccount.objects.get(user=user, provider="google")
        token = SocialToken.objects.get(account=account)
    except Exception:
        raise ValueError(
            f"{user.email} için Gmail bağlantısı bulunamadı. "
            "Lütfen Google hesabınızla giriş yapın."
        )

    creds = Credentials(
        token=token.token,
        refresh_token=token.token_secret,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )

    # Token süresi dolmuşsa yenile ve kaydet
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token.token = creds.token
            token.save(update_fields=["token"])
            logger.info(f"{user.email} için Gmail token yenilendi.")
        except Exception as e:
            raise ValueError(f"Gmail token yenilenemedi: {e}")

    return creds


def send_email_via_gmail(generated_email):
    """
    Gmail API aracılığıyla e-mail gönderir.
    Mail gövdesine tracking pixel ve abonelikten çıkma linki ekler.
    """
    from googleapiclient.discovery import build

    kullanici = generated_email.campaign.user
    creds = _gmail_credentials(kullanici)
    servis = build("gmail", "v1", credentials=creds)

    # Tracking pixel ve abonelikten çıkma URL'leri
    pixel_url = f"{settings.APP_BASE_URL}/emails/t/{generated_email.tracking_id}/"
    unsub_url = f"{settings.APP_BASE_URL}/emails/unsub/{generated_email.tracking_id}/"

    # HTML gövde oluştur
    html_govde = generated_email.body.replace("\n", "<br>\n")
    html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
  {html_govde}
  <br><br>
  <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
  <p style="color: #aaa; font-size: 11px; margin: 0;">
    Bu e-postayı artık almak istemiyorsanız
    <a href="{unsub_url}" style="color: #888;">buraya tıklayın</a>.
  </p>
  <img src="{pixel_url}" width="1" height="1" alt="" style="display:none; border:0;">
</body>
</html>"""

    # MIME mesajı oluştur
    mesaj = MIMEMultipart("alternative")
    mesaj["Subject"] = generated_email.subject
    mesaj["From"] = kullanici.email
    mesaj["To"] = generated_email.lead.email

    # Hem düz metin hem HTML ekle (e-mail istemcileri birini seçer)
    mesaj.attach(MIMEText(generated_email.body, "plain", "utf-8"))
    mesaj.attach(MIMEText(html_icerik, "html", "utf-8"))

    ham_veri = base64.urlsafe_b64encode(mesaj.as_bytes()).decode()
    sonuc = servis.users().messages().send(
        userId="me", body={"raw": ham_veri}
    ).execute()

    # Gmail mesaj ID'sini kaydet (cevap takibi için)
    generated_email.gmail_message_id = sonuc.get("id", "")
    generated_email.save(update_fields=["gmail_message_id"])

    logger.info(f"Mail gönderildi: {generated_email.lead.email} → Gmail ID: {sonuc.get('id')}")
    return sonuc
