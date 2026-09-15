"""Assessment engine models.

Assessment      — a published test for one catalog skill (difficulty, duration).
Question        — belongs to an assessment; carries text and marks.
Option          — an answer choice on a question. `is_correct` is admin-only
                  and is never serialized to students before submission.
StudentAttempt  — one student's run at an assessment (IN_PROGRESS / SUBMITTED).
StudentAnswer   — a snapshot of what the student picked for a question.
AssessmentResult— immutable result snapshot written at submission time,
                  including improvement suggestions.

Scoring lives in apps/core/services/scoring.py; the submission flow (scoring +
writing results + updating the student's skill score) lives in services.py.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.skills.models import Skill


class Assessment(models.Model):
    """A test targeting one catalog skill."""

    class Difficulty(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
        EXPERT = "EXPERT", "Expert"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    skill = models.ForeignKey(
        Skill, on_delete=models.PROTECT, related_name="assessments"
    )
    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices, default=Difficulty.INTERMEDIATE
    )
    duration_minutes = models.PositiveSmallIntegerField(
        default=10, validators=[MinValueValidator(1)]
    )
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assessments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    """A single question inside an assessment."""

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField()
    marks = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.text[:60]


class Option(models.Model):
    """An answer choice on a question."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.text[:60]


class StudentAttempt(models.Model):
    """One student's run at an assessment."""

    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        SUBMITTED = "SUBMITTED", "Submitted"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.PROTECT, related_name="attempts"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.IN_PROGRESS
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    correct_count = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            # A student has at most one in-progress attempt per assessment;
            # once submitted, fresh attempts are free (retakes allowed).
            models.UniqueConstraint(
                fields=["user", "assessment"],
                condition=Q(status="IN_PROGRESS"),
                name="unique_inprogress_attempt_per_assessment",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.assessment.title} ({self.status})"


class StudentAnswer(models.Model):
    """A snapshot of the option a student chose for a question.

    `selected_option` may be cleared later (SET_NULL) without corrupting the
    stored `is_correct` result.
    """

    attempt = models.ForeignKey(
        StudentAttempt, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="student_answers"
    )
    selected_option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"], name="unique_answer_per_attempt_question"
            )
        ]

    def __str__(self) -> str:
        return f"Q{self.question_id} on attempt {self.attempt_id}"


class AssessmentResult(models.Model):
    """Immutable result written when an attempt is submitted."""

    attempt = models.OneToOneField(
        StudentAttempt, on_delete=models.CASCADE, related_name="result"
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="results"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    correct_count = models.PositiveSmallIntegerField()
    total_questions = models.PositiveSmallIntegerField()
    improvement_suggestions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.assessment.title} → {self.score}%"
