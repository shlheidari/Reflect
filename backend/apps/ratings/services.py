from django.db import transaction
from django.db.models import Avg, Count, Q

from apps.events.models import Event
from apps.memories.services import create_memory
from apps.participants.models import Participant

from .models import Rating, RatingCategory


class RatingSubmissionError(Exception):
    """Raised by the functions below; views translate this into the
    project's standard {"detail", "code"} error response (matching the
    pattern already used by AdminRatingCategoryViewSet.reorder)."""

    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(detail)


def _validate_target(evaluator, target_id):
    try:
        target = Participant.objects.select_related("event").get(pk=target_id)
    except Participant.DoesNotExist:
        raise RatingSubmissionError("invalid_target", "شرکت‌کننده مقصد یافت نشد.")

    if target.pk == evaluator.pk:
        raise RatingSubmissionError("self_rating", "امکان ثبت نظر درباره خودتان وجود ندارد.")

    if not target.is_active or target.event_id != evaluator.event_id:
        raise RatingSubmissionError("invalid_target", "شرکت‌کننده مقصد یافت نشد.")

    return target


def _validate_event_open(event):
    if event.status != Event.Status.OPEN:
        raise RatingSubmissionError("event_closed", "این رویداد در حال حاضر برای ثبت نظر باز نیست.")


def _validate_categories(event, items, *, enforce_required):
    category_ids = [item["category_id"] for item in items]

    if len(set(category_ids)) != len(category_ids):
        raise RatingSubmissionError(
            "duplicate_category", "هر دسته فقط یک‌بار می‌تواند در یک ارسال ثبت شود."
        )

    categories = {c.id: c for c in RatingCategory.objects.filter(event=event, id__in=category_ids)}
    if len(categories) != len(category_ids):
        raise RatingSubmissionError("invalid_category", "دسته امتیازدهی نامعتبر است.")

    if any(not categories[cid].active for cid in category_ids):
        raise RatingSubmissionError("inactive_category", "این دسته امتیازدهی غیرفعال است.")

    if enforce_required:
        required_ids = set(
            RatingCategory.objects.filter(event=event, active=True, required=True).values_list(
                "id", flat=True
            )
        )
        if required_ids - set(category_ids):
            raise RatingSubmissionError(
                "required_category_missing", "همه دسته‌های اجباری باید تکمیل شوند."
            )

    return categories


@transaction.atomic
def submit_ratings(evaluator, target_id, items, memory_text=""):
    """Create a participant's full rating set for one target, plus an
    optional anonymous memory (docs/PRODUCT.md #5 "create optional memory").
    All-or-nothing: if a target has ever been rated by this evaluator
    before, the whole request is rejected (docs/API.md separates create
    from the dedicated update endpoint, so partial re-submission goes
    through `update_ratings`)."""

    target = _validate_target(evaluator, target_id)
    _validate_event_open(evaluator.event)
    categories = _validate_categories(evaluator.event, items, enforce_required=True)

    if Rating.objects.filter(evaluator=evaluator, target=target).exists():
        raise RatingSubmissionError(
            "duplicate_rating", "شما قبلاً درباره این شخص نظر ثبت کرده‌اید."
        )

    ratings = [
        Rating(
            event=evaluator.event,
            evaluator=evaluator,
            target=target,
            category=categories[item["category_id"]],
            score=item["score"],
        )
        for item in items
    ]
    created = Rating.objects.bulk_create(ratings)
    create_memory(event=evaluator.event, author=evaluator, target=target, text=memory_text)
    return created


@transaction.atomic
def update_ratings(evaluator, target_id, items):
    """Update an evaluator's own previously-submitted scores for one target.
    Only allowed when the event's `allow_rating_edit` flag is set. Partial:
    categories not present in `items` are left untouched, so completeness
    (all required categories) is not re-enforced here."""

    target = _validate_target(evaluator, target_id)
    event = evaluator.event
    _validate_event_open(event)

    if not event.allow_rating_edit:
        raise RatingSubmissionError(
            "rating_edit_not_allowed", "ویرایش نظرات برای این رویداد فعال نیست."
        )

    categories = _validate_categories(event, items, enforce_required=False)

    if not Rating.objects.filter(evaluator=evaluator, target=target).exists():
        raise RatingSubmissionError("not_found", "نظری برای ویرایش یافت نشد.")

    updated = []
    for item in items:
        rating, _ = Rating.objects.update_or_create(
            evaluator=evaluator,
            target=target,
            category=categories[item["category_id"]],
            event=event,
            defaults={"score": item["score"]},
        )
        updated.append(rating)
    return updated


def get_my_results(me):
    """Anonymous aggregate results for `me` (docs/API.md "My Results").

    Only ever touches Count/Avg over Rating rows scoped to `target=me` —
    `evaluator` never enters the returned data, so there is nothing
    evaluator-identifying to accidentally leak (docs/PRIVACY.md #3, #7).

    The overall `rating_count` (distinct evaluators across any category) is
    always shown, matching the same-named field already exposed on
    /api/participants/ (docs/PRIVACY.md #9 — a plain count is not
    evaluator-identifying). Each category's `average` is independently
    gated on `minimum_ratings_for_results`: optional categories can lag
    behind the overall count since evaluators may skip them, so thresholding
    only the top-level count would leak low-N averages for those.
    """

    threshold = me.event.minimum_ratings_for_results

    rating_count = Rating.objects.filter(target=me).values("evaluator").distinct().count()

    categories = (
        RatingCategory.objects.filter(event=me.event, active=True)
        .order_by("order", "id")
        .annotate(
            _avg=Avg("ratings__score", filter=Q(ratings__target=me)),
            _count=Count("ratings", filter=Q(ratings__target=me)),
        )
    )

    category_results = []
    for category in categories:
        enough = category._count >= threshold
        category_results.append(
            {
                "category_id": category.id,
                "left_label": category.left_label,
                "right_label": category.right_label,
                "average": round(float(category._avg), 1) if enough and category._avg is not None else None,
                "count": category._count,
                "has_enough_ratings": enough,
            }
        )

    return {"rating_count": rating_count, "categories": category_results}
