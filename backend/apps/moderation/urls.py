from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AdminReportViewSet, MemoryHideView, MemoryRestoreView

router = DefaultRouter()
router.register("admin/reports", AdminReportViewSet, basename="admin-report")

urlpatterns = [
    path("admin/memories/<int:memory_id>/hide/", MemoryHideView.as_view(), name="admin-memory-hide"),
    path(
        "admin/memories/<int:memory_id>/restore/",
        MemoryRestoreView.as_view(),
        name="admin-memory-restore",
    ),
] + router.urls
