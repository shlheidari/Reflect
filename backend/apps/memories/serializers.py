from rest_framework import serializers

from .models import Memory


class MemorySerializer(serializers.ModelSerializer):
    """Participant-facing shape for GET /api/me/memories/ — id + text only.
    `author`, `target`, `event`, timestamps and `status` never appear here
    (docs/PRIVACY.md #4, docs/API.md "Memories About Me")."""

    class Meta:
        model = Memory
        fields = ("id", "text")
        read_only_fields = fields


class MemoryReportSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
