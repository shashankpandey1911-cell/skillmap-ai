"""Serializers for the applications app (Phase 11)."""

from rest_framework import serializers

from apps.opportunities.models import Opportunity

from .models import Application


class OpportunityBriefSerializer(serializers.ModelSerializer):
    """The posting an application belongs to (deadline included so the
    student can always see how much time remains)."""

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "company",
            "opportunity_type",
            "location",
            "is_remote",
            "deadline",
            "compensation",
        ]
        read_only_fields = fields


class ApplicationSerializer(serializers.ModelSerializer):
    """Student view of one application."""

    opportunity = OpportunityBriefSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "opportunity",
            "status",
            "notes",
            "interview_date",
            "applied_at",
            "updated_at",
        ]
        read_only_fields = fields


class StudentNotesWriteSerializer(serializers.ModelSerializer):
    """Students may only edit the notes on their own application."""

    class Meta:
        model = Application
        fields = ["notes"]
        extra_kwargs = {"notes": {"required": False, "allow_blank": True}}


class AdminApplicationWriteSerializer(serializers.ModelSerializer):
    """Admins drive the pipeline: status, interview date and shared notes."""

    class Meta:
        model = Application
        fields = ["status", "interview_date", "notes"]
        extra_kwargs = {
            "status": {"required": False},
            "notes": {"required": False, "allow_blank": True},
            "interview_date": {"required": False},
        }


class AdminApplicationListSerializer(ApplicationSerializer):
    """Admin/staff list view: which student the application belongs to."""

    student = serializers.SerializerMethodField()

    class Meta(ApplicationSerializer.Meta):
        fields = ApplicationSerializer.Meta.fields + ["student"]

    def get_student(self, obj: Application) -> dict:
        user = obj.student
        return {
            "id": user.id,
            "name": user.get_full_name() or user.username,
            "email": user.email,
        }


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Applying: the student names the posting they are applying to."""

    opportunity = serializers.PrimaryKeyRelatedField(
        queryset=Opportunity.objects.all()
    )

    class Meta:
        model = Application
        fields = ["opportunity"]
