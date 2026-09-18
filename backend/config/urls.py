from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.participants.urls")),
    path("api/", include("apps.ratings.urls")),
    path("api/", include("apps.events.urls")),
    path("api/", include("apps.memories.urls")),
    path("api/", include("apps.moderation.urls")),
]

# Served directly by Django rather than a CDN/object store: this app is a
# small, private, single-event tool (a few dozen-to-hundreds of avatars), not
# an internet-scale site, so the extra infra isn't justified yet. Revisit
# (e.g. S3 + signed URLs) if traffic or storage needs grow — see
# docs/DEPLOYMENT.md.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
