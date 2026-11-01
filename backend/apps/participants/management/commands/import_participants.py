import base64
import csv
import io
import os

from django.core.management.base import BaseCommand, CommandError

from apps.events.models import Event
from apps.accounts.models import User
from apps.participants.models import Participant

# Data is passed via the PARTICIPANTS_IMPORT_DATA_B64 env var (base64-encoded
# CSV: اسم,شماره دانشجویی,کد ملی) rather than a CLI arg or a file committed to
# git — real people's national codes/student numbers must never land in git
# history, and base64 sidesteps the Persian-text-through-shell mangling seen
# with `liara shell --command`.
ENV_VAR = "PARTICIPANTS_IMPORT_DATA_B64"


class Command(BaseCommand):
    help = (
        "Create User+Participant rows for event guests from CSV data "
        f"(name, student number, national code) base64-encoded in the {ENV_VAR} "
        "env var. Username = student number, password = national code."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-id",
            type=int,
            default=None,
            help="Event to attach participants to. Defaults to the only Event if exactly one exists.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Also reset password/display_name for rows whose user already exists.",
        )

    def handle(self, *args, **options):
        raw = os.environ.get(ENV_VAR)
        if not raw:
            raise CommandError(f"{ENV_VAR} env var is not set.")

        try:
            csv_text = base64.b64decode(raw).decode("utf-8")
        except Exception as exc:
            raise CommandError(f"Could not decode {ENV_VAR} as base64 UTF-8 CSV: {exc}")

        event_id = options["event_id"]
        if event_id is not None:
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                raise CommandError(f"No Event with id={event_id}.")
        else:
            count = Event.objects.count()
            if count != 1:
                raise CommandError(
                    f"{count} events exist; pass --event-id to pick one."
                )
            event = Event.objects.get()

        reader = csv.DictReader(io.StringIO(csv_text))
        created_users = 0
        updated_users = 0
        created_participants = 0
        updated_participants = 0
        skipped = []

        for row in reader:
            name = (row.get("اسم") or "").strip()
            student_no = (row.get("شماره دانشجویی") or "").strip()
            national_code = (row.get("کد ملی") or "").strip()

            if not name or not student_no or not national_code:
                skipped.append(name or student_no or "؟")
                continue

            user, was_created = User.objects.get_or_create(
                username=student_no,
                defaults={"first_name": name},
            )
            if was_created:
                user.set_password(national_code)
                user.save(update_fields=["password"])
                created_users += 1
            elif options["update"]:
                user.set_password(national_code)
                user.first_name = name
                user.save(update_fields=["password", "first_name"])
                updated_users += 1

            _, participant_created = Participant.objects.update_or_create(
                user=user,
                event=event,
                defaults={"display_name": name},
            )
            if participant_created:
                created_participants += 1
            else:
                updated_participants += 1

        self.stdout.write(self.style.SUCCESS(
            f"کاربران ساخته‌شده: {created_users} | کاربران به‌روزشده: {updated_users} | "
            f"شرکت‌کننده‌های ساخته‌شده: {created_participants} | "
            f"شرکت‌کننده‌های موجود: {updated_participants} | "
            f"ردیف‌های رد شده: {len(skipped)}"
        ))
        if skipped:
            self.stdout.write(self.style.WARNING("رد شده (فیلد ناقص): " + ", ".join(skipped)))
