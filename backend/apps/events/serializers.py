from rest_framework import serializers

from .models import Event


class AdminEventSerializer(serializers.ModelSerializer):
    """Admin-facing read/write shape for docs/PRODUCT.md #9 "Event"
    settings. All the configurable fields listed there are writable;
    `id`/timestamps are read-only."""

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "status",
            "start_at",
            "end_at",
            "results_enabled",
            "memories_enabled",
            "allow_rating_edit",
            "minimum_ratings_for_results",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
