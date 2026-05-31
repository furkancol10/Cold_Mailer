"""
Kampanya view'ları: liste, oluşturma, düzenleme, silme,
AI mail üretimi ve gönderim başlatma.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from leads.models import Lead

from .forms import CampaignForm
from .models import Campaign


@login_required
def campaign_list(request):
    """Kullanıcının tüm kampanyalarını listeler."""
    kampanyalar = Campaign.objects.filter(user=request.user).prefetch_related("emails")
    context = {
        "campaigns": kampanyalar,
        "total": kampanyalar.count(),
    }
    return render(request, "campaigns/campaign_list.html", context)


@login_required
def campaign_create(request):
    """Yeni kampanya oluşturma formu."""
    if request.method == "POST":
        form = CampaignForm(request.user, request.POST)
        if form.is_valid():
            kampanya = form.save(commit=False)
            kampanya.user = request.user
            kampanya.save()
            form.save_m2m()  # lead'lerin M2M ilişkisini kaydet
            messages.success(request, f"'{kampanya.name}' kampanyası oluşturuldu.")
            return redirect("campaign_detail", pk=kampanya.pk)
    else:
        form = CampaignForm(request.user)

    context = {
        "form": form,
        "title": "Yeni Kampanya",
        "available_leads": Lead.objects.filter(user=request.user, is_unsubscribed=False),
        "selected_lead_ids": [],
    }
    return render(request, "campaigns/campaign_form.html", context)


@login_required
def campaign_edit(request, pk):
    """Mevcut kampanyayı düzenle."""
    kampanya = get_object_or_404(Campaign, pk=pk, user=request.user)

    if request.method == "POST":
        form = CampaignForm(request.user, request.POST, instance=kampanya)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{kampanya.name}' güncellendi.")
            return redirect("campaign_detail", pk=pk)
    else:
        form = CampaignForm(request.user, instance=kampanya)

    context = {
        "form": form,
        "campaign": kampanya,
        "title": "Kampanyayı Düzenle",
        "available_leads": Lead.objects.filter(user=request.user, is_unsubscribed=False),
        "selected_lead_ids": list(kampanya.leads.values_list("pk", flat=True)),
    }
    return render(request, "campaigns/campaign_form.html", context)


@login_required
def campaign_detail(request, pk):
    """Kampanya detay sayfası: e-mailler, istatistikler, aksiyonlar."""
    from emails.models import GeneratedEmail

    kampanya = get_object_or_404(Campaign, pk=pk, user=request.user)
    mailler = kampanya.emails.select_related("lead").order_by("lead__first_name")

    # İstatistik hesapla
    toplam = mailler.count()
    gonderilen = mailler.filter(
        status__in=[GeneratedEmail.Status.SENT, GeneratedEmail.Status.OPENED, GeneratedEmail.Status.REPLIED]
    ).count()
    acilan = mailler.filter(
        status__in=[GeneratedEmail.Status.OPENED, GeneratedEmail.Status.REPLIED]
    ).count()
    cevaplanan = mailler.filter(status=GeneratedEmail.Status.REPLIED).count()
    onaylanan = mailler.filter(status=GeneratedEmail.Status.APPROVED).count()
    bekleyen = mailler.filter(status=GeneratedEmail.Status.PENDING).count()

    context = {
        "campaign": kampanya,
        "emails": mailler,
        "stats": {
            "toplam_lead": kampanya.leads.count(),
            "uretilen": toplam,
            "bekleyen": bekleyen,
            "onaylanan": onaylanan,
            "gonderilen": gonderilen,
            "acilan": acilan,
            "cevaplanan": cevaplanan,
            "acilma_orani": round(acilan / gonderilen * 100) if gonderilen > 0 else 0,
            "cevap_orani": round(cevaplanan / gonderilen * 100) if gonderilen > 0 else 0,
        },
    }
    return render(request, "campaigns/campaign_detail.html", context)


@login_required
def campaign_delete(request, pk):
    """Kampanyayı sil — POST ile çalışır."""
    kampanya = get_object_or_404(Campaign, pk=pk, user=request.user)

    if request.method == "POST":
        isim = kampanya.name
        kampanya.delete()
        messages.success(request, f"'{isim}' kampanyası silindi.")
        return redirect("campaign_list")

    return render(request, "campaigns/campaign_confirm_delete.html", {"campaign": kampanya})


@login_required
def campaign_generate(request, pk):
    """AI ile e-mail üretimini Celery arka planında başlat."""
    from emails.tasks import generate_emails_for_campaign

    kampanya = get_object_or_404(Campaign, pk=pk, user=request.user)

    if request.method == "POST":
        lead_sayisi = kampanya.leads.filter(is_unsubscribed=False).count()

        if lead_sayisi == 0:
            messages.error(request, "Kampanyada lead yok. Önce lead ekleyin.")
            return redirect("campaign_detail", pk=pk)

        generate_emails_for_campaign.delay(kampanya.pk)
        messages.info(
            request,
            f"{lead_sayisi} lead için mail üretimi başlatıldı. "
            "Claude AI yazdıkça mailler burada görünecek — sayfayı yenileyin.",
        )

    return redirect("campaign_detail", pk=pk)


@login_required
def campaign_launch(request, pk):
    """Onaylı e-mailleri göndermeye başlat."""
    from emails.tasks import send_approved_emails

    kampanya = get_object_or_404(Campaign, pk=pk, user=request.user)

    if request.method == "POST":
        from emails.models import GeneratedEmail

        onaylı_sayı = kampanya.emails.filter(status=GeneratedEmail.Status.APPROVED).count()

        if onaylı_sayı == 0:
            messages.error(request, "Göndermek için en az bir onaylı mail gerekli. Mailleri onaylayın.")
            return redirect("campaign_detail", pk=pk)

        kampanya.status = Campaign.Status.ACTIVE
        kampanya.save()

        send_approved_emails.delay(kampanya.pk)

        messages.success(
            request,
            f"Kampanya başlatıldı! {onaylı_sayı} mail gönderim kuyruğuna eklendi. "
            f"Günlük limit: {kampanya.daily_limit} mail.",
        )

    return redirect("campaign_detail", pk=pk)


@login_required
def campaign_pause(request, pk):
    """Aktif kampanyayı duraklat veya duraklatılmışı devam ettir."""
    kampanya = get_object_or_404(Campaign, pk=pk, user=request.user)

    if request.method == "POST":
        if kampanya.status == Campaign.Status.ACTIVE:
            kampanya.status = Campaign.Status.PAUSED
            kampanya.save()
            messages.info(request, "Kampanya duraklatıldı.")
        elif kampanya.status == Campaign.Status.PAUSED:
            from emails.tasks import send_approved_emails

            kampanya.status = Campaign.Status.ACTIVE
            kampanya.save()
            send_approved_emails.delay(kampanya.pk)
            messages.success(request, "Kampanya devam ettiriliyor.")

    return redirect("campaign_detail", pk=pk)
