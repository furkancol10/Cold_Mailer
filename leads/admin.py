from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "company", "position", "is_unsubscribed", "created_at"]
    list_filter = ["is_unsubscribed"]
    search_fields = ["first_name", "last_name", "email", "company"]
