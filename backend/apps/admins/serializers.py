"""Admin serializers for all platform entities."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.assessments.models import Assessment, Option, Question
from apps.careers.models import Career, CareerSkillRequirement
from apps.learning.models import LearningResource
from apps.opportunities.models import Opportunity, OpportunityRequirement
from apps.skills.models import Skill, UserSkill
from apps.students.models import StudentProfile

User = get_user_model()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "full_name", "first_name", "last_name",
            "role", "phone", "is_active", "date_joined",
        ]
        read_only_fields = ["id", "username", "date_joined"]

    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username


class AdminUserCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Role.choices)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_password(self, value):
        try:
            validate_password(value)
        except Exception as exc:
            raise serializers.ValidationError(list(getattr(exc, 'messages', [str(exc)]))) from exc
        return value

    def create(self, validated_data):
        import re
        parts = validated_data.pop("full_name").strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        email = validated_data["email"]
        password = validated_data.pop("password")

        base = re.sub(r"[^a-zA-Z0-9_.]", "", email.split("@")[0])[:30] or "user"
        base = base.lower()
        username, n = base, 1
        while User.objects.filter(username=username).exists():
            suffix = str(n)
            username = f"{base[:30 - len(suffix)]}{suffix}"
            n += 1

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=validated_data.get("role", User.Role.STUDENT),
            phone=validated_data.get("phone", ""),
        )
        user.set_password(password)
        user.save()

        if user.is_student:
            StudentProfile.objects.get_or_create(user=user)
        return user


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------
class AdminSkillSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ["id", "name", "category", "description", "is_active", "user_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_user_count(self, obj) -> int:
        return obj.user_skills.count()


# ---------------------------------------------------------------------------
# Careers
# ---------------------------------------------------------------------------
class AdminCareerRequirementSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = CareerSkillRequirement
        fields = ["id", "skill", "skill_name", "target_level", "importance"]
        read_only_fields = ["id"]


class AdminCareerSerializer(serializers.ModelSerializer):
    requirements = AdminCareerRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Career
        fields = [
            "id", "title", "description", "category", "education",
            "outlook", "salary_range", "domain_keywords", "learning_areas",
            "is_active", "requirements", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# ---------------------------------------------------------------------------
# Assessments
# ---------------------------------------------------------------------------
class AdminOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct", "order"]
        read_only_fields = ["id"]


class AdminQuestionSerializer(serializers.ModelSerializer):
    options = AdminOptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ["id", "text", "marks", "order", "options"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        question = Question.objects.create(**validated_data)
        for opt in options_data:
            Option.objects.create(question=question, **opt)
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if options_data is not None:
            instance.options.all().delete()
            for opt in options_data:
                Option.objects.create(question=instance, **opt)
        return instance


class AdminAssessmentSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id", "title", "description", "skill", "skill_name", "difficulty",
            "duration_minutes", "is_published", "question_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_question_count(self, obj) -> int:
        return obj.questions.count()


class AdminAssessmentDetailSerializer(AdminAssessmentSerializer):
    questions = AdminQuestionSerializer(many=True, read_only=True)

    class Meta(AdminAssessmentSerializer.Meta):
        fields = AdminAssessmentSerializer.Meta.fields + ["questions"]


# ---------------------------------------------------------------------------
# Opportunities
# ---------------------------------------------------------------------------
class AdminOpportunityRequirementSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = OpportunityRequirement
        fields = ["id", "skill", "skill_name", "min_level"]
        read_only_fields = ["id"]


class AdminOpportunitySerializer(serializers.ModelSerializer):
    requirements = AdminOpportunityRequirementSerializer(many=True, read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            "id", "title", "company", "opportunity_type", "description",
            "eligibility", "location", "is_remote", "deadline",
            "application_link", "compensation", "status", "requirements",
            "application_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_application_count(self, obj) -> int:
        return obj.applications.count() if hasattr(obj, "applications") else 0


# ---------------------------------------------------------------------------
# Learning Resources
# ---------------------------------------------------------------------------
class AdminLearningResourceSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = LearningResource
        fields = [
            "id", "title", "description", "skill", "skill_name", "level",
            "type", "url", "estimated_duration_minutes", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
class AdminChangePasswordSerializer(serializers.Serializer):
    """Admin-initiated password change for any user.

    Both fields are write-only so passwords never appear in API responses.
    Django's password validators run on the new password before it is stored.
    """
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({
                "confirm_password": "The two password fields did not match."
            })
        try:
            validate_password(attrs["new_password"])
        except Exception as exc:  # Django password validators
            raise serializers.ValidationError({
                "new_password": list(getattr(exc, "messages", [str(exc)]))
            }) from exc
        return attrs


class AdminAnalyticsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_professors = serializers.IntegerField()
    total_admins = serializers.IntegerField()
    total_skills = serializers.IntegerField()
    total_careers = serializers.IntegerField()
    total_assessments = serializers.IntegerField()
    total_opportunities = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    total_learning_resources = serializers.IntegerField()
    selected_students = serializers.IntegerField()
    active_opportunities = serializers.IntegerField()
    published_assessments = serializers.IntegerField()
    users_by_role = serializers.ListField()
    users_by_month = serializers.ListField()
    popular_skills = serializers.ListField()
    popular_careers = serializers.ListField()
    applications_by_status = serializers.ListField()
    common_skill_gaps = serializers.ListField()
