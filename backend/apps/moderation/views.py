from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Report
from .serializers import AdminReportSerializer
from .services import ModerationError, dismiss_report, hide_memory, resolve_report, restore_memory


class MemoryHideView(APIView):
    """POST /api/admin/memories/{id}/hide/ — admin-only moderation action.
    Not in docs/API.md (that document only specifies the participant-facing
    report endpoint); this is the minimal backend hook Phase 7 explicitly
    asks for ("hide memory")."""

    permission_classes = [IsAdminUser]

    def post(self, request, memory_id):
        try:
            hide_memory(memory_id)
        except ModerationError as exc:
            http_status = (
                status.HTTP_404_NOT_FOUND if exc.code == "not_found" else status.HTTP_400_BAD_REQUEST
            )
            return Response({"detail": exc.detail, "code": exc.code}, status=http_status)

        return Response({"detail": "خاطره پنهان شد."})


class MemoryRestoreView(APIView):
    """POST /api/admin/memories/{id}/restore/ — admin-only, the inverse of
    MemoryHideView (docs/PRODUCT.md #9 "restore content")."""

    permission_classes = [IsAdminUser]

    def post(self, request, memory_id):
        try:
            restore_memory(memory_id)
        except ModerationError as exc:
            http_status = (
                status.HTTP_404_NOT_FOUND if exc.code == "not_found" else status.HTTP_400_BAD_REQUEST
            )
            return Response({"detail": exc.detail, "code": exc.code}, status=http_status)

        return Response({"detail": "خاطره بازگردانی شد."})


class AdminReportViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/admin/reports/ — docs/API.md "Admin Moderation". Read-only
    plus the two resolution actions below; the actual content actions
    (hide/restore) live on the memory itself (MemoryHideView/
    MemoryRestoreView above), since a memory can be hidden independently of
    any report against it."""

    permission_classes = [IsAdminUser]
    serializer_class = AdminReportSerializer
    queryset = Report.objects.select_related("memory").order_by("-created_at")

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        report = self.get_object()
        resolve_report(report)
        return Response(AdminReportSerializer(report).data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request, pk=None):
        report = self.get_object()
        dismiss_report(report)
        return Response(AdminReportSerializer(report).data)
