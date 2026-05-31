from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "gmail_address", "gmail_connected", "created_at"]
    list_filter = ["gmail_connected"]
    search_fields = ["user__email", "gmail_address"]
