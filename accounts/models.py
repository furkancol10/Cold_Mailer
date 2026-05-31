"""
Kullanıcı profil modeli.
Django'nun varsayılan User modeline Gmail token bilgilerini ekler.
"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Her kullanıcıya ait ek bilgiler (1-1 ilişki)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Gmail API erişim tokenları
    gmail_access_token = models.TextField(blank=True, null=True)
    gmail_refresh_token = models.TextField(blank=True, null=True)
    gmail_token_expiry = models.DateTimeField(blank=True, null=True)

    gmail_address = models.EmailField(blank=True, null=True)
    gmail_connected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} profili"

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"
