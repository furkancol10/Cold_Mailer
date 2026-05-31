"""
Kampanya modeli.
Bir kullanıcının oluşturduğu e-mail gönderim kampanyası.
"""

from django.db import models
from django.contrib.auth.models import User
from leads.models import Lead


class Campaign(models.Model):
    """E-mail kampanyasının tüm ayarlarını barındırır."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Taslak"
        ACTIVE = "active", "Aktif"
        PAUSED = "paused", "Duraklatıldı"
        COMPLETED = "completed", "Tamamlandı"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField("Kampanya Adı", max_length=200)
    description = models.TextField("Açıklama", blank=True)

    # Kampanyaya eklenmiş lead'ler (çok-a-çok ilişki)
    leads = models.ManyToManyField(Lead, blank=True, related_name="campaigns")

    # AI'a verilecek hizmet açıklaması
    service_description = models.TextField("Hizmet Açıklaması")

    # AI prompt şablonu — {lead.first_name}, {lead.company} gibi yer tutucular kullanılır
    prompt_template = models.TextField(
        "Prompt Şablonu",
        default=(
            "{lead.first_name} için kişisel bir cold e-mail yaz.\n"
            "Şirket: {lead.company}\n"
            "Pozisyon: {lead.position}\n"
            "Notlar: {lead.notes}\n\n"
            "Benim hizmetim: {service_description}\n"
            "Ton: Profesyonel ama samimi\n"
            "Uzunluk: 80-120 kelime"
        ),
    )

    status = models.CharField(
        "Durum", max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    # Gönderim zamanlaması
    scheduled_at = models.DateTimeField("Zamanlanmış Gönderim", blank=True, null=True)
    daily_limit = models.PositiveIntegerField("Günlük Gönderim Limiti", default=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Kampanya"
        verbose_name_plural = "Kampanyalar"
        ordering = ["-created_at"]
