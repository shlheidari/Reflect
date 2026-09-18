from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Safe, participant-facing user representation.

    Deliberately excludes password/hash and any other sensitive field —
    only ever add fields here that are safe to return to the user themselves.
    """

    class Meta:
        model = User
        fields = ("id", "username", "is_staff")
        read_only_fields = fields
