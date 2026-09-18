from django.conf import settings
from django.db import models


class Participant(models.Model):
    """A user's participant profile within a single event.

    Modeled as a one-to-one with User (not a plain ForeignKey): this MVP
    supports one event at a time and every login IS a participant, so a
    second event later would need its own User accounts rather than
    re-using this row. Documented assumption — see docs/DATABASE.md #3.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="participant",
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="participants",
    )
    display_name = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["event", "is_active"]),
        ]

    def __str__(self):
        return self.display_name
