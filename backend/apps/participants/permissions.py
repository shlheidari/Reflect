from rest_framework.permissions import BasePermission


class IsActiveParticipant(BasePermission):
    """Gate participant-facing endpoints to users with an active Participant
    profile. Blocks staff-only accounts (no participant row) and deactivated
    participants alike — docs/ROADMAP.md Phase 3 item 8."""

    message = "این حساب شرکت‌کننده فعال نیست."

    def has_permission(self, request, view):
        participant = getattr(request.user, "participant", None)
        return participant is not None and participant.is_active
