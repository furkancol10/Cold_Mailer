"""
E-mail ve takip modelleri.
GeneratedEmail: AI tarafından üretilmiş, gönderilmeyi bekleyen mailler.
EmailEvent: Açılma, tıklama, cevap gibi olaylar.
"""

import uuid
from django.db import models
from leads.models import Lead
from campaigns.models import Campaign


class GeneratedEmail(models.Model):
    """AI tarafından üretilmiş tek bir e-mail."""

    class Status(models.TextChoices):
        PENDING = "pending", "Bekliyor"       # Üretildi, onay bekleniyor
        APPROVED = "approved", "Onaylandı"    # Kullanıcı onayladı, gönderilecek
        SENT = "sent", "Gönderildi"
        OPENED = "opened", "Açıldı"
        REPLIED = "replied", "Cevaplandı"
        FAILED = "failed", "Başarısız"
        SKIPPED = "skipped", "Atlandı"        # Kullanıcı bu lead'i atladı

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="emails"
    )
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name="generated_emails"
    )

    subject = models.CharField("Konu", max_length=300)
    body = models.TextField("İçerik")

    status = models.CharField(
        "Durum", max_length=20, choices=Status.choices, default=Status.PENDING
    )

    # Tracking için benzersiz ID — URL'de kullanılır
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Gmail'in döndürdüğü mesaj ID'si (cevap takibi için)
    gmail_message_id = models.CharField(max_length=200, blank=True, null=True)

    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.campaign.name} → {self.lead.email} [{self.get_status_display()}]"

    class Meta:
        verbose_name = "Üretilmiş E-mail"
        verbose_name_plural = "Üretilmiş E-mailler"
        ordering = ["-created_at"]


class EmailEvent(models.Model):
    """Bir e-mail üzerinde gerçekleşen her olayı kaydeder."""

    class EventType(models.TextChoices):
        OPEN = "open", "Açıldı"
        CLICK = "click", "Tıklandı"
        REPLY = "reply", "Cevaplandı"
        BOUNCE = "bounce", "Geri döndü"
        UNSUBSCRIBE = "unsubscribe", "Abonelikten çıktı"

    email = models.ForeignKey(
        GeneratedEmail, on_delete=models.CASCADE, related_name="events"
    )
    event_type = models.CharField(
        "Olay Tipi", max_length=20, choices=EventType.choices
    )

    # Tıklanan URL (click olayları için)
    clicked_url = models.URLField(blank=True, null=True)

    # İstek bilgileri (analiz için)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    occurred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} — {self.get_event_type_display()}"

    class Meta:
        verbose_name = "E-mail Olayı"
        verbose_name_plural = "E-mail Olayları"
        ordering = ["-occurred_at"]
