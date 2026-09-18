from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers

from apps.events.models import Event

from .models import Participant

User = get_user_model()


class ParticipantPublicSerializer(serializers.ModelSerializer):
    """/api/participants/ — what one participant may see about another.

    Deliberately excludes `user` entirely: only `id` (the Participant row,
    used as `target_id` for rating submission) and display-safe fields.
    Never expose the underlying account/user identifier here.

    `rating_count`/`rated_by_me` are annotated onto the queryset in
    ParticipantListView (distinct-evaluator count and an Exists subquery) —
    this only declares their shape, it never touches apps.ratings directly.
    """

    rating_count = serializers.IntegerField(read_only=True)
    rated_by_me = serializers.BooleanField(read_only=True)

    class Meta:
        model = Participant
        fields = ("id", "display_name", "avatar", "rating_count", "rated_by_me")


class ParticipantSelfSerializer(serializers.ModelSerializer):
    """The authenticated user's own participant profile, embedded in /api/me/."""

    class Meta:
        model = Participant
        fields = ("id", "display_name", "avatar", "event", "is_active")
        read_only_fields = fields


class AdminParticipantSerializer(serializers.ModelSerializer):
    """Admin-facing read/update shape. `username` is read-only here — changing
    login credentials goes through the dedicated reset-password action, never
    through a generic field update.

    `ratings_given_count`/`ratings_received_count` are annotated onto the
    queryset in AdminParticipantViewSet.get_queryset (distinct-target and
    distinct-evaluator counts) — this only declares their shape. Falls back
    to 0 via getattr for instances not built from that queryset (e.g. a
    freshly created Participant in the create() response), same pattern as
    ParticipantPublicSerializer's annotated fields.

    docs/PRODUCT.md #9 "view participation status": plain counts and
    last-login, never which specific ratings/memories or who evaluated whom
    (docs/PRIVACY.md #11 — the admin interface should not casually expose
    evaluator identities either).
    """

    username = serializers.CharField(source="user.username", read_only=True)
    last_login = serializers.DateTimeField(source="user.last_login", read_only=True)
    ratings_given_count = serializers.SerializerMethodField()
    ratings_received_count = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = (
            "id",
            "username",
            "display_name",
            "avatar",
            "event",
            "is_active",
            "last_login",
            "ratings_given_count",
            "ratings_received_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "username",
            "last_login",
            "ratings_given_count",
            "ratings_received_count",
            "created_at",
            "updated_at",
        )

    def get_ratings_given_count(self, obj):
        return getattr(obj, "ratings_given_count", 0)

    def get_ratings_received_count(self, obj):
        return getattr(obj, "ratings_received_count", 0)


class AdminParticipantCreateSerializer(serializers.Serializer):
    """Admin creates a participant: this creates the backing User account too,
    since participants have no self-registration flow (docs/PRODUCT.md §1)."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, min_length=8)
    display_name = serializers.CharField(max_length=150)
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    avatar = serializers.ImageField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً استفاده شده است.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password", None)

        self.generated_password = None
        if not password:
            password = get_random_string(12)
            self.generated_password = password

        with transaction.atomic():
            user = User.objects.create_user(username=username, password=password)
            participant = Participant.objects.create(user=user, **validated_data)

        return participant


class AdminPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=False, allow_blank=False, min_length=8, write_only=True
    )
