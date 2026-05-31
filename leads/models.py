"""
Lead (müşteri adayı) modeli.
CSV'den yüklenen veya elle eklenen potansiyel müşteri bilgileri.
"""

from django.db import models
from django.contrib.auth.models import User


class Lead(models.Model):
    """Tek bir müşteri adayını temsil eder."""

    # Her lead bir kullanıcıya ait — başka kullanıcılar göremez
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads")

    # Temel iletişim bilgileri
    first_name = models.CharField("Ad", max_length=100)
    last_name = models.CharField("Soyad", max_length=100, blank=True)
    email = models.EmailField("E-posta")
    company = models.CharField("Şirket", max_length=200, blank=True)
    position = models.CharField("Pozisyon", max_length=200, blank=True)

    # AI'a verilecek ek bağlam
    notes = models.TextField("Notlar", blank=True)

    # Bu lead'e daha önce mail gönderildi mi?
    is_unsubscribed = models.BooleanField("Abonelikten çıktı", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Lead'ler"
        # Aynı kullanıcı aynı e-postayı iki kez ekleyemesin
        unique_together = ("user", "email")
        ordering = ["-created_at"]
