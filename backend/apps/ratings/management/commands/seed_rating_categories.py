from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.events.models import Event
from apps.ratings.models import RatingCategory

# The 25 categories defined in docs/RATING_SYSTEM.md #2-#3, in seed order.
# Categories 1-16 are the core set (required=True); 17-25 are the
# "additional suggested" set, which the doc says should start optional.
CATEGORIES = [
    {"key": "shift_behavior", "left_label": "خوش‌کشیک", "right_label": "بدکشیک", "required": True},
    {"key": "vibe", "left_label": "خوش‌فاز", "right_label": "بدفاز", "required": True},
    {"key": "team_support", "left_label": "گردن‌گیر و کاور", "right_label": "بندازکن", "required": True},
    {
        "key": "morning_responsibility",
        "left_label": "سپر بلا",
        "right_label": "گردن‌نگیر",
        "description": "مخصوصاً در مورنینگ",
        "required": True,
    },
    {"key": "responsibility", "left_label": "مسئولیت‌پذیر", "right_label": "می‌پیچونه", "required": True},
    {"key": "call_room_sleeping", "left_label": "پاویون‌خواب", "right_label": "باید خونه بخوابم", "required": True},
    {"key": "shift_preference", "left_label": "کشیک‌خر", "right_label": "کشیک‌فروش", "required": True},
    {"key": "personality_style", "left_label": "ادایی", "right_label": "خاکی", "required": True},
    {"key": "fashion_style", "left_label": "خوش‌استایل", "right_label": "بدسلیقه", "required": True},
    {"key": "practical_skill", "left_label": "عمل‌بالا", "right_label": "سوبر", "required": True},
    {"key": "loyalty", "left_label": "بامرام", "right_label": "بی‌معرفت", "required": True},
    {"key": "social_circle", "left_label": "رفیق‌باز", "right_label": "تنها", "required": True},
    {"key": "calmness", "left_label": "چیل", "right_label": "حساس", "required": True},
    {"key": "work_ethic", "left_label": "پرتلاش", "right_label": "تنبل", "required": True},
    {"key": "study_habits", "left_label": "درس‌خون", "right_label": "کمتر اهل درس", "required": True},
    {
        "key": "social_communication",
        "left_label": "اجتماعی و مذاکره‌گر",
        "right_label": "ساکت و سر به زیر",
        "required": True,
    },
    {"key": "punctuality", "left_label": "وقت‌شناس", "right_label": "همیشه دیر", "required": False},
    {"key": "organization", "left_label": "منظم", "right_label": "شلخته", "required": False},
    {"key": "helpfulness", "left_label": "کمک‌حال", "right_label": "خودش‌محور", "required": False},
    {"key": "humor", "left_label": "شوخ‌طبع", "right_label": "جدی", "required": False},
    {"key": "commitment", "left_label": "پای کار", "right_label": "جا می‌زنه", "required": False},
    {"key": "leadership", "left_label": "رهبر", "right_label": "دنبال‌رو", "required": False},
    {"key": "communication_style", "left_label": "حاضر جواب", "right_label": "کم‌حرف", "required": False},
    {"key": "emotional_reactivity", "left_label": "خونسرد", "right_label": "زودجوش", "required": False},
    {"key": "creativity", "left_label": "خلاق", "right_label": "کلاسیک", "required": False},
]


class Command(BaseCommand):
    help = "Seed the initial rating categories from docs/RATING_SYSTEM.md for one or all events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--event",
            type=int,
            dest="event_id",
            help="Only seed this event id. Defaults to every existing event.",
        )

    def handle(self, *args, **options):
        event_id = options.get("event_id")
        events = Event.objects.filter(pk=event_id) if event_id else Event.objects.all()

        if event_id and not events.exists():
            raise CommandError(f"رویدادی با شناسه {event_id} پیدا نشد.")

        if not events.exists():
            self.stdout.write(self.style.WARNING("هیچ رویدادی برای seed کردن دسته‌ها پیدا نشد."))
            return

        for event in events:
            created_count = 0
            with transaction.atomic():
                for index, data in enumerate(CATEGORIES):
                    _, created = RatingCategory.objects.get_or_create(
                        event=event,
                        key=data["key"],
                        defaults={
                            "left_label": data["left_label"],
                            "right_label": data["right_label"],
                            "description": data.get("description", ""),
                            "order": index,
                            "required": data["required"],
                            "active": True,
                        },
                    )
                    if created:
                        created_count += 1

            self.stdout.write(
                self.style.SUCCESS(f"رویداد «{event.name}»: {created_count} دسته جدید ایجاد شد.")
            )
