from rest_framework import serializers

from apps.memories.models import Memory

from .models import Report


class ReportMemorySerializer(serializers.ModelSerializer):
    """The reported memory, nested inside AdminReportSerializer. `author` is
    deliberately excluded (docs/PRIVACY.md #11)."""

    class Meta:
        model = Memory
        fields = ("id", "text", "status")
        read_only_fields = fields


class AdminReportSerializer(serializers.ModelSerializer):
    """Admin-facing report shape (docs/API.md "Admin Moderation").
    Deliberately omits `reporter` as well as the memory's `author` — even
    for admins, docs/PRIVACY.md #11 says the interface "should not casually
    expose evaluator identities"; moderating means judging the reported
    content, not identifying who wrote or reported it."""

    memory = ReportMemorySerializer(read_only=True)

    class Meta:
        model = Report
        fields = ("id", "memory", "reason", "status", "created_at", "resolved_at")
        read_only_fields = fields
