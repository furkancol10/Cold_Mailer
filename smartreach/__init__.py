# Django başlarken Celery uygulamasını yükle
from .celery import app as celery_app

__all__ = ("celery_app",)
