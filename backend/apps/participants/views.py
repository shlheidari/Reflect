from django.db.models import Count, Exists, OuterRef
from django.utils.crypto import get_random_string
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.ratings.models import Rating

from .models import Participant
from .permissions import IsActiveParticipant
from .serializers import (
    AdminParticipantCreateSerializer,
    AdminParticipantSerializer,
    AdminPasswordResetSerializer,
    ParticipantPublicSerializer,
)


class ParticipantListView(generics.ListAPIView):
    """GET /api/participants/ — other active participants in my own event.

    Ordered by id (creation order) rather than SQL RANDOM(): docs/PRODUCT.md
    §8 asks for a neutral/randomized order so rating counts don't read as a
    leaderboard, but true per-request randomization would reshuffle entries
    across pages, causing skips/repeats under pagination. Creation order is
    neutral (it doesn't rank by popularity) and pagination-safe.
    """

    serializer_class = ParticipantPublicSerializer
    permission_classes = [IsAuthenticated, IsActiveParticipant]

    def get_queryset(self):
        me = self.request.user.participant
        return (
            Participant.objects.filter(event=me.event, is_active=True)
            .exclude(pk=me.pk)
            .annotate(
                rating_count=Count("ratings_received__evaluator", distinct=True),
                rated_by_me=Exists(Rating.objects.filter(target=OuterRef("pk"), evaluator=me)),
            )
            .order_by("id")
        )


class AdminParticipantViewSet(viewsets.ModelViewSet):
    """Admin-only participant management. No hard delete: docs/DATABASE.md
    #10 prefers soft deactivation, so `is_active` is a plain patchable field
    and there is no destroy route (also covers reactivate: PATCH is_active
    back to true)."""

    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return (
            Participant.objects.select_related("user", "event")
            .annotate(
                ratings_given_count=Count("ratings_given__target", distinct=True),
                ratings_received_count=Count("ratings_received__evaluator", distinct=True),
            )
            .order_by("id")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return AdminParticipantCreateSerializer
        return AdminParticipantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant = serializer.save()

        output = AdminParticipantSerializer(participant, context=self.get_serializer_context()).data
        if serializer.generated_password:
            output["generated_password"] = serializer.generated_password
        return Response(output, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        participant = self.get_object()
        serializer = AdminPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data.get("new_password")
        generated = new_password is None
        if generated:
            new_password = get_random_string(12)

        participant.user.set_password(new_password)
        participant.user.save(update_fields=["password"])

        response = {"detail": "رمز عبور بازنشانی شد."}
        if generated:
            response["generated_password"] = new_password
        return Response(response)
