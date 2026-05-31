"""emails uygulaması URL'leri."""

from django.urls import path

from . import views

urlpatterns = [
    # Mail yönetimi (giriş gerektirir)
    path("<int:pk>/onayla/", views.email_approve, name="email_approve"),
    path("<int:pk>/atla/", views.email_skip, name="email_skip"),
    path("<int:pk>/duzenle/", views.email_edit, name="email_edit"),
    path("kampanya/<int:campaign_pk>/hepsini-onayla/", views.email_approve_all, name="email_approve_all"),

    # Herkese açık tracking URL'leri (giriş gerekmez)
    path("t/<uuid:tracking_id>/", views.tracking_pixel, name="tracking_pixel"),
    path("unsub/<uuid:tracking_id>/", views.unsubscribe, name="unsubscribe"),
]
