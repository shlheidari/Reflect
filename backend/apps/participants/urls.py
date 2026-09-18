from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AdminParticipantViewSet, ParticipantListView

router = DefaultRouter()
router.register("admin/participants", AdminParticipantViewSet, basename="admin-participant")

urlpatterns = [
    path("participants/", ParticipantListView.as_view(), name="participant-list"),
] + router.urls
