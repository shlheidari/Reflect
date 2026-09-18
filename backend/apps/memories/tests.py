from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.events.models import Event
from apps.moderation.models import Report
from apps.ratings.tests import AuthMixin, make_category, make_participant

from .models import Memory


class MemoryCreationTests(AuthMixin, APITestCase):
    """docs/PRODUCT.md #5: an optional memory is created alongside a rating
    submission. Validation (authenticated author, valid non-self target,
    OPEN event, max length) is exercised through the same
    RatingSubmitView/submit_ratings path already tested in apps.ratings —
    here we only check the memory side effect."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.ali = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.sara = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        self.category = make_category(self.event, "vibe", order=0, required=True)

    def _submit(self, target_id, memory=""):
        self.auth_as("ali", "ali-pass-123")
        return self.client.post(
            reverse("rating-submit"),
            {
                "target_id": target_id,
                "ratings": [{"category_id": self.category.id, "score": 7}],
                "memory": memory,
            },
            format="json",
        )

    def test_memory_created_alongside_rating_submission(self):
        response = self._submit(self.sara.id, memory="یه خاطره قشنگ از اون کشیک")

        self.assertEqual(response.status_code, 201)
        memory = Memory.objects.get(target=self.sara, author=self.ali)
        self.assertEqual(memory.text, "یه خاطره قشنگ از اون کشیک")
        self.assertEqual(memory.status, Memory.Status.VISIBLE)
        self.assertEqual(memory.event_id, self.event.id)

    def test_blank_memory_creates_no_row(self):
        response = self._submit(self.sara.id, memory="   ")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Memory.objects.count(), 0)

    def test_omitted_memory_field_creates_no_row(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(
            reverse("rating-submit"),
            {"target_id": self.sara.id, "ratings": [{"category_id": self.category.id, "score": 7}]},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Memory.objects.count(), 0)

    def test_maximum_length_is_rejected(self):
        response = self._submit(self.sara.id, memory="a" * 2001)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Memory.objects.count(), 0)

    def test_exactly_maximum_length_is_accepted(self):
        response = self._submit(self.sara.id, memory="a" * 2000)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Memory.objects.count(), 1)

    def test_self_target_prevents_memory_creation(self):
        response = self._submit(self.ali.id, memory="یادداشت برای خودم")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "self_rating")
        self.assertEqual(Memory.objects.count(), 0)

    def test_closed_event_prevents_memory_creation(self):
        self.event.status = Event.Status.CLOSED
        self.event.save(update_fields=["status"])

        response = self._submit(self.sara.id, memory="نظر بعد از بسته شدن رویداد")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "event_closed")
        self.assertEqual(Memory.objects.count(), 0)


class MyMemoriesTests(AuthMixin, APITestCase):
    """GET /api/me/memories/ — docs/API.md "Memories About Me"."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.me = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.author_a = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        self.author_b = make_participant(
            "mohammad", self.event, display_name="Mohammad", password="mohammad-pass-123"
        )

    def test_requires_authentication(self):
        response = self.client.get(reverse("my-memories"))
        self.assertEqual(response.status_code, 401)

    def test_empty_state(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.get(reverse("my-memories"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

    def test_returns_visible_and_reported_but_excludes_hidden_and_others(self):
        visible = Memory.objects.create(
            event=self.event, author=self.author_a, target=self.me, text="خاطره یک"
        )
        reported = Memory.objects.create(
            event=self.event,
            author=self.author_b,
            target=self.me,
            text="خاطره دو",
            status=Memory.Status.REPORTED,
        )
        Memory.objects.create(
            event=self.event,
            author=self.author_a,
            target=self.me,
            text="این نباید دیده بشه",
            status=Memory.Status.HIDDEN,
        )
        # A memory I wrote about someone else must never appear in my own list.
        Memory.objects.create(event=self.event, author=self.me, target=self.author_a, text="درباره سارا")

        self.auth_as("ali", "ali-pass-123")
        response = self.client.get(reverse("my-memories"))

        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {visible.id, reported.id})

    def test_newest_first(self):
        first = Memory.objects.create(event=self.event, author=self.author_a, target=self.me, text="اول")
        second = Memory.objects.create(event=self.event, author=self.author_b, target=self.me, text="دوم")

        self.auth_as("ali", "ali-pass-123")
        response = self.client.get(reverse("my-memories"))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids, [second.id, first.id])

    def test_response_items_never_expose_author_information(self):
        Memory.objects.create(event=self.event, author=self.author_a, target=self.me, text="خاطره یک")

        self.auth_as("ali", "ali-pass-123")
        response = self.client.get(reverse("my-memories"))

        item = response.data["results"][0]
        self.assertEqual(set(item.keys()), {"id", "text"})


class MemoryReportTests(AuthMixin, APITestCase):
    """POST /api/memories/{id}/report/ — docs/API.md "Report Memory".

    A participant may only ever report a memory addressed to them (the only
    memories they can see, via /api/me/memories/), so every memory here has
    `target=self.reporter`."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.reporter = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.author = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        self.bystander = make_participant(
            "mohammad", self.event, display_name="Mohammad", password="mohammad-pass-123"
        )
        self.memory = Memory.objects.create(
            event=self.event, author=self.author, target=self.reporter, text="یه خاطره"
        )

    def test_requires_authentication(self):
        response = self.client.post(
            reverse("memory-report", args=[self.memory.id]), {"reason": "inappropriate"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_report_creates_report_and_flags_memory(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(
            reverse("memory-report", args=[self.memory.id]), {"reason": "inappropriate"}, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.filter(memory=self.memory, reporter=self.reporter).count(), 1)
        self.memory.refresh_from_db()
        self.assertEqual(self.memory.status, Memory.Status.REPORTED)

    def test_report_without_reason_is_allowed(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("memory-report", args=[self.memory.id]), {}, format="json")

        self.assertEqual(response.status_code, 201)

    def test_duplicate_report_by_same_participant_is_rejected(self):
        self.auth_as("ali", "ali-pass-123")
        self.client.post(reverse("memory-report", args=[self.memory.id]), {}, format="json")
        response = self.client.post(reverse("memory-report", args=[self.memory.id]), {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "already_reported")
        self.assertEqual(Report.objects.filter(memory=self.memory).count(), 1)

    def test_reporting_nonexistent_memory_is_not_found(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("memory-report", args=[999999]), {}, format="json")

        self.assertEqual(response.status_code, 404)

    def test_reporting_memory_from_another_event_is_not_found(self):
        other_event = Event.objects.create(name="Other Event", status=Event.Status.OPEN)
        other_author = make_participant("reza", other_event, display_name="Reza", password="reza-pass-123")
        other_target = make_participant(
            "kian", other_event, display_name="Kian", password="kian-pass-123"
        )
        other_memory = Memory.objects.create(
            event=other_event, author=other_author, target=other_target, text="یه خاطره از رویداد دیگه"
        )

        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("memory-report", args=[other_memory.id]), {}, format="json")

        self.assertEqual(response.status_code, 404)

    def test_reporting_a_memory_not_addressed_to_you_is_not_found(self):
        # A memory about someone else, in the same event: ali must not be
        # able to report (and thereby flip the status of) content that has
        # nothing to do with him, and must not learn its ID is valid.
        others_memory = Memory.objects.create(
            event=self.event, author=self.author, target=self.bystander, text="خاطره درباره یکی دیگه"
        )

        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("memory-report", args=[others_memory.id]), {}, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["code"], "not_found")
        self.assertFalse(Report.objects.filter(memory=others_memory).exists())
        others_memory.refresh_from_db()
        self.assertEqual(others_memory.status, Memory.Status.VISIBLE)

    def test_report_already_reported_memory_does_not_change_status(self):
        self.memory.status = Memory.Status.REPORTED
        self.memory.save(update_fields=["status"])

        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("memory-report", args=[self.memory.id]), {}, format="json")

        self.assertEqual(response.status_code, 201)
        self.memory.refresh_from_db()
        self.assertEqual(self.memory.status, Memory.Status.REPORTED)

    def test_reporting_hidden_memory_does_not_unhide_it(self):
        self.memory.status = Memory.Status.HIDDEN
        self.memory.save(update_fields=["status"])

        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("memory-report", args=[self.memory.id]), {}, format="json")

        self.assertEqual(response.status_code, 201)
        self.memory.refresh_from_db()
        self.assertEqual(self.memory.status, Memory.Status.HIDDEN)


class MemoryDatabaseConstraintTests(APITestCase):
    """docs/ROADMAP.md Phase 9 "Database Security" — the self-target
    CheckConstraint on Memory.Meta must hold even when the ORM is used
    directly, bypassing apps.memories.services.create_memory's own guard."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.me = make_participant("ali", self.event, "Ali", password="ali-pass-123")

    def test_db_rejects_self_targeted_memory_bypassing_the_service_layer(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Memory.objects.create(event=self.event, author=self.me, target=self.me, text="یادداشت برای خودم")


class MemoryContentSafetyTests(AuthMixin, APITestCase):
    """docs/ROADMAP.md Phase 9 "XSS" / docs/SECURITY.md "Text Content": a
    memory containing markup must never be rendered as HTML. The frontend
    never uses dangerouslySetInnerHTML (memory text is only ever interpolated
    into JSX, which React escapes automatically), but that guarantee is only
    real if the API actually serves the text as a JSON string and not, say,
    inside an HTML fragment a future endpoint might render server-side."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.author = make_participant("ali", self.event, "Ali", password="ali-pass-123")
        self.target = make_participant("sara", self.event, "Sara", password="sara-pass-123")
        self.category = make_category(self.event, "vibe", order=0)

    def test_markup_in_memory_text_is_stored_verbatim_and_served_as_json(self):
        payload = "<script>alert('xss')</script><img src=x onerror=alert(1)>"

        self.auth_as("ali", "ali-pass-123")
        submit = self.client.post(
            reverse("rating-submit"),
            {
                "target_id": self.target.id,
                "ratings": [{"category_id": self.category.id, "score": 6}],
                "memory": payload,
            },
            format="json",
        )
        self.assertEqual(submit.status_code, 201)
        self.client.credentials()

        self.auth_as("sara", "sara-pass-123")
        response = self.client.get(reverse("my-memories"))

        # Served as a genuine JSON response — a browser will never parse
        # this body as HTML/script regardless of what the string contains.
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["Content-Type"])
        self.assertEqual(response.data["results"][0]["text"], payload)

        # The stored value is exactly what was submitted — the backend
        # never attempts (and must never need) to sanitize/strip markup
        # itself, since rendering safety is React's job, not the API's.
        self.assertEqual(Memory.objects.get(target=self.target).text, payload)


class MemoryPrivacyTests(AuthMixin, APITestCase):
    """Dedicated privacy proof (docs/PRIVACY.md #15, docs/ROADMAP.md Phase 7):
    Participant A writes a memory about Participant B via the real rating
    submission API; B's /api/me/memories/ response must contain nothing
    that could identify A."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.author_a = make_participant("ali", self.event, "Ali Rezaei", password="ali-pass-123")
        self.target_b = make_participant("mohammad", self.event, "Mohammad", password="reza-pass-123")
        self.category = make_category(self.event, "vibe", order=0)

    @staticmethod
    def _collect_keys_and_strings(node, keys, strings):
        if isinstance(node, dict):
            for key, value in node.items():
                keys.append(str(key))
                MemoryPrivacyTests._collect_keys_and_strings(value, keys, strings)
        elif isinstance(node, list):
            for item in node:
                MemoryPrivacyTests._collect_keys_and_strings(item, keys, strings)
        elif isinstance(node, str):
            strings.append(node)

    def test_author_identity_never_exposed_in_my_memories(self):
        self.auth_as("ali", "ali-pass-123")
        submit_response = self.client.post(
            reverse("rating-submit"),
            {
                "target_id": self.target_b.id,
                "ratings": [{"category_id": self.category.id, "score": 8}],
                "memory": "یاد اون کشیک هیچ‌وقت یادم نمیره 😂",
            },
            format="json",
        )
        self.assertEqual(submit_response.status_code, 201)
        self.client.credentials()

        self.auth_as("mohammad", "reza-pass-123")
        response = self.client.get(reverse("my-memories"))
        self.assertEqual(response.status_code, 200)

        keys, strings = [], []
        self._collect_keys_and_strings(response.data, keys, strings)

        for key in keys:
            self.assertNotIn("author", key.lower())

        self.assertNotIn("ali", strings)
        self.assertNotIn("Ali Rezaei", strings)
        self.assertNotIn(str(self.author_a.user_id), strings)

        self.assertEqual(response.data["results"][0]["text"], "یاد اون کشیک هیچ‌وقت یادم نمیره 😂")
