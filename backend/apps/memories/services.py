from .models import Memory


def create_memory(*, event, author, target, text):
    """Create a memory row if `text` is non-blank after stripping. Returns
    None when there's nothing to save, so callers can treat "no memory
    typed" and "blank memory" identically (docs/PRODUCT.md #5 — the memory
    is optional). Caller is responsible for validating event/target/author
    beforehand (apps/ratings/services.submit_ratings already does this)."""

    text = text.strip()
    if not text:
        return None
    return Memory.objects.create(event=event, author=author, target=target, text=text)


def get_memories_about_me(me):
    """Anonymous memories written about `me` (docs/API.md "Memories About
    Me"). HIDDEN memories are excluded; REPORTED ones stay visible until an
    admin actually hides them (see apps.moderation.models.Report's
    docstring). `author` is never touched here — there is nothing
    evaluator-identifying to leak (docs/PRIVACY.md #4)."""

    return Memory.objects.filter(target=me).exclude(status=Memory.Status.HIDDEN).order_by("-created_at")
