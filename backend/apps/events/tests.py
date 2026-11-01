from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.ratings.tests import make_category, make_participant

from .models import Event

User = get_user_model()


class AuthMixin:
    def auth_as(self, username, password):
        login = self.client.post(reverse("auth-login"), {"username": username, "password": password})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")


class AdminEventApiTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026", status=Event.Status.DRAFT)
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")

    def test_unauthenticated_is_rejected(self):
        response = self.client.get("/api/admin/events/")
        self.assertEqual(response.status_code, 401)

    def test_non_admin_participant_is_forbidden(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.get("/api/admin/events/")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_events_unpaginated(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.get("/api/admin/events/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]["name"], "Event 2026")

    def test_admin_can_update_event_settings(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.patch(
            f"/api/admin/events/{self.event.id}/",
            {
                "status": "OPEN",
                "results_enabled": False,
                "memories_enabled": False,
                "allow_rating_edit": True,
                "minimum_ratings_for_results": 5,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, Event.Status.OPEN)
        self.assertFalse(self.event.results_enabled)
        self.assertFalse(self.event.memories_enabled)
        self.assertTrue(self.event.allow_rating_edit)
        self.assertEqual(self.event.minimum_ratings_for_results, 5)

    def test_admin_can_create_event(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/events/", {"name": "Event 2027", "status": "DRAFT"}, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Event.objects.filter(name="Event 2027").exists())

    def test_admin_cannot_delete_event(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.delete(f"/api/admin/events/{self.event.id}/")

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Event.objects.filter(pk=self.event.id).exists())


class AdminStatisticsTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026", status=Event.Status.OPEN)
        self.other_event = Event.objects.create(name="Other Event", status=Event.Status.OPEN)
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)

    def test_unauthenticated_is_rejected(self):
        response = self.client.get(f"/api/admin/events/{self.event.id}/statistics/")
        self.assertEqual(response.status_code, 401)

    def test_non_admin_participant_is_forbidden(self):
        make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(f"/api/admin/events/{self.event.id}/statistics/")

        self.assertEqual(response.status_code, 403)

    def test_statistics_with_no_participants(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.get(f"/api/admin/events/{self.event.id}/statistics/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "event_id": self.event.id,
                "total_participants": 0,
                "active_participants": 0,
                "participants_logged_in": 0,
                "participants_rated": 0,
                "total_ratings": 0,
                "total_memories": 0,
                "average_ratings_per_participant": 0.0,
                "participation_percentage": 0.0,
            },
        )

    def test_statistics_reflect_real_activity_and_ignore_other_events(self):
        ali = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        sara = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        make_participant("hidden", self.event, display_name="Hidden", is_active=False)
        make_participant("nora", self.other_event, display_name="Nora", password="nora-pass-123")
        nora2 = make_participant(
            "nora2", self.other_event, display_name="Nora2", password="nora2-pass-123"
        )

        category = make_category(self.event, "vibe", order=0)
        other_category = make_category(self.other_event, "vibe", order=0)

        self.auth_as("ali", "ali-pass-123")
        self.client.post(
            reverse("rating-submit"),
            {
                "target_id": sara.id,
                "ratings": [{"category_id": category.id, "score": 8}],
                "memory": "یه خاطره",
            },
            format="json",
        )
        self.client.credentials()

        # Activity in the other event must never leak into this event's stats.
        self.auth_as("nora", "nora-pass-123")
        self.client.post(
            reverse("rating-submit"),
            {"target_id": nora2.id, "ratings": [{"category_id": other_category.id, "score": 5}]},
            format="json",
        )
        self.client.credentials()

        ali.user.last_login = ali.user.date_joined
        ali.user.save(update_fields=["last_login"])

        self.auth_as("admin", "admin-pass-123")
        response = self.client.get(f"/api/admin/events/{self.event.id}/statistics/")

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["total_participants"], 3)
        self.assertEqual(data["active_participants"], 2)
        self.assertEqual(data["participants_logged_in"], 1)
        self.assertEqual(data["participants_rated"], 1)
        self.assertEqual(data["total_ratings"], 1)
        self.assertEqual(data["total_memories"], 1)
        self.assertAlmostEqual(data["average_ratings_per_participant"], round(1 / 3, 1))
        self.assertAlmostEqual(data["participation_percentage"], round((1 / 3) * 100, 1))
