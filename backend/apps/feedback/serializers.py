"""Serializers for the career feedback loop (Phase 12)."""

from rest_framework import serializers

from apps.applications.serializers import OpportunityBriefSerializer

from .models import ApplicationFeedback, FeedbackGap
from .services import gap_recommendations


class FeedbackGapSerializer(serializers.ModelSerializer):
    """One recorded gap with its live learning recommendations."""

    skill_id = serializers.IntegerField(source="skill.id", read_only=True)
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    category = serializers.CharField(source="skill.category", read_only=True)
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackGap
        fields = [
            "id",
            "skill_id",
            "skill_name",
            "category",
            "current_level",
            "required_level",
            "gap_percentage",
            "gap_class",
            "priority",
            "recommended_action",
            "recommendations",
        ]
        read_only_fields = fields

    def get_recommendations(self, obj: FeedbackGap) -> list[dict]:
        return gap_recommendations(obj)


class FeedbackSerializer(serializers.ModelSerializer):
    """Student view of one application's terminal feedback."""

    opportunity = OpportunityBriefSerializer(
        source="application.opportunity", read_only=True
    )
    gaps = FeedbackGapSerializer(many=True, read_only=True)

    class Meta:
        model = ApplicationFeedback
        fields = [
            "id",
            "kind",
            "status",
            "summary",
            "notes",
            "opportunity",
            "gaps",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class FeedbackNotesWriteSerializer(serializers.ModelSerializer):
    """Students may only edit the notes on their own feedback."""

    class Meta:
        model = ApplicationFeedback
        fields = ["notes"]
        extra_kwargs = {"notes": {"required": False, "allow_blank": True}}