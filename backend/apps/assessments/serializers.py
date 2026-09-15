"""Serializers for the assessment engine.

Correct-answer discipline:
    - Public/student serializers never expose `is_correct` before submission
      (options carry only id/text/order).
    - Admin serializers carry full option data including `is_correct` and are
      admin-only.
    - After submission, AssessmentResultSerializer exposes the review, which
      is when the student is allowed to see what was correct.
"""

from rest_framework import serializers

from apps.skills.models import Skill
from apps.skills.serializers import SkillSerializer

from .models import Assessment, AssessmentResult, Option, Question
from .services import build_review


class AssessmentPublicSerializer(serializers.ModelSerializer):
    """Student-facing assessment metadata (never includes questions)."""

    skill = SkillSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()
    my_last_score = serializers.SerializerMethodField()
    my_attempts = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "title",
            "description",
            "skill",
            "difficulty",
            "duration_minutes",
            "question_count",
            "my_last_score",
            "my_attempts",
        ]

    def get_question_count(self, obj: Assessment) -> int:
        return obj.questions.count()

    def get_my_last_score(self, obj: Assessment) -> float | None:
        last = (self.context.get("last_scores") or {}).get(obj.id)
        return float(last) if last is not None else None

    def get_my_attempts(self, obj: Assessment) -> int:
        return (self.context.get("attempt_counts") or {}).get(obj.id, 0)


class OptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "order"]


class QuestionPublicSerializer(serializers.ModelSerializer):
    """A question visible to a student mid-attempt: no correct answers."""

    options = OptionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "marks", "order", "options"]


class SubmitAttemptSerializer(serializers.Serializer):
    """Validates the payload shape; semantic checks happen in the service."""

    attempt_id = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.DictField(), allow_empty=False
    )


class AssessmentResultSerializer(serializers.ModelSerializer):
    """Immutable result + post-submission review (safe only after submit)."""

    submitted_at = serializers.DateTimeField(source="created_at", read_only=True)
    assessment = AssessmentPublicSerializer(read_only=True)
    review = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentResult
        fields = [
            "id",
            "score",
            "correct_count",
            "total_questions",
            "submitted_at",
            "improvement_suggestions",
            "assessment",
            "review",
        ]

    def get_review(self, obj: AssessmentResult):
        return build_review(obj.attempt)

    def get_score(self, obj: AssessmentResult) -> float:
        return float(obj.score)


# ---------------------------------------------------------------------------
# Admin CRUD (full option data, including correct answers)
# ---------------------------------------------------------------------------


class OptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct", "order"]
        extra_kwargs = {"id": {"read_only": True}}


class AdminAssessmentReadSerializer(serializers.ModelSerializer):
    """Admin list/detail view of an assessment with its question count."""

    skill = SkillSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "title",
            "description",
            "skill",
            "difficulty",
            "duration_minutes",
            "is_published",
            "question_count",
        ]

    def get_question_count(self, obj: Assessment) -> int:
        return obj.questions.count()


class AdminQuestionReadSerializer(serializers.ModelSerializer):
    """Admin view of a question: options expose `is_correct`."""

    options = OptionWriteSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "marks", "order", "options"]


class AdminQuestionWriteSerializer(serializers.ModelSerializer):
    """Create/update a question together with its options.

    Accepts nested options; enforces 2-6 options with exactly one correct.
    """

    options = OptionWriteSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "marks", "order", "options"]
        extra_kwargs = {"id": {"read_only": True}}

    def validate_options(self, options):
        if not 2 <= len(options) <= 6:
            raise serializers.ValidationError(
                "A question needs between 2 and 6 options."
            )
        correct = [o for o in options if o.get("is_correct")]
        if len(correct) != 1:
            raise serializers.ValidationError(
                "Exactly one option must be marked as correct."
            )
        texts = [o.get("text", "").strip() for o in options]
        if any(not t for t in texts):
            raise serializers.ValidationError("Option text cannot be empty.")
        if len({t.lower() for t in texts}) != len(texts):
            raise serializers.ValidationError("Options must be unique.")
        return options

    def create(self, validated_data):
        options = validated_data.pop("options")
        question = Question.objects.create(**validated_data)
        self._save_options(question, options)
        return question

    def update(self, instance, validated_data):
        options = validated_data.pop("options", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if options is not None:
            instance.options.all().delete()
            self._save_options(instance, options)
        return instance

    @staticmethod
    def _save_options(question, options):
        Option.objects.bulk_create(
            [Option(question=question, **opt) for opt in options]
        )


class AdminAssessmentWriteSerializer(serializers.ModelSerializer):
    skill = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(is_active=True)
    )

    class Meta:
        model = Assessment
        fields = [
            "id",
            "title",
            "description",
            "skill",
            "difficulty",
            "duration_minutes",
            "is_published",
        ]
        extra_kwargs = {"id": {"read_only": True}}
