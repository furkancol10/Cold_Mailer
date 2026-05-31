"""
python manage.py setup_oauth
Site ve Google OAuth2 SocialApp'i otomatik yapılandırır.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Site ve Google OAuth2 SocialApp'i yapılandırır"

    def handle(self, *args, **options):
        from django.conf import settings
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        # Site'i localhost olarak güncelle
        site, _ = Site.objects.get_or_create(id=1)
        site.domain = "localhost:8000"
        site.name = "SmartReach Dev"
        site.save()
        self.stdout.write(f"[OK] Site: {site.domain}")

        # Google credentials'ı settings'ten al
        google = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]

        # Duplicate kayıtları temizle, tek kayıt bırak
        SocialApp.objects.filter(provider="google").delete()
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id=google["client_id"],
            secret=google["secret"],
        )
        app.sites.add(site)

        self.stdout.write("[OK] Google SocialApp olusturuldu (eskiler silindi)")
        self.stdout.write(self.style.SUCCESS("Hazir! http://localhost:8000 adresine gidebilirsin."))
