from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.events.models import Event
from apps.memories.models import Memory
from apps.memories.services import get_memories_about_me
from apps.ratings.tests import AuthMixin, make_participant

from .models import Report

User = get_user_model()


class MemoryHideViewTests(AuthMixin, APITestCase):
    """POST /api/admin/memories/{id}/hide/ — the minimal admin moderation
    hook docs/ROADMAP.md Phase 7 asks for ("hide memory"). Full admin
    moderation dashboard is Phase 8."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        self.author = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        self.target = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.memory = Memory.objects.create(
            event=self.event, author=self.author, target=self.target, text="یه خاطره"
        )

    def test_requires_authentication(self):
        response = self.client.post(reverse("admin-memory-hide", args=[self.memory.id]))
        self.assertEqual(response.status_code, 401)

    def test_non_admin_participant_is_forbidden(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("admin-memory-hide", args=[self.memory.id]))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_hide_a_memory(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.post(reverse("admin-memory-hide", args=[self.memory.id]))

        self.assertEqual(response.status_code, 200)
        self.memory.refresh_from_db()
        self.assertEqual(self.memory.status, Memory.Status.HIDDEN)

    def test_hiding_nonexistent_memory_is_not_found(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.post(reverse("admin-memory-hide", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_hidden_memory_is_excluded_from_anonymous_retrieval(self):
        self.auth_as("admin", "admin-pass-123")
        self.client.post(reverse("admin-memory-hide", args=[self.memory.id]))

        self.assertNotIn(self.memory, get_memories_about_me(self.target))

        self.client.credentials()
        self.auth_as("ali", "ali-pass-123")
        response = self.client.get(reverse("my-memories"))
        self.assertEqual(response.data["results"], [])


class MemoryRestoreViewTests(AuthMixin, APITestCase):
    """POST /api/admin/memories/{id}/restore/ — docs/PRODUCT.md #9
    "restore content"."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        self.author = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        self.target = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.memory = Memory.objects.create(
            event=self.event,
            author=self.author,
            target=self.target,
            text="یه خاطره",
            status=Memory.Status.HIDDEN,
        )

    def test_requires_authentication(self):
        response = self.client.post(reverse("admin-memory-restore", args=[self.memory.id]))
        self.assertEqual(response.status_code, 401)

    def test_non_admin_participant_is_forbidden(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(reverse("admin-memory-restore", args=[self.memory.id]))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_restore_a_hidden_memory(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.post(reverse("admin-memory-restore", args=[self.memory.id]))

        self.assertEqual(response.status_code, 200)
        self.memory.refresh_from_db()
        self.assertEqual(self.memory.status, Memory.Status.VISIBLE)

    def test_restored_memory_reappears_in_anonymous_retrieval(self):
        self.auth_as("admin", "admin-pass-123")
        self.client.post(reverse("admin-memory-restore", args=[self.memory.id]))

        self.client.credentials()
        self.auth_as("ali", "ali-pass-123")
        response = self.client.get(reverse("my-memories"))
        self.assertEqual(len(response.data["results"]), 1)

    def test_restoring_nonexistent_memory_is_not_found(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.post(reverse("admin-memory-restore", args=[999999]))
        self.assertEqual(response.status_code, 404)


class AdminReportApiTests(AuthMixin, APITestCase):
    """GET /api/admin/reports/ and the resolve/dismiss actions
    (docs/API.md "Admin Moderation", docs/PRODUCT.md #9 "Moderation")."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Graduation 2026", status=Event.Status.OPEN)
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        self.reporter = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.author = make_participant("sara", self.event, display_name="Sara", password="sara-pass-123")
        self.target = make_participant(
            "mohammad", self.event, display_name="Mohammad", password="mohammad-pass-123"
        )
        self.memory = Memory.objects.create(
            event=self.event,
            author=self.author,
            target=self.target,
            text="یه خاطره گزارش‌شده",
            status=Memory.Status.REPORTED,
        )
        self.report = Report.objects.create(
            event=self.event, reporter=self.reporter, memory=self.memory, reason="inappropriate"
        )

    def test_requires_authentication(self):
        response = self.client.get("/api/admin/reports/")
        self.assertEqual(response.status_code, 401)

    def test_non_admin_participant_is_forbidden(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.get("/api/admin/reports/")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_reports_paginated(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.get("/api/admin/reports/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_report_response_never_exposes_reporter_or_author(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.get("/api/admin/reports/")

        item = response.data["results"][0]
        self.assertEqual(set(item.keys()), {"id", "memory", "reason", "status", "created_at", "resolved_at"})
        self.assertEqual(set(item["memory"].keys()), {"id", "text", "status"})
        self.assertEqual(item["memory"]["text"], "یه خاطره گزارش‌شده")

    def test_admin_can_resolve_a_report(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.post(f"/api/admin/reports/{self.report.id}/resolve/")

        self.assertEqual(response.status_code, 200)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.RESOLVED)
        self.assertIsNotNone(self.report.resolved_at)
        # Resolving a report must not silently touch the memory's own status.
        self.memory.refresh_from_db()
        self.assertEqual(self.memory.status, Memory.Status.REPORTED)

    def test_admin_can_dismiss_a_report(self):
        self.auth_as("admin", "admin-pass-123")
        response = self.client.post(f"/api/admin/reports/{self.report.id}/dismiss/")

        self.assertEqual(response.status_code, 200)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.DISMISSED)
        self.assertIsNotNone(self.report.resolved_at)

    def test_non_admin_cannot_resolve_a_report(self):
        self.auth_as("ali", "ali-pass-123")
        response = self.client.post(f"/api/admin/reports/{self.report.id}/resolve/")
        self.assertEqual(response.status_code, 403)
