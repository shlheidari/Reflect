from django.contrib import admin

from .models import Rating, RatingCategory


@admin.register(RatingCategory)
class RatingCategoryAdmin(admin.ModelAdmin):
    list_display = ("left_label", "right_label", "event", "order", "required", "active")
    list_filter = ("event", "active", "required")
    search_fields = ("key", "left_label", "right_label")
    autocomplete_fields = ("event",)
    ordering = ("event", "order", "id")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Internal/staff-only inspection, not a moderation tool. Deliberately
    keeps `evaluator` out of list_display/search — visible only if a staff
    member opens one row's detail page (docs/PRIVACY.md #11: don't casually
    surface evaluator identity)."""

    list_display = ("id", "event", "target", "category", "score", "created_at")
    list_filter = ("event", "category")
    search_fields = ("target__display_name",)
    autocomplete_fields = ("event", "evaluator", "target", "category")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
