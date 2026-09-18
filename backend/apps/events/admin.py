from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "start_at", "end_at", "created_at")
    list_filter = ("status",)
    search_fields = ("name",)
