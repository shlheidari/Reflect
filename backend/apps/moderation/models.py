from django.db import models


class Report(models.Model):
    """A participant's report of a Memory, for moderation review
    (docs/DATABASE.md #7).

    Distinct from `Memory.status`: a Report records the reporter's complaint
    and its own resolution lifecycle; `Memory.status` records what's
    actually shown to participants. Filing a report flags the memory
    (status -> REPORTED) but does not hide it — only an explicit hide
    action (an admin moderation decision, docs/PRODUCT.md #9) removes a
    memory from anonymous retrieval. This keeps a single bad-faith report
    from unilaterally censoring someone.
    """

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        RESOLVED = "RESOLVED", "Resolved"
        DISMISSED = "DISMISSED", "Dismissed"

    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(
        "participants.Participant", on_delete=models.CASCADE, related_name="reports_filed"
    )
    memory = models.ForeignKey("memories.Memory", on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reporter", "memory"], name="unique_report_per_reporter_memory"
            ),
        ]
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["status"]),
            models.Index(fields=["memory"]),
        ]

    def __str__(self):
        return f"report #{self.pk} on memory #{self.memory_id}"
