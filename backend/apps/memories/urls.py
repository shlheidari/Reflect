from django.urls import path

from .views import MemoryReportView, MyMemoriesView

urlpatterns = [
    path("me/memories/", MyMemoriesView.as_view(), name="my-memories"),
    path("memories/<int:memory_id>/report/", MemoryReportView.as_view(), name="memory-report"),
]
