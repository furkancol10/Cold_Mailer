"""leads uygulaması URL'leri."""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.lead_list, name="lead_list"),
    path("ekle/", views.lead_create, name="lead_create"),
    path("<int:pk>/duzenle/", views.lead_edit, name="lead_edit"),
    path("<int:pk>/sil/", views.lead_delete, name="lead_delete"),
    path("csv-yukle/", views.csv_upload, name="csv_upload"),
]
