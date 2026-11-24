"""
Celery görevleri:
  - generate_emails_for_campaign: Claude AI ile e-mail üret
  - send_approved_emails: Onaylı mailleri Gmail'den gönder
"""

import logging
import random
import time

from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def generate_emails_for_campaign(self, campaign_id):
    """
    Kampanyadaki her lead için Claude API'ye istek atarak
    kişiselleştirilmiş e-mail üretir ve veritabanına kaydeder.
    """
    from campaigns.models import Campaign
    from emails.models import GeneratedEmail

    try:
        kampanya = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        logger.error(f"Kampanya bulunamadı: {campaign_id}")
        return

    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=(
            "Sen profesyonel bir B2B satış yazarısın. "
            "Verilen bilgilere göre kişiselleştirilmiş, doğal ve samimi bir soğuk e-mail yaz. "
            "ÇIKTI FORMATI (kesinlikle bu şekilde yaz, başka hiçbir şey ekleme):\n"
            "Konu: <e-mail konusu>\n\n"
            "<e-mail gövdesi>"
        ),
    )
    uretilen = 0
    atlanan = 0

    for lead in kampanya.leads.filter(is_unsubscribed=False):
        # Bu lead için zaten mail üretilmişse atla
        if GeneratedEmail.objects.filter(campaign=kampanya, lead=lead).exists():
            atlanan += 1
            continue

        try:
            # Prompt şablonunu lead verisiyle doldur
            prompt = kampanya.prompt_template.format(
                lead=lead,
                service_description=kampanya.service_description,
            )

            yanit_obj = model.generate_content(prompt)
            yanit = yanit_obj.text.strip()

            # "Konu: ..." satırını ve gövdeyi ayır
            satirlar = yanit.split("\n")
            konu = f"Merhaba {lead.first_name}"
            govde_baslangic = 0

            for i, satir in enumerate(satirlar):
                if satir.strip().lower().startswith("konu:"):
                    konu = satir.strip()[5:].strip()
                    # Boş satırı atla
                    govde_baslangic = i + 2
                    break

            govde_satirlari = satirlar[govde_baslangic:]

            # Baştaki boş satırları temizle
            while govde_satirlari and not govde_satirlari[0].strip():
                govde_satirlari.pop(0)

            govde = "\n".join(govde_satirlari).strip()

            if not govde:
                govde = yanit

            GeneratedEmail.objects.create(
                campaign=kampanya,
                lead=lead,
                subject=konu,
                body=govde,
                status=GeneratedEmail.Status.PENDING,
            )
            uretilen += 1

            # Claude API rate limit için kısa bekleme
            time.sleep(0.5)

        except Exception as hata:
            logger.error(f"Lead {lead.email} için mail üretilemedi: {hata}")
            atlanan += 1

    logger.info(
        f"Kampanya {campaign_id}: {uretilen} mail üretildi, {atlanan} atlandı."
    )
    return {"uretilen": uretilen, "atlanan": atlanan}


@shared_task(bind=True, max_retries=2)
def send_approved_emails(self, campaign_id):
    """
    Onaylı e-mailleri Gmail API aracılığıyla gönderir.
    Günlük limit ve rastgele bekleme (spam koruması) uygulanır.
    """
    from campaigns.models import Campaign
    from emails.gmail_service import send_email_via_gmail
    from emails.models import GeneratedEmail

    try:
        kampanya = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        logger.error(f"Kampanya bulunamadı: {campaign_id}")
        return

    # Bugün kaç mail gönderildi?
    bugun = timezone.now().date()
    bugun_gonderilen = GeneratedEmail.objects.filter(
        campaign=kampanya,
        sent_at__date=bugun,
        status__in=[
            GeneratedEmail.Status.SENT,
            GeneratedEmail.Status.OPENED,
            GeneratedEmail.Status.REPLIED,
        ],
    ).count()

    # Tüm onaylı mailleri al
    onaylı_mailler = GeneratedEmail.objects.filter(
        campaign=kampanya,
        status=GeneratedEmail.Status.APPROVED,
    ).select_related("lead", "campaign__user")

    gonderilen = 0
    basarisiz = 0

    for email in onaylı_mailler:
        # Günlük limit doluysa dur
        if bugun_gonderilen >= kampanya.daily_limit:
            logger.info(
                f"Kampanya {campaign_id}: Günlük limit ({kampanya.daily_limit}) doldu."
            )
            break

        try:
            send_email_via_gmail(email)
            email.status = GeneratedEmail.Status.SENT
            email.sent_at = timezone.now()
            email.save()

            bugun_gonderilen += 1
            gonderilen += 1

            # Spam'e düşmemek için 30–90 saniye rastgele bekleme
            bekleme = random.randint(30, 90)
            logger.debug(f"Sonraki mail için {bekleme}sn bekleniyor...")
            time.sleep(bekleme)

        except Exception as hata:
            logger.error(f"Mail gönderilemedi ({email.lead.email}): {hata}")
            email.status = GeneratedEmail.Status.FAILED
            email.save()
            basarisiz += 1

    # Tüm onaylı mailler gönderildiyse kampanyayı tamamlandı olarak işaretle
    kalan = GeneratedEmail.objects.filter(
        campaign=kampanya, status=GeneratedEmail.Status.APPROVED
    ).count()

    if kalan == 0 and gonderilen > 0:
        kampanya.status = Campaign.Status.COMPLETED
        kampanya.save()

    logger.info(
        f"Kampanya {campaign_id}: {gonderilen} gönderildi, {basarisiz} başarısız."
    )
    return {"gonderilen": gonderilen, "basarisiz": basarisiz}
