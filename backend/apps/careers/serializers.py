"""Serializers for the careers app and skill gap analysis."""

from rest_framework import serializers

from apps.skills.models import Skill
from apps.skills.serializers import SkillSerializer

from .models import Career, CareerSkillRequirement


class CareerListSerializer(serializers.ModelSerializer):
    """Catalog entry: metadata plus how many skills the role expects."""

    skill_count = serializers.SerializerMethodField()

    class Meta:
        model = Career
        fields = [
            "id",
            "title",
            "description",
            "category",
            "education",
            "salary_range",
            "learning_areas",
            "skill_count",
        ]
        read_only_fields = fields

    def get_skill_count(self, obj: Career) -> int:
        return obj.requirements.count()


class CareerRequirementSerializer(serializers.ModelSerializer):
    """A career's expectation for one skill."""

    skill = SkillSerializer(read_only=True)

    class Meta:
        model = CareerSkillRequirement
        fields = ["id", "skill", "target_level", "importance"]
        read_only_fields = fields


class CareerDetailSerializer(CareerListSerializer):
    """Full career view with its required skills and target levels."""

    requirements = CareerRequirementSerializer(many=True, read_only=True)

    class Meta(CareerListSerializer.Meta):
        fields = CareerListSerializer.Meta.fields + [
            "outlook",
            "requirements",
        ]


class SkillGapSerializer(serializers.Serializer):
    """One row of the Skill Gap Dashboard."""

    skill_id = serializers.IntegerField()
    skill_name = serializers.CharField()
    category = serializers.CharField()
    current_level = serializers.FloatField()
    required_level = serializers.IntegerField()
    gap_percentage = serializers.FloatField()
    gap_class = serializers.CharField()
    importance = serializers.CharField()
    priority = serializers.CharField()
    recommended_action = serializers.CharField()


class GapAnalysisSerializer(serializers.Serializer):
    """Full gap analysis for one student against one career."""

    career = CareerListSerializer()
    readiness_percentage = serializers.FloatField()
    gaps = SkillGapSerializer(many=True)
    summary = serializers.DictField()


# ---------------------------------------------------------------------------
# Admin CRUD (career catalog management; UI lands in Phase 7)
# ---------------------------------------------------------------------------


class AdminCareerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = [
            "id",
            "title",
            "description",
            "category",
            "education",
            "outlook",
            "salary_range",
            "domain_keywords",
            "learning_areas",
            "is_active",
        ]
        extra_kwargs = {"id": {"read_only": True}}


class AdminRequirementWriteSerializer(serializers.ModelSerializer):
    skill = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(is_active=True)
    )

    class Meta:
        model = CareerSkillRequirement
        fields = ["id", "skill", "target_level", "importance"]
        extra_kwargs = {
            "id": {"read_only": True},
            "target_level": {"min_value": 0, "max_value": 100},
        }

    def validate(self, attrs):
        career = self.context.get("career")
        skill = attrs.get("skill") or getattr(self.instance, "skill", None)
        if career and skill and career.requirements.filter(skill=skill).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                {"skill": "This skill is already a requirement for the career."}
            )
        return attrs