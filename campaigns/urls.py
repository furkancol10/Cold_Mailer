"""campaigns uygulaması URL'leri."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.campaign_list, name="campaign_list"),
    path("yeni/", views.campaign_create, name="campaign_create"),
    path("<int:pk>/", views.campaign_detail, name="campaign_detail"),
    path("<int:pk>/duzenle/", views.campaign_edit, name="campaign_edit"),
    path("<int:pk>/sil/", views.campaign_delete, name="campaign_delete"),
    path("<int:pk>/uret/", views.campaign_generate, name="campaign_generate"),
    path("<int:pk>/baslat/", views.campaign_launch, name="campaign_launch"),
    path("<int:pk>/duraklat/", views.campaign_pause, name="campaign_pause"),
]
