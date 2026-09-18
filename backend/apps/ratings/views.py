from django.db import transaction
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.participants.permissions import IsActiveParticipant

from .models import RatingCategory
from .serializers import (
    AdminRatingCategorySerializer,
    RatingCategoryPublicSerializer,
    RatingCategoryReorderSerializer,
    RatingSubmitSerializer,
    RatingUpdateSerializer,
)
from .services import RatingSubmissionError, get_my_results, submit_ratings, update_ratings


class RatingCategoryListView(generics.ListAPIView):
    """GET /api/rating-categories/ — active categories for the current
    participant's event, in display order. Unpaginated: docs/API.md's
    pagination list omits this endpoint, and the rating form (Phase 5) needs
    the whole active set at once to render."""

    serializer_class = RatingCategoryPublicSerializer
    permission_classes = [IsActiveParticipant]
    pagination_class = None

    def get_queryset(self):
        me = self.request.user.participant
        return RatingCategory.objects.filter(event=me.event, active=True).order_by("order", "id")


class AdminRatingCategoryViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for rating categories. No hard delete — deactivate via
    `active` instead (docs/PRODUCT.md #9 only lists create/edit/disable/
    reorder for admin categories), same soft-deletion posture as
    AdminParticipantViewSet.

    Unpaginated on purpose: category sets are small by design (docs/
    RATING_SYSTEM.md ships ~25) and `reorder` below needs the complete,
    per-event set in one response to work at all."""

    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    serializer_class = AdminRatingCategorySerializer
    pagination_class = None
    queryset = RatingCategory.objects.select_related("event").order_by("event", "order", "id")

    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        serializer = RatingCategoryReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data["ids"]

        categories = list(RatingCategory.objects.filter(pk__in=ids))
        if len(categories) != len(ids):
            return Response(
                {"detail": "برخی شناسه‌ها معتبر نیستند.", "code": "invalid_ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        events = {category.event_id for category in categories}
        if len(events) > 1:
            return Response(
                {"detail": "همه دسته‌ها باید متعلق به یک رویداد باشند.", "code": "mixed_events"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_id = events.pop()
        existing_ids = set(
            RatingCategory.objects.filter(event_id=event_id).values_list("id", flat=True)
        )
        if set(ids) != existing_ids:
            return Response(
                {
                    "detail": "برای مرتب‌سازی باید تمام دسته‌های این رویداد ارسال شوند.",
                    "code": "incomplete_order",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for index, category_id in enumerate(ids):
                RatingCategory.objects.filter(pk=category_id).update(order=index)

        updated = RatingCategory.objects.filter(event_id=event_id).order_by("order", "id")
        return Response(AdminRatingCategorySerializer(updated, many=True).data)


class RatingSubmitView(APIView):
    """POST /api/ratings/ — a participant's first rating of a target across
    one or more categories, created atomically. The response never contains
    evaluator information (docs/PRIVACY.md, docs/SECURITY.md)."""

    permission_classes = [IsActiveParticipant]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "rating_submit"

    def post(self, request):
        serializer = RatingSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            ratings = submit_ratings(
                evaluator=request.user.participant,
                target_id=data["target_id"],
                items=data["ratings"],
                memory_text=data.get("memory", ""),
            )
        except RatingSubmissionError as exc:
            return Response(
                {"detail": exc.detail, "code": exc.code}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "نظر شما با موفقیت ثبت شد.", "created": len(ratings)},
            status=status.HTTP_201_CREATED,
        )


class RatingUpdateView(APIView):
    """PATCH/PUT /api/ratings/{target_id}/ — edit the requesting participant's
    own previous ratings for that target. Only reachable when the event's
    `allow_rating_edit` flag is on (docs/API.md "Update Rating")."""

    permission_classes = [IsActiveParticipant]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "rating_submit"

    def _update(self, request, target_id):
        serializer = RatingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data["ratings"]

        try:
            ratings = update_ratings(
                evaluator=request.user.participant,
                target_id=target_id,
                items=items,
            )
        except RatingSubmissionError as exc:
            http_status = (
                status.HTTP_404_NOT_FOUND
                if exc.code == "not_found"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response({"detail": exc.detail, "code": exc.code}, status=http_status)

        return Response({"detail": "نظر شما به‌روزرسانی شد.", "updated": len(ratings)})

    def patch(self, request, target_id):
        return self._update(request, target_id)

    def put(self, request, target_id):
        return self._update(request, target_id)


class MyResultsView(APIView):
    """GET /api/me/results/ — anonymous aggregate results for the
    authenticated participant. Response shape and privacy guarantees are
    entirely owned by services.get_my_results (docs/PRIVACY.md, docs/API.md
    "My Results")."""

    permission_classes = [IsActiveParticipant]

    def get(self, request):
        return Response(get_my_results(request.user.participant))
