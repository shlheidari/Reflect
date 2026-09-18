from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        # DRF's ScopedRateThrottle state lives in the default cache; without
        # clearing it, throttle counts leak between tests and between runs.
        cache.clear()
        self.password = "a-strong-password-123"
        self.user = User.objects.create_user(username="ali", password=self.password)

    def _login(self, username, password):
        return self.client.post(
            reverse("auth-login"), {"username": username, "password": password}
        )

    def test_valid_login_returns_access_token_and_safe_user_and_sets_refresh_cookie(self):
        response = self._login("ali", self.password)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["username"], "ali")
        self.assertNotIn("password", response.data["user"])
        self.assertNotIn("refresh", response.data)

        cookie = response.cookies.get("refresh_token")
        self.assertIsNotNone(cookie)
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")

    def test_invalid_password_is_rejected(self):
        response = self._login("ali", "totally-wrong-password")

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)

    def test_unknown_username_gives_same_generic_error_as_wrong_password(self):
        wrong_password = self._login("ali", "totally-wrong-password")
        unknown_user = self._login("does-not-exist", "whatever-password")

        self.assertEqual(wrong_password.status_code, unknown_user.status_code)
        self.assertEqual(wrong_password.data["code"], unknown_user.data["code"])

    def test_disabled_account_cannot_log_in(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self._login("ali", self.password)

        self.assertEqual(response.status_code, 401)

    def test_login_is_rate_limited(self):
        for _ in range(5):
            response = self._login("ali", "wrong-password")
            self.assertEqual(response.status_code, 401)

        throttled = self._login("ali", "wrong-password")
        self.assertEqual(throttled.status_code, 429)

    def test_current_user_requires_authentication(self):
        response = self.client.get(reverse("current-user"))
        self.assertEqual(response.status_code, 401)

    def test_current_user_returns_safe_profile_when_authenticated(self):
        login = self._login("ali", self.password)
        access = login.data["access"]

        response = self.client.get(
            reverse("current-user"), HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "ali")
        self.assertNotIn("password", response.data)

    def test_refresh_issues_new_access_token_and_rotates_cookie(self):
        login = self._login("ali", self.password)
        old_refresh_cookie = login.cookies["refresh_token"].value
        self.client.cookies["refresh_token"] = old_refresh_cookie

        response = self.client.post(reverse("auth-refresh"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        new_refresh_cookie = response.cookies["refresh_token"].value
        self.assertNotEqual(new_refresh_cookie, old_refresh_cookie)

    def test_refresh_without_cookie_is_rejected(self):
        response = self.client.post(reverse("auth-refresh"))
        self.assertEqual(response.status_code, 401)

    def test_rotated_refresh_token_cannot_be_reused(self):
        login = self._login("ali", self.password)
        old_refresh_cookie = login.cookies["refresh_token"].value
        self.client.cookies["refresh_token"] = old_refresh_cookie

        first_refresh = self.client.post(reverse("auth-refresh"))
        self.assertEqual(first_refresh.status_code, 200)

        # Replay the now-rotated-away original refresh token.
        self.client.cookies["refresh_token"] = old_refresh_cookie
        replay = self.client.post(reverse("auth-refresh"))

        self.assertEqual(replay.status_code, 401)

    def test_logout_blacklists_refresh_token_and_clears_cookie(self):
        login = self._login("ali", self.password)
        refresh_cookie = login.cookies["refresh_token"].value
        self.client.cookies["refresh_token"] = refresh_cookie

        logout = self.client.post(reverse("auth-logout"))
        self.assertEqual(logout.status_code, 204)
        self.assertEqual(logout.cookies["refresh_token"].value, "")

        self.client.cookies["refresh_token"] = refresh_cookie
        response = self.client.post(reverse("auth-refresh"))
        self.assertEqual(response.status_code, 401)

    def test_logout_without_a_session_still_succeeds(self):
        response = self.client.post(reverse("auth-logout"))
        self.assertEqual(response.status_code, 204)
