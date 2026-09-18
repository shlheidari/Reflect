from rest_framework.routers import DefaultRouter

from .views import AdminEventViewSet

router = DefaultRouter()
router.register("admin/events", AdminEventViewSet, basename="admin-event")

urlpatterns = router.urls
