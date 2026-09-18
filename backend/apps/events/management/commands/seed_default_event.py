from django.core.management.base import BaseCommand

from apps.events.models import Event

# Hardcoded rather than passed as a CLI arg: this command is only ever run
# once against production via a non-interactive remote shell, where passing
# Persian text through several layers of shell quoting is unreliable.
EVENT_NAME = "جشن فرافارغ التحصیلی ورودی ۹۸"
EVENT_STATUS = Event.Status.OPEN


class Command(BaseCommand):
    help = "Create the graduation event for this deployment, if it doesn't exist yet."

    def handle(self, *args, **options):
        event, created = Event.objects.get_or_create(
            name=EVENT_NAME,
            defaults={"status": EVENT_STATUS},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"رویداد «{event.name}» ساخته شد (id={event.id})."))
        else:
            self.stdout.write(self.style.WARNING(f"رویداد «{event.name}» از قبل وجود داشت (id={event.id})."))
