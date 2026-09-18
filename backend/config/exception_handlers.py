from rest_framework.views import exception_handler as drf_exception_handler


def _first_error_detail(data):
    """Walk a DRF error payload (dict/list of ErrorDetail) and return the first leaf."""
    if isinstance(data, dict):
        for value in data.values():
            found = _first_error_detail(value)
            if found is not None:
                return found
        return None
    if isinstance(data, (list, tuple)):
        for item in data:
            found = _first_error_detail(item)
            if found is not None:
                return found
        return None
    return data


def api_exception_handler(exc, context):
    """Normalize every DRF error response to {"detail": ..., "code": ...}.

    Keeps individual views from having to shape their own error bodies and
    guarantees no stack trace / internal object ever reaches the client
    (docs/API.md "Error Format", docs/SECURITY.md error-disclosure checklist).
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    leaf = _first_error_detail(response.data)
    message = str(leaf) if leaf is not None else "خطایی رخ داد."
    code = getattr(leaf, "code", None) or "error"
    response.data = {"detail": message, "code": code}
    return response
