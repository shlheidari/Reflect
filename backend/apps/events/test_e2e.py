"""End-to-end scenario test (docs/ROADMAP.md Phase 10 / docs/TESTING.md
"End-to-End"). Walks the full product flow through the real HTTP API in one
continuous session, the same way a browser would: admin sets up an event,
one participant rates and writes a memory about another, the target reads
their anonymous results/memory, and the event closes off further ratings.

This is deliberately a single long test rather than one-assertion-per-method
tests (used everywhere else in this codebase) because the whole point is
verifying the *sequence* holds together end-to-end — each individual
assertion already has narrower, isolated coverage elsewhere (apps.ratings,
apps.memories, apps.participants, apps.events tests)."""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.ratings.tests import AuthMixin

from .models import Event

User = get_user_model()


class FullProductFlowE2ETest(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_user(
            username="e2e-admin", password="admin-pass-123", is_staff=True
        )

    def test_full_admin_to_participant_flow(self):
        # 1. Admin logs in.
        self.auth_as("e2e-admin", "admin-pass-123")

        # 2. Admin creates an event (starts DRAFT; opened once set up).
        response = self.client.post(
            "/api/admin/events/", {"name": "Graduation 2026", "status": "DRAFT"}, format="json"
        )
        self.assertEqual(response.status_code, 201, response.data)
        event_id = response.data["id"]

        # 3. Admin creates participants A and B.
        response = self.client.post(
            "/api/admin/participants/",
            {
                "username": "e2e-ali",
                "password": "ali-pass-123",
                "display_name": "Ali",
                "event": event_id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        participant_a_id = response.data["id"]

        response = self.client.post(
            "/api/admin/participants/",
            {
                "username": "e2e-sara",
                "password": "sara-pass-123",
                "display_name": "Sara",
                "event": event_id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        participant_b_id = response.data["id"]

        # 4. Admin configures categories.
        response = self.client.post(
            "/api/admin/rating-categories/",
            {
                "event": event_id,
                "key": "good_shift",
                "left_label": "خوش‌کشیک",
                "right_label": "بدکشیک",
                "order": 0,
                "required": True,
                "active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        category_id = response.data["id"]

        # 5. Event becomes OPEN (also drop the results threshold to 1 so a
        # single rating is enough to see an aggregate below).
        response = self.client.patch(
            f"/api/admin/events/{event_id}/",
            {
                "status": "OPEN",
                "results_enabled": True,
                "memories_enabled": True,
                "allow_rating_edit": False,
                "minimum_ratings_for_results": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials()  # log admin out of the test client

        # 6. Participant A logs in.
        self.auth_as("e2e-ali", "ali-pass-123")

        # 7. Participant A sees participants (B is listed, not yet rated).
        response = self.client.get(reverse("participant-list"))
        self.assertEqual(response.status_code, 200)
        listed_ids = [p["id"] for p in response.data["results"]]
        self.assertIn(participant_b_id, listed_ids)
        sara_entry = next(p for p in response.data["results"] if p["id"] == participant_b_id)
        self.assertFalse(sara_entry["rated_by_me"])

        # 8. + 9. Participant A rates Participant B and writes a memory about her.
        response = self.client.post(
            reverse("rating-submit"),
            {
                "target_id": participant_b_id,
                "ratings": [{"category_id": category_id, "score": 9}],
                "memory": "سارا همیشه به بقیه کمک می‌کرد.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.client.credentials()  # log participant A out of the test client

        # 10. Participant B logs in.
        self.auth_as("e2e-sara", "sara-pass-123")

        # 11. Participant B sees an aggregate result (no individual score).
        response = self.client.get(reverse("my-results"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rating_count"], 1)
        category_result = next(
            c for c in response.data["categories"] if c["category_id"] == category_id
        )
        self.assertTrue(category_result["has_enough_ratings"])
        self.assertEqual(category_result["average"], 9.0)

        # 12. Participant B sees the anonymous memory.
        response = self.client.get(reverse("my-memories"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["text"], "سارا همیشه به بقیه کمک می‌کرد.")

        # 13. Participant B cannot identify Participant A: neither response's
        # raw body may contain A's username or the word "evaluator"/"author"
        # (a bare numeric id check isn't meaningful here — small integer ids
        # collide with unrelated fields like rating_count/category_id; the
        # dedicated privacy tests in apps.ratings/apps.memories already do
        # the rigorous per-field scan against the real evaluator pk).
        for payload in (
            self.client.get(reverse("my-results")).content,
            self.client.get(reverse("my-memories")).content,
        ):
            body = payload.decode()
            self.assertNotIn("e2e-ali", body)
            self.assertNotRegex(body, r"(?i)evaluator|author")

        # 14. Participant B cannot access admin APIs.
        response = self.client.get("/api/admin/events/")
        self.assertEqual(response.status_code, 403)

        # 15. Participant B cannot rate themselves.
        response = self.client.post(
            reverse("rating-submit"),
            {
                "target_id": participant_b_id,
                "ratings": [{"category_id": category_id, "score": 5}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "self_rating")
        self.client.credentials()  # log participant B out of the test client

        # 16. Event becomes CLOSED.
        self.auth_as("e2e-admin", "admin-pass-123")
        response = self.client.patch(
            f"/api/admin/events/{event_id}/", {"status": "CLOSED"}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials()

        # 17. Rating submission is rejected once the event is closed.
        self.auth_as("e2e-sara", "sara-pass-123")
        response = self.client.post(
            reverse("rating-submit"),
            {
                "target_id": participant_a_id,
                "ratings": [{"category_id": category_id, "score": 6}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "event_closed")

        event = Event.objects.get(pk=event_id)
        self.assertEqual(event.status, Event.Status.CLOSED)
