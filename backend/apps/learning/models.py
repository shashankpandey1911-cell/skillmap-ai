"""Learning content and roadmap tracking (Phase 8).

LearningResource  — the curated learning-content catalog. Each row is a
                    concrete item (course, video, doc, practice exercise,
                    project or quiz) tagged to one catalog skill, so roadmap
                    generation has real, database-backed material to draw
                    from instead of fabricated text.
ResourceCompletion— a student's "done" flag for one resource. Roadmap
                    progress percentages are computed live from these rows
                    (completed ÷ recommended for the chosen career).

The roadmap itself is not stored: apps/learning/services.py derives it from
the Phase 6 skill-gap engine each time a student asks, so it stays honest as
skills, resources and assessments change.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.skills.models import Skill


class LearningResource(models.Model):
    """A concrete learning item a student can work through."""

    class Level(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    class Type(models.TextChoices):
        COURSE = "COURSE", "Course"
        VIDEO = "VIDEO", "Video"
        DOCUMENTATION = "DOCUMENTATION", "Documentation"
        PRACTICE = "PRACTICE", "Practice"
        PROJECT = "PROJECT", "Project"
        QUIZ = "QUIZ", "Quiz"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="learning_resources"
    )
    level = models.CharField(
        max_length=20, choices=Level.choices, default=Level.INTERMEDIATE
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.COURSE)
    url = models.URLField(blank=True)
    estimated_duration_minutes = models.PositiveSmallIntegerField(
        default=30, validators=[MinValueValidator(1)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["skill__name", "type", "level", "title"]

    def __str__(self) -> str:
        return self.title


class ResourceCompletion(models.Model):
    """A student marking one learning resource as completed."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resource_completions",
    )
    resource = models.ForeignKey(
        LearningResource, on_delete=models.CASCADE, related_name="completions"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "resource"], name="unique_resource_completion"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} ✓ {self.resource.title}"
