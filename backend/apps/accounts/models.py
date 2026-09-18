from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model.

    Kept as a plain AbstractUser subclass for now so AUTH_USER_MODEL is
    correct from the start; role/participant-specific fields are added in
    Phase 2 (Authentication) and Phase 3 (Event and Participants).
    """

    pass
