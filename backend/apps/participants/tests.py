from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.events.models import Event
from apps.ratings.models import Rating
from apps.ratings.tests import make_category

from .models import Participant

User = get_user_model()


def make_participant(username, event, display_name=None, is_active=True, password="pass12345!"):
    user = User.objects.create_user(username=username, password=password)
    return Participant.objects.create(
        user=user,
        event=event,
        display_name=display_name or username,
        is_active=is_active,
    )


class ParticipantListTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.other_event = Event.objects.create(name="Other Event", status=Event.Status.OPEN)

        self.me = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.peer = make_participant("sara", self.event, display_name="Sara")
        self.inactive_peer = make_participant("hidden", self.event, display_name="Hidden", is_active=False)
        self.other_event_peer = make_participant("nora", self.other_event, display_name="Nora")

    def auth_as(self, username, password):
        login = self.client.post(
            reverse("auth-login"), {"username": username, "password": password}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_requires_authentication(self):
        response = self.client.get(reverse("participant-list"))
        self.assertEqual(response.status_code, 401)

    def test_staff_without_participant_profile_is_forbidden(self):
        User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        self.auth_as("admin", "admin-pass-123")

        response = self.client.get(reverse("participant-list"))
        self.assertEqual(response.status_code, 403)

    def test_deactivated_participant_is_forbidden(self):
        self.me.is_active = False
        self.me.save(update_fields=["is_active"])
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("participant-list"))
        self.assertEqual(response.status_code, 403)

    def test_list_excludes_self_inactive_peers_and_other_events(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("participant-list"))

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.peer.id})

    def test_list_items_never_expose_user_identifiers(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("participant-list"))

        item = response.data["results"][0]
        self.assertEqual(set(item.keys()), {"id", "display_name", "avatar", "rating_count", "rated_by_me"})

    def test_list_includes_rating_placeholders(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("participant-list"))

        item = response.data["results"][0]
        self.assertEqual(item["rating_count"], 0)
        self.assertEqual(item["rated_by_me"], False)


class CurrentUserParticipantTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026")

    def auth_as(self, username, password):
        login = self.client.post(
            reverse("auth-login"), {"username": username, "password": password}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_me_includes_participant_profile(self):
        make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["participant"]["display_name"], "Ali")

    def test_login_response_already_includes_participant_profile(self):
        # Regression: login used to return a bare user (no `participant`),
        # only /api/me/ was enriched — so the frontend showed the username
        # instead of display_name until the next reload.
        make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")

        login = self.client.post(
            reverse("auth-login"), {"username": "ali", "password": "ali-pass-123"}
        )

        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.data["user"]["participant"]["display_name"], "Ali")

    def test_me_participant_is_null_for_staff_without_a_participant_row(self):
        User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        self.auth_as("admin", "admin-pass-123")

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["participant"])


class AdminParticipantApiTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026")
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        self.participant = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")

    def auth_as(self, username, password):
        login = self.client.post(
            reverse("auth-login"), {"username": username, "password": password}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_unauthenticated_is_rejected(self):
        response = self.client.get("/api/admin/participants/")
        self.assertEqual(response.status_code, 401)

    def test_non_admin_participant_is_forbidden(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get("/api/admin/participants/")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_participants_paginated(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.get("/api/admin/participants/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        usernames = {item["username"] for item in response.data["results"]}
        self.assertIn("ali", usernames)

    def test_admin_can_create_participant_with_generated_password(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/participants/",
            {"username": "reza", "display_name": "Reza", "event": self.event.id},
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("generated_password", response.data)
        new_user = User.objects.get(username="reza")
        self.assertTrue(new_user.check_password(response.data["generated_password"]))

    def test_admin_can_create_participant_with_explicit_password(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/participants/",
            {
                "username": "reza",
                "password": "reza-explicit-pass",
                "display_name": "Reza",
                "event": self.event.id,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("generated_password", response.data)
        new_user = User.objects.get(username="reza")
        self.assertTrue(new_user.check_password("reza-explicit-pass"))

    def test_cannot_create_participant_with_duplicate_username(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/participants/",
            {"username": "ali", "display_name": "Ali Again", "event": self.event.id},
        )

        self.assertEqual(response.status_code, 400)

    def test_admin_can_update_display_name_and_deactivate(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.patch(
            f"/api/admin/participants/{self.participant.id}/",
            {"display_name": "Ali Updated", "is_active": False},
        )

        self.assertEqual(response.status_code, 200)
        self.participant.refresh_from_db()
        self.assertEqual(self.participant.display_name, "Ali Updated")
        self.assertFalse(self.participant.is_active)

    def test_updating_username_field_via_patch_is_ignored(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.patch(
            f"/api/admin/participants/{self.participant.id}/",
            {"username": "hacker"},
        )

        self.assertEqual(response.status_code, 200)
        self.participant.refresh_from_db()
        self.assertEqual(self.participant.user.username, "ali")

    def test_admin_reset_password_with_explicit_value(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            f"/api/admin/participants/{self.participant.id}/reset-password/",
            {"new_password": "brand-new-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("generated_password", response.data)
        self.participant.user.refresh_from_db()
        self.assertTrue(self.participant.user.check_password("brand-new-password"))

    def test_admin_reset_password_generates_when_omitted(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(f"/api/admin/participants/{self.participant.id}/reset-password/", {})

        self.assertEqual(response.status_code, 200)
        self.assertIn("generated_password", response.data)
        self.participant.user.refresh_from_db()
        self.assertTrue(self.participant.user.check_password(response.data["generated_password"]))

    def test_admin_cannot_use_participant_write_endpoints_to_delete(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.delete(f"/api/admin/participants/{self.participant.id}/")

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Participant.objects.filter(pk=self.participant.id).exists())

    def test_admin_can_reactivate_a_deactivated_participant(self):
        self.participant.is_active = False
        self.participant.save(update_fields=["is_active"])
        self.auth_as("admin", "admin-pass-123")

        response = self.client.patch(
            f"/api/admin/participants/{self.participant.id}/", {"is_active": True}
        )

        self.assertEqual(response.status_code, 200)
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.is_active)

    def test_list_exposes_participation_status_without_evaluator_detail(self):
        peer = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        category = make_category(self.event, "vibe", order=0)
        Rating.objects.create(
            event=self.event, evaluator=self.participant, target=peer, category=category, score=7
        )

        self.auth_as("admin", "admin-pass-123")
        response = self.client.get("/api/admin/participants/")

        self.assertEqual(response.status_code, 200)
        by_username = {item["username"]: item for item in response.data["results"]}

        self.assertEqual(
            set(by_username["ali"].keys()),
            {
                "id",
                "username",
                "display_name",
                "avatar",
                "event",
                "is_active",
                "last_login",
                "ratings_given_count",
                "ratings_received_count",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(by_username["ali"]["ratings_given_count"], 1)
        self.assertEqual(by_username["ali"]["ratings_received_count"], 0)
        self.assertEqual(by_username["sara"]["ratings_given_count"], 0)
        self.assertEqual(by_username["sara"]["ratings_received_count"], 1)

    def test_newly_created_participant_has_zero_participation_counts(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/participants/",
            {"username": "reza", "display_name": "Reza", "event": self.event.id},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["ratings_given_count"], 0)
        self.assertEqual(response.data["ratings_received_count"], 0)
        self.assertIsNone(response.data["last_login"])
