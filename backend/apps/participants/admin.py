from django.contrib import admin

from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "event", "is_active", "created_at")
    list_filter = ("event", "is_active")
    search_fields = ("display_name", "user__username")
    autocomplete_fields = ("user", "event")
