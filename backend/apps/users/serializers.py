"""Serializers for authentication and user management."""

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.students.models import StudentProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public view of a user (used by /auth/me and dashboards)."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "role",
            "phone",
            "avatar",
        ]
        read_only_fields = ["id", "username"]

    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username

    def validate_phone(self, value: str) -> str:
        """Limit phone field length to prevent abuse."""
        if len(value) > 20:
            raise serializers.ValidationError("Phone number must be at most 20 characters.")
        return value


class RegisterSerializer(serializers.Serializer):
    """Self-service registration for students and professors.

    Admin accounts are never self-serve: they are created by an existing
    admin (Django admin) or the seed command.
    """

    full_name = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=[User.Role.STUDENT, User.Role.PROFESSOR])
    college = serializers.CharField(max_length=200, required=False, allow_blank=True)
    course = serializers.CharField(max_length=150, required=False, allow_blank=True)
    year = serializers.IntegerField(min_value=1, max_value=6, required=False, allow_null=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except django_exceptions.ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate(self, attrs):
        if attrs.get("role") == User.Role.STUDENT:
            missing = [
                field
                for field in ("college", "course", "year")
                if not attrs.get(field)
            ]
            if missing:
                raise serializers.ValidationError(
                    {
                        field: "This field is required for student accounts."
                        for field in missing
                    }
                )
        return attrs

    def create(self, validated_data):
        parts = validated_data.pop("full_name").strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        email = validated_data["email"]
        password = validated_data.pop("password")

        user = User(
            username=self._unique_username(email),
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=validated_data.pop("role"),
        )
        user.set_password(password)  # hashed by Django's default (PBKDF2)
        user.save()

        if user.is_student:
            StudentProfile.objects.create(
                user=user,
                college=validated_data.get("college", ""),
                course=validated_data.get("course", ""),
                year=validated_data.get("year"),
            )
        return user

    @staticmethod
    def _unique_username(email: str) -> str:
        base = re.sub(r"[^a-zA-Z0-9_.]", "", email.split("@")[0])[:30] or "user"
        base = base.lower()
        username, n = base, 1
        while User.objects.filter(username=username).exists():
            suffix = str(n)
            username = f"{base[: 30 - len(suffix)]}{suffix}"
            n += 1
        return username


class LoginSerializer(serializers.Serializer):
    """Accepts an email address or username plus password.

    Returns fresh JWT tokens plus the user record (avoids an extra
    round-trip to /auth/me after signing in).
    """

    email = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        identifier = attrs.get("email", "").strip()
        password = attrs.get("password", "")
        user = User.objects.filter(Q(email__iexact=identifier) | Q(username=identifier)).first()

        if user is None or not user.is_active or not user.check_password(password):
            raise serializers.ValidationError(
                "Unable to log in with the provided credentials."
            )

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except django_exceptions.ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value