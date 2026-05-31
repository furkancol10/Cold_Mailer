"""
Celery uygulama yapılandırması.
Görev kuyruğu bu dosya üzerinden başlatılır.
"""

import os
from celery import Celery

# Django settings modülünü Celery'e bildir
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartreach.settings")

app = Celery("smartreach")

# settings.py içindeki CELERY_ ile başlayan değişkenleri kullan
app.config_from_object("django.conf:settings", namespace="CELERY")

# Tüm app klasörlerindeki tasks.py dosyalarını otomatik bul
app.autodiscover_tasks()
