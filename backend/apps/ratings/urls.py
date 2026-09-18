from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminRatingCategoryViewSet,
    MyResultsView,
    RatingCategoryListView,
    RatingSubmitView,
    RatingUpdateView,
)

router = DefaultRouter()
router.register("admin/rating-categories", AdminRatingCategoryViewSet, basename="admin-rating-category")

urlpatterns = [
    path("rating-categories/", RatingCategoryListView.as_view(), name="rating-category-list"),
    path("ratings/", RatingSubmitView.as_view(), name="rating-submit"),
    path("ratings/<int:target_id>/", RatingUpdateView.as_view(), name="rating-update"),
    path("me/results/", MyResultsView.as_view(), name="my-results"),
] + router.urls
