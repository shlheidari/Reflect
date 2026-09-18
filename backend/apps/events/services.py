from apps.memories.models import Memory
from apps.participants.models import Participant
from apps.ratings.models import Rating


def get_admin_statistics(event):
    """Admin dashboard "Overview" numbers for one event (docs/PRODUCT.md #9,
    docs/ROADMAP.md Phase 8). Every figure here is a plain aggregate count —
    nothing evaluator-identifying is ever touched (docs/PRIVACY.md #11)."""

    participants = Participant.objects.filter(event=event)
    total_participants = participants.count()
    active_participants = participants.filter(is_active=True).count()
    participants_logged_in = participants.filter(user__last_login__isnull=False).count()

    ratings = Rating.objects.filter(event=event)
    total_ratings = ratings.count()
    participants_rated = ratings.values("evaluator").distinct().count()

    total_memories = Memory.objects.filter(event=event).count()

    average_ratings_per_participant = (
        round(total_ratings / total_participants, 1) if total_participants else 0.0
    )
    participation_percentage = (
        round((participants_rated / total_participants) * 100, 1) if total_participants else 0.0
    )

    return {
        "event_id": event.id,
        "total_participants": total_participants,
        "active_participants": active_participants,
        "participants_logged_in": participants_logged_in,
        "participants_rated": participants_rated,
        "total_ratings": total_ratings,
        "total_memories": total_memories,
        "average_ratings_per_participant": average_ratings_per_participant,
        "participation_percentage": participation_percentage,
    }
