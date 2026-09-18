from django.db import transaction
from django.utils import timezone

from apps.memories.models import Memory

from .models import Report


class ModerationError(Exception):
    """Raised by the functions below; views translate this into the
    project's standard {"detail", "code"} error response (same pattern as
    apps.ratings.services.RatingSubmissionError)."""

    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(detail)


@transaction.atomic
def report_memory(*, reporter, memory_id, reason=""):
    """Record a participant's report of a memory (docs/API.md "Report
    Memory"). Scoped to memories about the reporter themselves — the only
    memories a participant ever sees are the ones on their own "memories
    about me" page (apps.memories.services.get_memories_about_me), so
    scoping to `target=reporter` matches the real UI surface and closes an
    IDOR/enumeration hole: without it, any participant could file a report
    against (and thereby flip the status of) any memory in their event
    just by guessing a numeric ID, and use the 201-vs-404 response to probe
    which memory IDs exist — never trust an ID coming from the frontend,
    docs/PRIVACY.md #6. A single `not_found` covers both "no such memory"
    and "exists but isn't about you" so the response never distinguishes
    the two (same pattern as apps.ratings.services._validate_target's
    `invalid_target`). Flags the memory REPORTED for admin attention
    without hiding it — see apps.moderation.models.Report's docstring for
    why."""

    try:
        memory = Memory.objects.get(pk=memory_id, event=reporter.event, target=reporter)
    except Memory.DoesNotExist:
        raise ModerationError("not_found", "خاطره مورد نظر یافت نشد.")

    if Report.objects.filter(reporter=reporter, memory=memory).exists():
        raise ModerationError("already_reported", "شما قبلاً این خاطره را گزارش کرده‌اید.")

    Report.objects.create(event=memory.event, reporter=reporter, memory=memory, reason=reason)

    if memory.status == Memory.Status.VISIBLE:
        memory.status = Memory.Status.REPORTED
        memory.save(update_fields=["status", "updated_at"])


def hide_memory(memory_id):
    """Admin moderation action: hide a memory from anonymous retrieval.
    This is the minimal backend hook docs/ROADMAP.md's Phase 7 explicitly
    asks for ("hide memory"); the full moderation dashboard (report
    listing, restore, dismiss) is Phase 8."""

    try:
        memory = Memory.objects.get(pk=memory_id)
    except Memory.DoesNotExist:
        raise ModerationError("not_found", "خاطره مورد نظر یافت نشد.")

    memory.status = Memory.Status.HIDDEN
    memory.save(update_fields=["status", "updated_at"])
    return memory


def restore_memory(memory_id):
    """Admin moderation action: the inverse of hide_memory — makes a memory
    visible again regardless of its prior status (docs/PRODUCT.md #9
    "restore content")."""

    try:
        memory = Memory.objects.get(pk=memory_id)
    except Memory.DoesNotExist:
        raise ModerationError("not_found", "خاطره مورد نظر یافت نشد.")

    memory.status = Memory.Status.VISIBLE
    memory.save(update_fields=["status", "updated_at"])
    return memory


def resolve_report(report):
    """Mark a report as resolved. Independent of the memory's own status —
    an admin may resolve a report without hiding the memory (e.g. after
    reviewing it and deciding it's fine), or vice versa."""

    report.status = Report.Status.RESOLVED
    report.resolved_at = timezone.now()
    report.save(update_fields=["status", "resolved_at"])
    return report


def dismiss_report(report):
    """Mark a report as dismissed (reviewed, no action warranted)."""

    report.status = Report.Status.DISMISSED
    report.resolved_at = timezone.now()
    report.save(update_fields=["status", "resolved_at"])
    return report
