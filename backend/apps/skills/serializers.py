"""Serializers for the skills app."""

from rest_framework import serializers

from .models import Skill, UserSkill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "category", "description"]
        read_only_fields = fields


class UserSkillWriteSerializer(serializers.ModelSerializer):
    """Student-facing write payload.

    assessment_score is intentionally absent: only the assessment engine
    (a later phase) can set objective scores, so students cannot fake them.
    """

    skill = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.filter(is_active=True))

    class Meta:
        model = UserSkill
        fields = ["skill", "proficiency_level", "experience_level"]
        extra_kwargs = {
            "proficiency_level": {"min_value": 1, "max_value": 5},
        }

    def validate(self, attrs):
        user = self.context["request"].user
        skill = attrs.get("skill") or getattr(self.instance, "skill", None)
        if skill and UserSkill.objects.filter(user=user, skill=skill).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError(
                {"skill": "You have already added this skill."}
            )
        return attrs


class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    score = serializers.SerializerMethodField()

    class Meta:
        model = UserSkill
        fields = [
            "id",
            "skill",
            "proficiency_level",
            "experience_level",
            "assessment_score",
            "score",
            "updated_at",
        ]
        read_only_fields = ["id", "assessment_score", "score", "updated_at"]

    def get_score(self, obj: UserSkill) -> float:
        return round(obj.score, 1)