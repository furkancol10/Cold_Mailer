from django.contrib import admin
from .models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "status", "daily_limit", "lead_count", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "user__email"]

    def lead_count(self, obj):
        return obj.leads.count()
    lead_count.short_description = "Lead Sayısı"
