"""User model with role-based access (student / professor / admin).

Defined at architecture time because switching AUTH_USER_MODEL later
requires a painful data migration.
"""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


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