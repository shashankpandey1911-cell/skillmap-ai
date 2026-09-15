"""Serializers for the learning app (Phase 8)."""

from rest_framework import serializers

from apps.skills.models import Skill
from apps.skills.serializers import SkillSerializer

from .models import LearningResource


class LearningResourceSerializer(serializers.ModelSerializer):
    """Student-facing learning resource with the student's completion flag."""

    skill = SkillSerializer(read_only=True)
    completed = serializers.SerializerMethodField()

    class Meta:
        model = LearningResource
        fields = [
            "id",
            "title",
            "description",
            "skill",
            "level",
            "type",
            "url",
            "estimated_duration_minutes",
            "completed",
        ]
        read_only_fields = fields

    def get_completed(self, obj: LearningResource) -> bool:
        return obj.id in (self.context.get("completed_ids") or set())


class LearningResourceListSerializer(serializers.ModelSerializer):
    """Catalog entry with the skill id/name flattened for list filters."""

    skill_id = serializers.IntegerField(source="skill.id", read_only=True)
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    completed = serializers.SerializerMethodField()

    class Meta:
        model = LearningResource
        fields = [
            "id",
            "title",
            "description",
            "skill_id",
            "skill_name",
            "level",
            "type",
            "url",
            "estimated_duration_minutes",
            "completed",
        ]
        read_only_fields = fields

    def get_completed(self, obj: LearningResource) -> bool:
        return obj.id in (self.context.get("completed_ids") or set())


# ---------------------------------------------------------------------------
# Admin CRUD
# ---------------------------------------------------------------------------


class AdminLearningResourceWriteSerializer(serializers.ModelSerializer):
    skill = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(is_active=True)
    )

    class Meta:
        model = LearningResource
        fields = [
            "id",
            "title",
            "description",
            "skill",
            "level",
            "type",
            "url",
            "estimated_duration_minutes",
            "is_active",
        ]
        extra_kwargs = {"id": {"read_only": True}}
