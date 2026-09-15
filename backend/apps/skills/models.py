"""Skill catalog and per-student skill records.

Skill          — master catalog, one per unique skill name, grouped into
                 the nine categories used across the app.
UserSkill      — a student's own record for a skill: self-rated proficiency
                 (1-5), experience level, and (later) a 0-100 assessment
                 score produced by the assessment engine.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Skill(models.Model):
    """Master skill catalog entry."""

    class Category(models.TextChoices):
        PROGRAMMING = "Programming", "Programming"
        WEB_DEVELOPMENT = "Web Development", "Web Development"
        DATABASE = "Database", "Database"
        CLOUD = "Cloud", "Cloud"
        AI_ML = "AI/ML", "AI/ML"
        DATA_SCIENCE = "Data Science", "Data Science"
        TOOLS = "Tools", "Tools"
        SOFT_SKILLS = "Soft Skills", "Soft Skills"
        OTHER = "Other", "Other"

    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=50, choices=Category.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserSkill(models.Model):
    """A student's skill record, linked to a catalog Skill."""

    class ExperienceLevel(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
        EXPERT = "EXPERT", "Expert"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_skills",
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="user_skills")
    proficiency_level = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    experience_level = models.CharField(
        max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.BEGINNER
    )
    # Set by the assessment engine only; students cannot write it directly.
    assessment_score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["skill__name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "skill"], name="unique_user_skill")
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.skill.name}"

    @property
    def score(self) -> float:
        """Displayed level (0-100): the assessment score when one exists,
        otherwise the self-rated proficiency scaled to a percentage."""
        if self.assessment_score is not None:
            return float(self.assessment_score)
        return self.proficiency_level * 20