from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

key_validator = RegexValidator(
    regex=r"^[a-z][a-z0-9_]*$",
    message="کلید باید با حرف انگلیسی کوچک شروع شود و فقط شامل حروف کوچک، عدد و زیرخط باشد.",
)


class RatingCategory(models.Model):
    """A single bipolar (0-10) scale participants rate each other on within
    an event, e.g. خوش‌کشیک <-> بدکشیک. docs/RATING_SYSTEM.md #2 defines the
    seed set; docs/DATABASE.md #4 defines this schema."""

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="rating_categories",
    )
    key = models.CharField(max_length=50, validators=[key_validator])
    left_label = models.CharField(max_length=100)
    right_label = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    required = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event", "order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["event", "key"], name="unique_rating_category_key_per_event"),
        ]
        indexes = [
            models.Index(fields=["event", "active"]),
        ]

    def __str__(self):
        return f"{self.left_label} / {self.right_label}"


class Rating(models.Model):
    """One evaluator's 0-10 score for one target participant on one category,
    within one event (docs/DATABASE.md #5).

    `event` is denormalized onto every row (also derivable via `category.event`
    or `target.event`) so the uniqueness constraint and per-event indexes
    don't require a join — same rationale as RatingCategory.event above.

    Privacy-critical: `evaluator` must never appear in a participant-facing
    serializer/response (docs/PRIVACY.md #3). Only apps/ratings/services.py
    and internal Django admin ever read it.
    """

    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="ratings")
    evaluator = models.ForeignKey(
        "participants.Participant", on_delete=models.CASCADE, related_name="ratings_given"
    )
    target = models.ForeignKey(
        "participants.Participant", on_delete=models.CASCADE, related_name="ratings_received"
    )
    category = models.ForeignKey(RatingCategory, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["evaluator", "target", "category", "event"],
                name="unique_rating_per_evaluator_target_category_event",
            ),
            models.CheckConstraint(
                check=models.Q(score__gte=0) & models.Q(score__lte=10),
                name="rating_score_range",
            ),
            models.CheckConstraint(
                check=~models.Q(evaluator=models.F("target")),
                name="rating_no_self_rating",
            ),
        ]
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["evaluator"]),
            models.Index(fields=["target"]),
            models.Index(fields=["category"]),
            models.Index(fields=["target", "category"]),
        ]

    def __str__(self):
        return f"rating #{self.pk}: {self.category_id} -> {self.score}"
