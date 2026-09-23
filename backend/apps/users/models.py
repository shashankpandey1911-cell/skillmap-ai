"""User model with role-based access (student / professor / admin).

Defined at architecture time because switching AUTH_USER_MODEL later
requires a painful data migration.
"""

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Platform user. `role` decides which dashboards and APIs are reachable."""

    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        PROFESSOR = "PROFESSOR", "Professor"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    # Default True keeps pre-existing/seeded/admin-created users verified;
    # self-registration explicitly sets this False until the email link is used.
    is_email_verified = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.avatar:
            # Validate file size (max 5MB)
            if self.avatar.size > 5 * 1024 * 1024:
                raise ValidationError("Avatar file size must be under 5MB.")
            # Validate file type
            valid_types = ["image/jpeg", "image/png", "image/webp"]
            if hasattr(self.avatar, "content_type") and self.avatar.content_type not in valid_types:
                raise ValidationError("Avatar must be a JPEG, PNG, or WebP image.")

    def __str__(self) -> str:
        return self.username

    # Convenience predicates used by permissions and serializers.
    @property
    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT

    @property
    def is_professor(self) -> bool:
        return self.role == self.Role.PROFESSOR

    @property
    def is_admin_user(self) -> bool:
        return self.role == self.Role.ADMIN


class EmailVerificationToken(models.Model):
    """Single-use, time-limited token backing the emailed verification link."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_verification_tokens"
    )
    # SHA-256 hex digest of the emailed token — the raw token is never stored.
    token = models.CharField(max_length=64, unique=True, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "email verification token"

    def __str__(self) -> str:
        return f"Verification token for {self.user.username}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @classmethod
    def issue(cls, user: "User") -> tuple["EmailVerificationToken", str]:
        """Create a fresh token, invalidating any outstanding unused ones.

        Returns (record, raw_token): only the SHA-256 digest is persisted,
        so a database leak cannot be replayed against the verify endpoint.
        """
        cls.objects.filter(user=user, used_at__isnull=True).delete()
        raw_token = secrets.token_urlsafe(32)
        obj = cls.objects.create(
            user=user,
            token=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=timezone.now()
            + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_HOURS),
        )
        return obj, raw_token
