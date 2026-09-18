from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Event
from .serializers import AdminEventSerializer
from .services import get_admin_statistics


class AdminEventViewSet(viewsets.ModelViewSet):
    """Admin-only event management (docs/PRODUCT.md #9 "Event",
    docs/ROADMAP.md Phase 8). No hard delete — events are never destroyed
    through the API, same soft-management posture as
    AdminParticipantViewSet/AdminRatingCategoryViewSet. Unpaginated: like
    rating categories, the event set is small by design.

    `GET /api/admin/events/` also continues to serve the admin rating-
    category page's event picker (Phase 4) — additive change only, the
    fields it reads (`id`, `name`, `status`) are unchanged, just no longer
    the only ones returned."""

    permission_classes = [IsAdminUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    serializer_class = AdminEventSerializer
    pagination_class = None
    queryset = Event.objects.all().order_by("id")

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """GET /api/admin/events/{id}/statistics/ — docs/API.md specifies a
        flat `/api/admin/statistics/`, but the data model supports more than
        one Event (docs/DATABASE.md), so statistics are scoped per event via
        the URL instead of an ambiguous implicit "current event"."""

        event = self.get_object()
        return Response(get_admin_statistics(event))
