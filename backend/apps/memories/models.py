from django.db import models


class Memory(models.Model):
    """An anonymous memory/story an evaluator writes about a target while
    rating them (docs/PRODUCT.md #5, #7; docs/DATABASE.md #6).

    `text` merges the "memory/story" and "additional comment" concepts from
    docs/PRODUCT.md #4 into one field, per docs/DATABASE.md #8's explicit
    MVP guidance ("Memory can contain both story and comment content unless
    the UX needs separate fields").

    Privacy-critical: `author` must never appear in a participant-facing
    serializer/response (docs/PRIVACY.md #4). Only apps/memories/services.py,
    apps/moderation/services.py and internal Django admin ever read it.
    """

    class Status(models.TextChoices):
        VISIBLE = "VISIBLE", "Visible"
        REPORTED = "REPORTED", "Reported"
        HIDDEN = "HIDDEN", "Hidden"

    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="memories")
    author = models.ForeignKey(
        "participants.Participant", on_delete=models.CASCADE, related_name="memories_written"
    )
    target = models.ForeignKey(
        "participants.Participant", on_delete=models.CASCADE, related_name="memories_received"
    )
    # 2000 chars: not specified numerically in docs/UX.md #6 ("large textarea")
    # or docs/SECURITY.md ("maximum text length") — a documented assumption,
    # generous enough for a real memory/story.
    text = models.CharField(max_length=2000)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.VISIBLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F("target")), name="memory_no_self_target"
            ),
        ]
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["target"]),
            models.Index(fields=["target", "status"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"memory #{self.pk} about participant #{self.target_id}"
