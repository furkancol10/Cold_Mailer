"""
Kullanıcı kaydedildiğinde otomatik olarak UserProfile oluşturur.
Google OAuth2 ile giriş yapıldığında da tetiklenir.
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def profil_olustur(sender, instance, created, **kwargs):
    """Yeni kullanıcı oluşturulduğunda profil yarat."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
