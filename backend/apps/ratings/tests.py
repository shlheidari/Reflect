from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.events.models import Event
from apps.participants.models import Participant

from .models import Rating, RatingCategory

User = get_user_model()


def make_participant(username, event, display_name=None, is_active=True, password="pass12345!"):
    user = User.objects.create_user(username=username, password=password)
    return Participant.objects.create(
        user=user,
        event=event,
        display_name=display_name or username,
        is_active=is_active,
    )


def make_category(event, key, order=0, active=True, required=True, **extra):
    return RatingCategory.objects.create(
        event=event,
        key=key,
        left_label=extra.pop("left_label", f"{key}-left"),
        right_label=extra.pop("right_label", f"{key}-right"),
        order=order,
        active=active,
        required=required,
        **extra,
    )


class AuthMixin:
    def auth_as(self, username, password):
        login = self.client.post(reverse("auth-login"), {"username": username, "password": password})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")


class RatingCategoryListTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026", status=Event.Status.OPEN)
        self.other_event = Event.objects.create(name="Other Event", status=Event.Status.OPEN)

        self.me = make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")

        self.cat_active_2 = make_category(self.event, "vibe", order=2)
        self.cat_active_1 = make_category(self.event, "shift_behavior", order=1)
        self.cat_inactive = make_category(self.event, "hidden_cat", order=0, active=False)
        self.cat_other_event = make_category(self.other_event, "other_cat", order=0)

    def test_requires_authentication(self):
        response = self.client.get(reverse("rating-category-list"))
        self.assertEqual(response.status_code, 401)

    def test_staff_without_participant_profile_is_forbidden(self):
        User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        self.auth_as("admin", "admin-pass-123")

        response = self.client.get(reverse("rating-category-list"))
        self.assertEqual(response.status_code, 403)

    def test_deactivated_participant_is_forbidden(self):
        self.me.is_active = False
        self.me.save(update_fields=["is_active"])
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("rating-category-list"))
        self.assertEqual(response.status_code, 403)

    def test_list_is_unpaginated_and_excludes_inactive_and_other_events(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("rating-category-list"))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        keys = [item["key"] for item in response.data]
        self.assertEqual(keys, ["shift_behavior", "vibe"])

    def test_list_items_never_expose_event_or_active_fields(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get(reverse("rating-category-list"))

        item = response.data[0]
        self.assertEqual(
            set(item.keys()),
            {"id", "key", "left_label", "right_label", "description", "order", "required"},
        )


class AdminRatingCategoryApiTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026")
        self.other_event = Event.objects.create(name="Other Event")
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")
        self.category = make_category(self.event, "shift_behavior", order=0)

    def test_unauthenticated_is_rejected(self):
        response = self.client.get("/api/admin/rating-categories/")
        self.assertEqual(response.status_code, 401)

    def test_non_admin_participant_is_forbidden(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.get("/api/admin/rating-categories/")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_categories_unpaginated(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.get("/api/admin/rating-categories/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_admin_can_create_category(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/",
            {
                "event": self.event.id,
                "key": "vibe",
                "left_label": "خوش‌فاز",
                "right_label": "بدفاز",
                "order": 1,
                "required": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(RatingCategory.objects.filter(event=self.event, key="vibe").exists())

    def test_cannot_create_duplicate_key_within_same_event(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/",
            {
                "event": self.event.id,
                "key": "shift_behavior",
                "left_label": "x",
                "right_label": "y",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_same_key_allowed_across_different_events(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/",
            {
                "event": self.other_event.id,
                "key": "shift_behavior",
                "left_label": "x",
                "right_label": "y",
            },
        )

        self.assertEqual(response.status_code, 201)

    def test_admin_can_update_labels_and_toggle_active_and_required(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.patch(
            f"/api/admin/rating-categories/{self.category.id}/",
            {"left_label": "خوش‌کشیک ویرایش‌شده", "active": False, "required": False},
        )

        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.left_label, "خوش‌کشیک ویرایش‌شده")
        self.assertFalse(self.category.active)
        self.assertFalse(self.category.required)

    def test_admin_cannot_hard_delete(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.delete(f"/api/admin/rating-categories/{self.category.id}/")

        self.assertEqual(response.status_code, 405)
        self.assertTrue(RatingCategory.objects.filter(pk=self.category.id).exists())


class RatingCategoryReorderTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026")
        self.admin = User.objects.create_user(username="admin", password="admin-pass-123", is_staff=True)
        make_participant("ali", self.event, display_name="Ali", password="ali-pass-123")

        self.cat_a = make_category(self.event, "a", order=0)
        self.cat_b = make_category(self.event, "b", order=1)
        self.cat_c = make_category(self.event, "c", order=2)

    def test_non_admin_forbidden(self):
        self.auth_as("ali", "ali-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/reorder/",
            {"ids": [self.cat_a.id, self.cat_b.id, self.cat_c.id]},
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_reorder_full_set(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/reorder/",
            {"ids": [self.cat_c.id, self.cat_a.id, self.cat_b.id]},
        )

        self.assertEqual(response.status_code, 200)
        self.cat_a.refresh_from_db()
        self.cat_b.refresh_from_db()
        self.cat_c.refresh_from_db()
        self.assertEqual(self.cat_c.order, 0)
        self.assertEqual(self.cat_a.order, 1)
        self.assertEqual(self.cat_b.order, 2)

    def test_reorder_rejects_incomplete_set(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/reorder/",
            {"ids": [self.cat_a.id, self.cat_b.id]},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "incomplete_order")

    def test_reorder_rejects_invalid_id(self):
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/reorder/",
            {"ids": [self.cat_a.id, self.cat_b.id, self.cat_c.id, 999999]},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_ids")

    def test_reorder_rejects_mixed_events(self):
        other_event = Event.objects.create(name="Other Event")
        other_cat = make_category(other_event, "other", order=0)
        self.auth_as("admin", "admin-pass-123")

        response = self.client.post(
            "/api/admin/rating-categories/reorder/",
            {"ids": [self.cat_a.id, self.cat_b.id, self.cat_c.id, other_cat.id]},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "mixed_events")


class SeedRatingCategoriesCommandTests(APITestCase):
    def test_seeds_all_25_categories_for_an_event(self):
        event = Event.objects.create(name="Event 2026")

        call_command("seed_rating_categories")

        self.assertEqual(RatingCategory.objects.filter(event=event).count(), 25)
        shift_behavior = RatingCategory.objects.get(event=event, key="shift_behavior")
        self.assertEqual(shift_behavior.left_label, "خوش‌کشیک")
        self.assertTrue(shift_behavior.required)
        creativity = RatingCategory.objects.get(event=event, key="creativity")
        self.assertFalse(creativity.required)

    def test_seed_is_idempotent(self):
        Event.objects.create(name="Event 2026")

        call_command("seed_rating_categories")
        call_command("seed_rating_categories")

        self.assertEqual(RatingCategory.objects.count(), 25)

    def test_seed_scoped_to_a_single_event_with_event_flag(self):
        event_one = Event.objects.create(name="Event 2026")
        Event.objects.create(name="Other Event")

        call_command("seed_rating_categories", event=event_one.id)

        self.assertEqual(RatingCategory.objects.count(), 25)
        self.assertEqual(RatingCategory.objects.filter(event=event_one).count(), 25)


class RatingSubmissionTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026", status=Event.Status.OPEN)
        self.other_event = Event.objects.create(name="Other Event", status=Event.Status.OPEN)

        self.evaluator = make_participant("ali", self.event, "Ali", password="ali-pass-123")
        self.target = make_participant("reza", self.event, "Reza", password="reza-pass-123")
        self.other_participant = make_participant(
            "sara", self.event, "Sara", password="sara-pass-123"
        )
        self.inactive_target = make_participant(
            "hidden", self.event, "Hidden", is_active=False, password="hidden-pass-123"
        )
        self.other_event_target = make_participant(
            "other", self.other_event, "Other", password="other-pass-123"
        )

        self.required_cat = make_category(self.event, "required_cat", order=0, required=True)
        self.optional_cat = make_category(self.event, "optional_cat", order=1, required=False)
        self.inactive_cat = make_category(
            self.event, "inactive_cat", order=2, required=False, active=False
        )
        self.other_event_cat = make_category(self.other_event, "other_cat", order=0)

        self.auth_as("ali", "ali-pass-123")

    def submit(self, target_id, ratings):
        return self.client.post(
            reverse("rating-submit"), {"target_id": target_id, "ratings": ratings}, format="json"
        )

    def test_score_0_is_accepted(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 0},
                {"category_id": self.optional_cat.id, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Rating.objects.get(evaluator=self.evaluator, category=self.required_cat).score, 0
        )

    def test_score_10_is_accepted(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 10},
                {"category_id": self.optional_cat.id, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Rating.objects.get(evaluator=self.evaluator, category=self.required_cat).score, 10
        )

    def test_score_below_zero_is_rejected(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": -1},
                {"category_id": self.optional_cat.id, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Rating.objects.filter(evaluator=self.evaluator).exists())

    def test_score_above_ten_is_rejected(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 11},
                {"category_id": self.optional_cat.id, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Rating.objects.filter(evaluator=self.evaluator).exists())

    def test_invalid_category_is_rejected(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 8},
                {"category_id": 999999, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_category")
        self.assertFalse(Rating.objects.filter(evaluator=self.evaluator).exists())

    def test_category_from_another_event_is_rejected(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 8},
                {"category_id": self.other_event_cat.id, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_category")

    def test_inactive_category_is_rejected(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 8},
                {"category_id": self.inactive_cat.id, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "inactive_category")
        self.assertFalse(Rating.objects.filter(evaluator=self.evaluator).exists())

    def test_self_rating_is_rejected(self):
        response = self.submit(
            self.evaluator.id,
            [{"category_id": self.required_cat.id, "score": 8}],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "self_rating")

    def test_duplicate_rating_is_rejected(self):
        first = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 8},
                {"category_id": self.optional_cat.id, "score": 5},
            ],
        )
        self.assertEqual(first.status_code, 201)

        second = self.submit(self.target.id, [{"category_id": self.required_cat.id, "score": 3}])
        self.assertEqual(second.status_code, 400)
        self.assertEqual(second.data["code"], "duplicate_rating")
        self.assertEqual(
            Rating.objects.get(evaluator=self.evaluator, category=self.required_cat).score, 8
        )

    def test_duplicate_category_within_one_submission_is_rejected(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 8},
                {"category_id": self.required_cat.id, "score": 3},
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "duplicate_category")

    def test_required_category_missing_is_rejected(self):
        response = self.submit(self.target.id, [{"category_id": self.optional_cat.id, "score": 5}])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "required_category_missing")
        self.assertFalse(Rating.objects.filter(evaluator=self.evaluator).exists())

    def test_closed_event_rejects_submission(self):
        self.event.status = Event.Status.CLOSED
        self.event.save(update_fields=["status"])

        response = self.submit(
            self.target.id,
            [{"category_id": self.required_cat.id, "score": 8}],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "event_closed")

    def test_inactive_target_participant_is_rejected(self):
        response = self.submit(
            self.inactive_target.id,
            [{"category_id": self.required_cat.id, "score": 8}],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_target")

    def test_target_in_another_event_is_rejected(self):
        response = self.submit(
            self.other_event_target.id,
            [{"category_id": self.required_cat.id, "score": 8}],
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_target")

    def test_nonexistent_target_is_rejected(self):
        response = self.submit(999999, [{"category_id": self.required_cat.id, "score": 8}])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_target")

    def test_atomic_submission_rolls_back_on_invalid_item(self):
        response = self.submit(
            self.target.id,
            [
                {"category_id": self.required_cat.id, "score": 8},
                {"category_id": self.optional_cat.id, "score": 5},
                {"category_id": 999999, "score": 5},
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Rating.objects.filter(evaluator=self.evaluator, target=self.target).exists())

    def test_evaluator_identity_never_returned_in_response(self):
        response = self.submit(
            self.target.id,
            [{"category_id": self.required_cat.id, "score": 8}],
        )
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("evaluator", response.data)
        self.assertNotIn("evaluator_id", response.data)
        body_text = str(response.data)
        self.assertNotIn("ali", body_text)

    def test_unauthorized_modification_cannot_touch_another_evaluators_rating(self):
        # ali rates reza first.
        first = self.submit(self.target.id, [{"category_id": self.required_cat.id, "score": 8}])
        self.assertEqual(first.status_code, 201)

        # sara (a different evaluator) tries to PATCH the same target/category —
        # this can only ever create/update *her own* rating, never ali's.
        self.client.credentials()
        self.auth_as("sara", "sara-pass-123")
        self.event.allow_rating_edit = True
        self.event.save(update_fields=["allow_rating_edit"])

        response = self.client.patch(
            reverse("rating-update", args=[self.target.id]),
            {"ratings": [{"category_id": self.required_cat.id, "score": 1}]},
            format="json",
        )

        # Sara has no prior rating of reza, so there's nothing to update yet.
        self.assertEqual(response.status_code, 404)
        alis_rating = Rating.objects.get(evaluator=self.evaluator, category=self.required_cat)
        self.assertEqual(alis_rating.score, 8)
        self.assertFalse(
            Rating.objects.filter(evaluator=self.other_participant, category=self.required_cat).exists()
        )

    def test_update_requires_allow_rating_edit(self):
        first = self.submit(self.target.id, [{"category_id": self.required_cat.id, "score": 8}])
        self.assertEqual(first.status_code, 201)

        response = self.client.patch(
            reverse("rating-update", args=[self.target.id]),
            {"ratings": [{"category_id": self.required_cat.id, "score": 3}]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "rating_edit_not_allowed")

    def test_update_changes_score_when_editing_allowed(self):
        first = self.submit(self.target.id, [{"category_id": self.required_cat.id, "score": 8}])
        self.assertEqual(first.status_code, 201)

        self.event.allow_rating_edit = True
        self.event.save(update_fields=["allow_rating_edit"])

        response = self.client.patch(
            reverse("rating-update", args=[self.target.id]),
            {"ratings": [{"category_id": self.required_cat.id, "score": 2}]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Rating.objects.get(evaluator=self.evaluator, category=self.required_cat).score, 2
        )

    def test_update_without_prior_rating_is_not_found(self):
        self.event.allow_rating_edit = True
        self.event.save(update_fields=["allow_rating_edit"])

        response = self.client.patch(
            reverse("rating-update", args=[self.target.id]),
            {"ratings": [{"category_id": self.required_cat.id, "score": 2}]},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_requires_authentication(self):
        self.client.credentials()
        response = self.submit(self.target.id, [{"category_id": self.required_cat.id, "score": 8}])
        self.assertEqual(response.status_code, 401)


class ParticipantRatingAnnotationTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026", status=Event.Status.OPEN)
        self.me = make_participant("ali", self.event, "Ali", password="ali-pass-123")
        self.other = make_participant("sara", self.event, "Sara", password="sara-pass-123")
        self.third = make_participant("reza", self.event, "Reza", password="reza-pass-123")
        self.category = make_category(self.event, "vibe", order=0)

    def test_rating_count_and_rated_by_me_reflect_real_ratings(self):
        self.auth_as("ali", "ali-pass-123")
        self.client.post(
            reverse("rating-submit"),
            {"target_id": self.other.id, "ratings": [{"category_id": self.category.id, "score": 7}]},
            format="json",
        )
        self.client.credentials()

        self.auth_as("reza", "reza-pass-123")
        self.client.post(
            reverse("rating-submit"),
            {"target_id": self.other.id, "ratings": [{"category_id": self.category.id, "score": 9}]},
            format="json",
        )
        self.client.credentials()

        self.auth_as("ali", "ali-pass-123")
        response = self.client.get(reverse("participant-list"))

        self.assertEqual(response.status_code, 200)
        by_id = {item["id"]: item for item in response.data["results"]}
        self.assertEqual(by_id[self.other.id]["rating_count"], 2)
        self.assertTrue(by_id[self.other.id]["rated_by_me"])
        self.assertEqual(by_id[self.third.id]["rating_count"], 0)
        self.assertFalse(by_id[self.third.id]["rated_by_me"])


class MyResultsTests(AuthMixin, APITestCase):
    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(
            name="Event 2026", status=Event.Status.OPEN, minimum_ratings_for_results=3
        )
        self.other_event = Event.objects.create(name="Other Event", status=Event.Status.OPEN)

        self.me = make_participant("reza", self.event, "Reza", password="reza-pass-123")
        self.evaluators = [
            make_participant(f"ev{i}", self.event, f"Evaluator {i}", password="pass-123456")
            for i in range(4)
        ]

        self.cat_vibe = make_category(
            self.event, "vibe", order=0, left_label="خوش‌فاز", right_label="بدفاز"
        )
        self.cat_shift = make_category(
            self.event, "shift", order=1, left_label="خوش‌کشیک", right_label="بدکشیک"
        )
        self.cat_inactive = make_category(self.event, "hidden", order=2, active=False)
        self.cat_other_event = make_category(self.other_event, "other_cat", order=0)

    def rate(self, evaluator, category, score):
        Rating.objects.create(
            event=self.event, evaluator=evaluator, target=self.me, category=category, score=score
        )

    def test_requires_authentication(self):
        response = self.client.get(reverse("my-results"))
        self.assertEqual(response.status_code, 401)

    def test_no_ratings_yet(self):
        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rating_count"], 0)
        for category in response.data["categories"]:
            self.assertIsNone(category["average"])
            self.assertEqual(category["count"], 0)
            self.assertFalse(category["has_enough_ratings"])

    def test_below_threshold_hides_average_but_shows_count(self):
        self.rate(self.evaluators[0], self.cat_vibe, 8)
        self.rate(self.evaluators[1], self.cat_vibe, 6)  # 2 ratings, default threshold is 3

        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))

        vibe = next(c for c in response.data["categories"] if c["category_id"] == self.cat_vibe.id)
        self.assertIsNone(vibe["average"])
        self.assertEqual(vibe["count"], 2)
        self.assertFalse(vibe["has_enough_ratings"])

    def test_at_threshold_reveals_rounded_average(self):
        self.rate(self.evaluators[0], self.cat_vibe, 8)
        self.rate(self.evaluators[1], self.cat_vibe, 7)
        self.rate(self.evaluators[2], self.cat_vibe, 8)  # avg = 23/3 = 7.666... -> 7.7

        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))

        vibe = next(c for c in response.data["categories"] if c["category_id"] == self.cat_vibe.id)
        self.assertTrue(vibe["has_enough_ratings"])
        self.assertEqual(vibe["count"], 3)
        self.assertEqual(vibe["average"], 7.7)

    def test_rating_count_is_distinct_evaluators_not_rows(self):
        self.rate(self.evaluators[0], self.cat_vibe, 8)
        self.rate(self.evaluators[0], self.cat_shift, 6)  # same evaluator, two categories

        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))
        self.assertEqual(response.data["rating_count"], 1)

    def test_inactive_category_excluded(self):
        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))
        ids = [c["category_id"] for c in response.data["categories"]]
        self.assertNotIn(self.cat_inactive.id, ids)

    def test_other_event_category_excluded(self):
        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))
        ids = [c["category_id"] for c in response.data["categories"]]
        self.assertNotIn(self.cat_other_event.id, ids)

    def test_custom_minimum_threshold_from_event(self):
        self.event.minimum_ratings_for_results = 1
        self.event.save(update_fields=["minimum_ratings_for_results"])
        self.rate(self.evaluators[0], self.cat_vibe, 9)

        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))

        vibe = next(c for c in response.data["categories"] if c["category_id"] == self.cat_vibe.id)
        self.assertTrue(vibe["has_enough_ratings"])
        self.assertEqual(vibe["average"], 9.0)

    def test_ratings_i_gave_others_are_not_my_own_results(self):
        Rating.objects.create(
            event=self.event,
            evaluator=self.me,
            target=self.evaluators[0],
            category=self.cat_vibe,
            score=10,
        )

        self.auth_as("reza", "reza-pass-123")
        response = self.client.get(reverse("my-results"))
        self.assertEqual(response.data["rating_count"], 0)


class RatingDatabaseConstraintTests(APITestCase):
    """docs/ROADMAP.md Phase 9 "Database Security": prove the constraints in
    apps/ratings/models.Rating.Meta are real Postgres-level guarantees, not
    just application-layer validation — by bypassing the service layer
    entirely and calling the ORM directly, the way a future bug (or a raw
    script/migration) could."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(name="Event 2026", status=Event.Status.OPEN)
        self.a = make_participant("a1", self.event, "A1", password="a1-pass-123")
        self.b = make_participant("b1", self.event, "B1", password="b1-pass-123")
        self.category = make_category(self.event, "vibe", order=0)

    def test_db_rejects_self_rating_bypassing_the_service_layer(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Rating.objects.create(
                event=self.event, evaluator=self.a, target=self.a, category=self.category, score=5
            )

    def test_db_rejects_out_of_range_score_bypassing_the_service_layer(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Rating.objects.create(
                event=self.event, evaluator=self.a, target=self.b, category=self.category, score=11
            )

    def test_db_rejects_negative_score_bypassing_the_service_layer(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Rating.objects.create(
                event=self.event, evaluator=self.a, target=self.b, category=self.category, score=-1
            )

    def test_db_rejects_duplicate_rating_bypassing_the_service_layer(self):
        Rating.objects.create(
            event=self.event, evaluator=self.a, target=self.b, category=self.category, score=5
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Rating.objects.create(
                event=self.event, evaluator=self.a, target=self.b, category=self.category, score=7
            )


class MyResultsPrivacyTests(AuthMixin, APITestCase):
    """Dedicated privacy proof (docs/PRIVACY.md #15, docs/ROADMAP.md Phase 6):
    Participant A rates Participant B; B's /api/me/results/ response must
    contain nothing that could identify A."""

    def setUp(self):
        cache.clear()
        self.event = Event.objects.create(
            name="Event 2026", status=Event.Status.OPEN, minimum_ratings_for_results=1
        )
        self.evaluator_a = make_participant("ali", self.event, "Ali Rezaei", password="ali-pass-123")
        self.target_b = make_participant("mohammad", self.event, "Mohammad", password="reza-pass-123")
        self.category = make_category(self.event, "vibe", order=0)

    @staticmethod
    def _collect_keys_and_strings(node, keys, strings):
        if isinstance(node, dict):
            for key, value in node.items():
                keys.append(str(key))
                MyResultsPrivacyTests._collect_keys_and_strings(value, keys, strings)
        elif isinstance(node, list):
            for item in node:
                MyResultsPrivacyTests._collect_keys_and_strings(item, keys, strings)
        elif isinstance(node, str):
            strings.append(node)

    def test_evaluator_identity_never_exposed_in_my_results(self):
        self.auth_as("ali", "ali-pass-123")
        submit_response = self.client.post(
            reverse("rating-submit"),
            {"target_id": self.target_b.id, "ratings": [{"category_id": self.category.id, "score": 8}]},
            format="json",
        )
        self.assertEqual(submit_response.status_code, 201)
        self.client.credentials()

        self.auth_as("mohammad", "reza-pass-123")
        response = self.client.get(reverse("my-results"))
        self.assertEqual(response.status_code, 200)

        keys, strings = [], []
        self._collect_keys_and_strings(response.data, keys, strings)

        for key in keys:
            self.assertNotIn("evaluator", key.lower())

        self.assertNotIn("ali", strings)
        self.assertNotIn("Ali Rezaei", strings)
        self.assertNotIn(str(self.evaluator_a.user_id), strings)

        self.assertEqual(response.data["rating_count"], 1)
