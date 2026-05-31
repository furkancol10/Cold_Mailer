"""
E-mail view'ları:
  - Mail onaylama (tek/toplu)
  - Mail düzenleme
  - Mail atlama
  - Tracking pixel (açılma takibi)
  - Abonelikten çıkma
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GeneratedEmailForm
from .models import EmailEvent, GeneratedEmail


@login_required
def email_approve(request, pk):
    """Tek bir maili onayla: PENDING → APPROVED."""
    email = get_object_or_404(GeneratedEmail, pk=pk, campaign__user=request.user)

    if request.method == "POST":
        email.status = GeneratedEmail.Status.APPROVED
        email.save()
        messages.success(request, f"{email.lead.full_name} için mail onaylandı.")

    return redirect("campaign_detail", pk=email.campaign_id)


@login_required
def email_approve_all(request, campaign_pk):
    """Kampanyadaki tüm bekleyen mailleri toplu onayla."""
    from campaigns.models import Campaign

    kampanya = get_object_or_404(Campaign, pk=campaign_pk, user=request.user)

    if request.method == "POST":
        sayi = kampanya.emails.filter(status=GeneratedEmail.Status.PENDING).update(
            status=GeneratedEmail.Status.APPROVED
        )
        messages.success(request, f"{sayi} mail onaylandı. Artık kampanyayı başlatabilirsiniz.")

    return redirect("campaign_detail", pk=campaign_pk)


@login_required
def email_skip(request, pk):
    """Maili atla: PENDING → SKIPPED (bu lead'e gönderilmeyecek)."""
    email = get_object_or_404(GeneratedEmail, pk=pk, campaign__user=request.user)

    if request.method == "POST":
        email.status = GeneratedEmail.Status.SKIPPED
        email.save()

    return redirect("campaign_detail", pk=email.campaign_id)


@login_required
def email_edit(request, pk):
    """AI'ın yazdığı maili kullanıcının düzenlemesine izin ver."""
    email = get_object_or_404(GeneratedEmail, pk=pk, campaign__user=request.user)

    if request.method == "POST":
        form = GeneratedEmailForm(request.POST, instance=email)
        if form.is_valid():
            mail = form.save(commit=False)
            # Düzenlendikten sonra otomatik onayla
            mail.status = GeneratedEmail.Status.APPROVED
            mail.save()
            messages.success(
                request,
                f"{email.lead.full_name} için mail düzenlendi ve onaylandı."
            )
            return redirect("campaign_detail", pk=email.campaign_id)
    else:
        form = GeneratedEmailForm(instance=email)

    return render(request, "emails/email_edit.html", {"form": form, "email": email})


def tracking_pixel(request, tracking_id):
    """
    Açılma takibi endpoint'i.
    E-maildeki gizli resim bu URL'ye istek attığında açılma kaydedilir.
    1x1 şeffaf GIF döner (görünmez).
    """
    try:
        email = GeneratedEmail.objects.get(tracking_id=tracking_id)

        # Açılma olayını kaydet
        EmailEvent.objects.create(
            email=email,
            event_type=EmailEvent.EventType.OPEN,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        # Sadece "Gönderildi" durumundaki maili "Açıldı" olarak güncelle
        if email.status == GeneratedEmail.Status.SENT:
            email.status = GeneratedEmail.Status.OPENED
            email.save(update_fields=["status"])

    except GeneratedEmail.DoesNotExist:
        pass  # Geçersiz tracking_id — sessizce devam et

    # 1x1 şeffaf GIF piksel (43 byte, sabit)
    pixel = bytes([
        0x47, 0x49, 0x46, 0x38, 0x39, 0x61,  # GIF89a
        0x01, 0x00, 0x01, 0x00, 0x80, 0x00, 0x00,
        0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00,
        0x21, 0xF9, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x2C, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
        0x02, 0x02, 0x44, 0x01, 0x00, 0x3B,
    ])
    return HttpResponse(pixel, content_type="image/gif")


def unsubscribe(request, tracking_id):
    """
    Abonelikten çıkma sayfası.
    Lead'i is_unsubscribed=True olarak işaretler, olayı kaydeder.
    """
    try:
        email = GeneratedEmail.objects.get(tracking_id=tracking_id)
        lead = email.lead

        if not lead.is_unsubscribed:
            lead.is_unsubscribed = True
            lead.save(update_fields=["is_unsubscribed"])

            EmailEvent.objects.create(
                email=email,
                event_type=EmailEvent.EventType.UNSUBSCRIBE,
                ip_address=request.META.get("REMOTE_ADDR"),
            )

        return render(request, "emails/unsubscribe.html", {"lead": lead})

    except GeneratedEmail.DoesNotExist:
        from django.http import Http404
        raise Http404("Geçersiz abonelik linki.")
