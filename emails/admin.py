from django.contrib import admin
from .models import EmailEvent, GeneratedEmail


@admin.register(GeneratedEmail)
class GeneratedEmailAdmin(admin.ModelAdmin):
    list_display = ["campaign", "lead", "subject", "status", "sent_at", "created_at"]
    list_filter = ["status"]
    search_fields = ["lead__email", "subject", "campaign__name"]
    readonly_fields = ["tracking_id", "gmail_message_id"]


@admin.register(EmailEvent)
class EmailEventAdmin(admin.ModelAdmin):
    list_display = ["email", "event_type", "ip_address", "occurred_at"]
    list_filter = ["event_type"]
    readonly_fields = ["occurred_at"]
