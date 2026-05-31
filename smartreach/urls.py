"""SmartReach ana URL yönlendirmeleri."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),   # Google giriş
    path("", include("accounts.urls")),            # Ana sayfa, dashboard
    path("leads/", include("leads.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("emails/", include("emails.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
