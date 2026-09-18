from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer

REFRESH_COOKIE_NAME = settings.REFRESH_COOKIE_NAME
REFRESH_COOKIE_PATH = settings.REFRESH_COOKIE_PATH


def _set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        str(refresh_token),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path=REFRESH_COOKIE_PATH,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
    )


def _delete_refresh_cookie(response):
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


def _serialize_current_user(user, request):
    """Shared by /api/auth/login/ and /api/me/ so both ever return the same
    shape — a prior version of this only enriched /api/me/ with `participant`,
    leaving the frontend's post-login state one field short of what a reload
    would then fetch."""
    data = UserSerializer(user).data
    participant = getattr(user, "participant", None)
    if participant is not None:
        from apps.participants.serializers import ParticipantSelfSerializer

        data["participant"] = ParticipantSelfSerializer(participant, context={"request": request}).data
    else:
        data["participant"] = None
    return data


class LoginView(APIView):
    """POST /api/auth/login/

    Accepts username/password, returns an access token + safe user info in
    the JSON body. The refresh token is never put in the response body: it
    is set as an httpOnly cookie so frontend JS can never read or leak it.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        user = serializer.user

        response = Response(
            {
                "access": validated["access"],
                "user": _serialize_current_user(user, request),
            }
        )
        _set_refresh_cookie(response, validated["refresh"])
        return response


class RefreshView(APIView):
    """POST /api/auth/refresh/

    Reads the refresh token from the httpOnly cookie (never from the body),
    issues a new access token, and rotates the refresh cookie.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if not raw_refresh:
            return Response(
                {"detail": "نشست یافت نشد.", "code": "refresh_missing"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(raw_refresh)
            access = str(refresh.access_token)

            if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION"):
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            new_refresh = str(refresh)
        except TokenError:
            response = Response(
                {"detail": "نشست منقضی شده است.", "code": "refresh_invalid"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            _delete_refresh_cookie(response)
            return response

        response = Response({"access": access})
        _set_refresh_cookie(response, new_refresh)
        return response


class LogoutView(APIView):
    """POST /api/auth/logout/

    Blacklists the current refresh token (so it can never be replayed) and
    clears the cookie. Idempotent: missing/invalid cookie still succeeds.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if raw_refresh:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)
        _delete_refresh_cookie(response)
        return response


class CurrentUserView(APIView):
    """GET /api/me/ — the authenticated user's own safe profile, plus their
    participant profile when one exists (docs/API.md describes this endpoint
    as returning "current participant information"; a plain admin/staff
    account with no Participant row gets `"participant": null`)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_serialize_current_user(request.user, request))
