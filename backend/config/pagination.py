from urllib.parse import urlsplit, urlunsplit

from rest_framework.pagination import PageNumberPagination


class ForwardedHostPageNumberPagination(PageNumberPagination):
    """PageNumberPagination whose next/previous links honor X-Forwarded-Host.

    nginx proxies to this backend over Liara's private network and sets a
    static `Host: reflect-backend` header (see frontend/nginx.conf) so
    ALLOWED_HOSTS never has to change when the public frontend domain does.
    But that same internal hostname otherwise leaks into these links via
    request.build_absolute_uri(), since DRF builds them from request.get_host().
    Rewriting just the host/scheme here — using X-Forwarded-Host/-Proto, which
    nginx sets to the real public request — fixes that without touching
    ALLOWED_HOSTS or Django's global host-validation behavior.
    """

    def _fix_host(self, url):
        if not url:
            return url
        forwarded_host = self.request.META.get("HTTP_X_FORWARDED_HOST")
        if not forwarded_host:
            return url
        scheme = self.request.META.get("HTTP_X_FORWARDED_PROTO") or urlsplit(url).scheme
        parts = urlsplit(url)
        return urlunsplit((scheme, forwarded_host, parts.path, parts.query, parts.fragment))

    def get_next_link(self):
        return self._fix_host(super().get_next_link())

    def get_previous_link(self):
        return self._fix_host(super().get_previous_link())
