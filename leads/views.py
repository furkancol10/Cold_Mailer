"""Lead yönetimi view'ları: liste, ekleme, düzenleme, silme, CSV yükleme."""

import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CSVUploadForm, LeadForm
from .models import Lead


@login_required
def lead_list(request):
    """Lead listesi — arama destekli."""
    leads = Lead.objects.filter(user=request.user)

    # URL'de ?q=... varsa ada, soyada, e-postaya veya şirkete göre filtrele
    from django.db.models import Q
    query = request.GET.get("q", "").strip()
    if query:
        leads = leads.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(company__icontains=query)
        )

    context = {
        "leads": leads,
        "query": query,
        "total": leads.count(),
    }
    return render(request, "leads/lead_list.html", context)


@login_required
def lead_create(request):
    """Yeni lead ekleme formu."""
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.user = request.user      # lead'i giriş yapan kullanıcıya bağla
            try:
                lead.save()
                messages.success(request, f"{lead.full_name} başarıyla eklendi.")
                return redirect("lead_list")
            except IntegrityError:
                messages.error(request, "Bu e-posta adresi zaten kayıtlı.")
    else:
        form = LeadForm()

    return render(request, "leads/lead_form.html", {"form": form, "title": "Yeni Lead Ekle"})


@login_required
def lead_edit(request, pk):
    """Mevcut lead'i düzenleme formu."""
    # get_object_or_404: lead bulunamazsa 404 sayfası göster
    lead = get_object_or_404(Lead, pk=pk, user=request.user)

    if request.method == "POST":
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f"{lead.full_name} güncellendi.")
            return redirect("lead_list")
    else:
        form = LeadForm(instance=lead)

    return render(request, "leads/lead_form.html", {"form": form, "title": "Lead Düzenle", "lead": lead})


@login_required
def lead_delete(request, pk):
    """Lead silme — POST ile çalışır (GET ile çalışmaz, güvenlik)."""
    lead = get_object_or_404(Lead, pk=pk, user=request.user)

    if request.method == "POST":
        isim = lead.full_name
        lead.delete()
        messages.success(request, f"{isim} silindi.")
        return redirect("lead_list")

    # GET isteğinde onay sayfası göster
    return render(request, "leads/lead_confirm_delete.html", {"lead": lead})


@login_required
def csv_upload(request):
    """CSV dosyasından toplu lead yükleme."""
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_dosya = request.FILES["csv_file"]

            # Dosyayı metin olarak oku (encoding hatalarını yoksay)
            icerik = csv_dosya.read().decode("utf-8", errors="ignore")
            okuyucu = csv.DictReader(io.StringIO(icerik))

            eklenen = 0
            atlanan = 0
            hatalar = []

            for satir_no, satir in enumerate(okuyucu, start=2):
                email = satir.get("email", "").strip()

                if not email:
                    hatalar.append(f"Satır {satir_no}: e-posta boş, atlandı.")
                    atlanan += 1
                    continue

                try:
                    Lead.objects.get_or_create(
                        user=request.user,
                        email=email,
                        defaults={
                            "first_name": satir.get("first_name", "").strip(),
                            "last_name": satir.get("last_name", "").strip(),
                            "company": satir.get("company", "").strip(),
                            "position": satir.get("position", "").strip(),
                            "notes": satir.get("notes", "").strip(),
                        },
                    )
                    eklenen += 1
                except Exception as e:
                    hatalar.append(f"Satır {satir_no} ({email}): {e}")
                    atlanan += 1

            messages.success(request, f"{eklenen} lead eklendi, {atlanan} satır atlandı.")

            # Hata varsa kullanıcıya göster
            for hata in hatalar[:5]:   # en fazla 5 hata göster
                messages.warning(request, hata)

            return redirect("lead_list")
    else:
        form = CSVUploadForm()

    return render(request, "leads/csv_upload.html", {"form": form})
