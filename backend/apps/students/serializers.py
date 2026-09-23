"""Serializers for the students app."""

from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Certification, Project, StudentProfile

_PROFILE_FIELDS = [
    "college",
    "course",
    "branch",
    "year",
    "cgpa",
    "semester",
    "achievements",
    "career_goal",
    "preferred_domain",
    "interests",
    "about",
    "linkedin_url",
    "github_url",
]


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = _PROFILE_FIELDS


class StudentProfileUpdateSerializer(serializers.Serializer):
    """Flat editor for the whole profile: user fields + profile fields.

    Accepts any subset (partial=True) and writes to both the User and the
    StudentProfile rows.
    """

    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    college = serializers.CharField(max_length=200, required=False, allow_blank=True)
    course = serializers.CharField(max_length=150, required=False, allow_blank=True)
    branch = serializers.CharField(max_length=150, required=False, allow_blank=True)
    year = serializers.IntegerField(min_value=1, max_value=6, required=False, allow_null=True)
    cgpa = serializers.DecimalField(
        max_digits=4, decimal_places=2, min_value=0, max_value=10, required=False, allow_null=True
    )
    semester = serializers.IntegerField(min_value=1, max_value=10, required=False, allow_null=True)
    achievements = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    career_goal = serializers.CharField(max_length=300, required=False, allow_blank=True)
    preferred_domain = serializers.CharField(max_length=150, required=False, allow_blank=True)
    interests = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)
    github_url = serializers.URLField(required=False, allow_blank=True)

    def update(self, instance: StudentProfile, validated_data):
        user = instance.user
        for field in ("first_name", "last_name", "phone"):
            if field in validated_data:
                setattr(user, field, validated_data[field])
        user.save(update_fields=["first_name", "last_name", "phone"])
        for field in _PROFILE_FIELDS:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "technologies",
            "github_url",
            "demo_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = [
            "id",
            "name",
            "provider",
            "issued_date",
            "credential_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# Re-exported for views that need the account serializer.
__all__ = [
    "CertificationSerializer",
    "ProjectSerializer",
    "StudentProfileSerializer",
    "StudentProfileUpdateSerializer",
    "UserSerializer",
]
