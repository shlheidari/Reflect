from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.moderation.services import ModerationError, report_memory
from apps.participants.permissions import IsActiveParticipant

from .serializers import MemoryReportSerializer, MemorySerializer
from .services import get_memories_about_me


class MyMemoriesView(generics.ListAPIView):
    """GET /api/me/memories/ — anonymous memories about the authenticated
    participant, newest first. Paginated in the same standard DRF shape
    already used by /api/participants/ (docs/API.md's inline example omits
    the pagination wrapper, same as that endpoint's example did; docs/API.md
    "Pagination" explicitly lists memories as needing it)."""

    serializer_class = MemorySerializer
    permission_classes = [IsActiveParticipant]

    def get_queryset(self):
        return get_memories_about_me(self.request.user.participant)


class MemoryReportView(APIView):
    """POST /api/memories/{id}/report/ — flag a memory for moderation
    review. Response and privacy guarantees are entirely owned by
    apps.moderation.services.report_memory (docs/API.md "Report Memory")."""

    permission_classes = [IsActiveParticipant]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "memory_report"

    def post(self, request, memory_id):
        serializer = MemoryReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            report_memory(
                reporter=request.user.participant,
                memory_id=memory_id,
                reason=serializer.validated_data.get("reason", ""),
            )
        except ModerationError as exc:
            http_status = (
                status.HTTP_404_NOT_FOUND if exc.code == "not_found" else status.HTTP_400_BAD_REQUEST
            )
            return Response({"detail": exc.detail, "code": exc.code}, status=http_status)

        return Response({"detail": "گزارش شما ثبت شد."}, status=status.HTTP_201_CREATED)
