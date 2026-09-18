from rest_framework import serializers

from .models import RatingCategory


class RatingCategoryPublicSerializer(serializers.ModelSerializer):
    """Participant-facing shape for GET /api/rating-categories/ — no
    event/active/timestamps, nothing an evaluator wouldn't need to render
    the rating form (docs/API.md)."""

    class Meta:
        model = RatingCategory
        fields = ("id", "key", "left_label", "right_label", "description", "order", "required")
        read_only_fields = fields


class AdminRatingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingCategory
        fields = (
            "id",
            "event",
            "key",
            "left_label",
            "right_label",
            "description",
            "order",
            "required",
            "active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        event = attrs.get("event", getattr(self.instance, "event", None))
        key = attrs.get("key", getattr(self.instance, "key", None))

        if event is not None and key:
            duplicates = RatingCategory.objects.filter(event=event, key=key)
            if self.instance is not None:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise serializers.ValidationError(
                    {"key": "این کلید قبلاً برای این رویداد استفاده شده است."}
                )

        return attrs


class RatingCategoryReorderSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def validate_ids(self, value):
        if len(set(value)) != len(value):
            raise serializers.ValidationError("شناسه‌های تکراری مجاز نیستند.")
        return value


class RatingItemSerializer(serializers.Serializer):
    """One category score within a rating submission. `score` rejects
    negatives, values above 10, non-integers and null at the field level
    (docs/RATING_SYSTEM.md #5)."""

    category_id = serializers.IntegerField()
    score = serializers.IntegerField(min_value=0, max_value=10)


class RatingSubmitSerializer(serializers.Serializer):
    target_id = serializers.IntegerField()
    ratings = RatingItemSerializer(many=True, allow_empty=False)
    # Optional anonymous memory/story about the target (docs/PRODUCT.md #5,
    # #7). Max length matches apps.memories.models.Memory.text.
    memory = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")


class RatingUpdateSerializer(serializers.Serializer):
    ratings = RatingItemSerializer(many=True, allow_empty=False)
