"""Serializers for opportunities (Phase 9)."""

from rest_framework import serializers

from apps.skills.models import Skill
from apps.skills.serializers import SkillSerializer

from .models import Opportunity, OpportunityRequirement
from .services import opportunity_match


class OpportunityRequirementSerializer(serializers.ModelSerializer):
    """Read view of one required skill (nested under an opportunity)."""

    skill = SkillSerializer(read_only=True)

    class Meta:
        model = OpportunityRequirement
        fields = ["id", "skill", "min_level"]
        read_only_fields = fields


class OpportunityListSerializer(serializers.ModelSerializer):
    """Student-facing listing / detail / recommendation payload.

    The smart-match fields are computed by the view-provided match inputs
    (scores, profile, projects). Callers without a target student (e.g. a
    professor just browsing the catalog) get null match fields.
    """

    skill_names = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "company",
            "opportunity_type",
            "description",
            "eligibility",
            "location",
            "is_remote",
            "deadline",
            "compensation",
            "application_link",
            "created_at",
            "skill_names",
        ]
        read_only_fields = fields

    def get_skill_names(self, obj: Opportunity) -> list[str]:
        return [req.skill.name for req in obj.requirements.all()]

    def to_representation(self, instance: Opportunity):
        data = super().to_representation(instance)
        inputs = self.context.get("match_inputs")
        if inputs is None:
            data.update(
                {
                    "match_percentage": None,
                    "matching_skills": [],
                    "missing_skills": [],
                    "matched_requirements": 0,
                    "total_requirements": 0,
                    "breakdown": None,
                    "explanation": None,
                    "recommended_next_steps": [],
                }
            )
            return data

        scores, profile, projects = inputs
        match = opportunity_match(
            instance, list(instance.requirements.all()), scores, profile, projects
        )
        data.update(
            {
                "match_percentage": match.match_percentage,
                "matching_skills": match.matching_skills,
                "missing_skills": match.missing_skills,
                "matched_requirements": match.matched_requirements,
                "total_requirements": match.total_requirements,
                "breakdown": {
                    "skills": match.skills_score,
                    "profile": match.profile_score,
                    "projects": match.projects_score,
                },
                "explanation": match.explanation,
                "recommended_next_steps": match.recommended_next_steps,
            }
        )
        return data


class OpportunityDetailSerializer(OpportunityListSerializer):
    """Full view: per-skill requirement breakdown with the student's own
    level against each minimum. The smart-match fields come from the list
    serializer (eligibility/application_link/created_at are plain fields)."""

    requirements = serializers.SerializerMethodField()

    class Meta(OpportunityListSerializer.Meta):
        fields = OpportunityListSerializer.Meta.fields + ["requirements"]

    def get_requirements(self, obj: Opportunity) -> list[dict]:
        scores = None
        inputs = self.context.get("match_inputs")
        if inputs is not None:
            scores = inputs[0]
        scores = scores or {}
        rows = []
        for req in obj.requirements.all():
            my_level = round(float(scores.get(req.skill_id, 0.0)), 1)
            rows.append(
                {
                    "id": req.id,
                    "skill": SkillSerializer(req.skill).data,
                    "min_level": req.min_level,
                    "my_level": my_level,
                    "met": req.min_level <= 0 or my_level >= req.min_level,
                }
            )
        return rows


# ---------------------------------------------------------------------------
# Admin CRUD (opportunity management; the UI lands in a later phase)
# ---------------------------------------------------------------------------


class AdminOpportunityDetailSerializer(serializers.ModelSerializer):
    """Full catalog row for the admin UI: everything, with requirements."""

    requirements = OpportunityRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "company",
            "opportunity_type",
            "description",
            "eligibility",
            "location",
            "is_remote",
            "deadline",
            "application_link",
            "compensation",
            "status",
            "created_at",
            "requirements",
        ]
        read_only_fields = fields


class AdminOpportunityWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "company",
            "opportunity_type",
            "description",
            "eligibility",
            "location",
            "is_remote",
            "deadline",
            "application_link",
            "compensation",
            "status",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "title": {"required": True},
            "company": {"required": True},
            "opportunity_type": {"required": True},
        }


class AdminRequirementWriteSerializer(serializers.ModelSerializer):
    skill = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(is_active=True)
    )

    class Meta:
        model = OpportunityRequirement
        fields = ["id", "skill", "min_level"]
        extra_kwargs = {
            "id": {"read_only": True},
            "min_level": {"min_value": 0, "max_value": 100},
        }

    def validate(self, attrs):
        opportunity = self.context.get("opportunity")
        skill = attrs.get("skill") or getattr(self.instance, "skill", None)
        if opportunity and skill and opportunity.requirements.filter(skill=skill).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                {"skill": "This skill is already a requirement for the opportunity."}
            )
        return attrs
