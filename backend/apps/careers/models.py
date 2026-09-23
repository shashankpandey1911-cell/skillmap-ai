"""Career catalog models.

Career                — a target role (e.g. "Backend Developer") with metadata.
CareerSkillRequirement— the skills a career expects and the target proficiency
                        level (0-100) for each, plus how important that skill is
                        to the role. The skill-gap engine compares these
                        requirements against a student's UserSkill records.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.skills.models import Skill


class Career(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=200, blank=True)
    outlook = models.TextField(blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    # Comma-separated keywords used to match student interests / goal text
    # (e.g. "backend, api, server, software, development").
    domain_keywords = models.TextField(blank=True)
    # Comma-separated recommended learning focus areas for this career.
    learning_areas = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    @property
    def domain_keywords_list(self) -> list[str]:
        """Parsed, lowercased domain keywords for the matching engine."""
        return [k.strip().lower() for k in self.domain_keywords.split(",") if k.strip()]


class CareerSkillRequirement(models.Model):
    """A skill a career needs, with the target level and its importance.

    target_level is the required 0-100 proficiency (the student's current
    level is computed the same way — assessment score when one exists,
    otherwise self-rated proficiency scaled to a percentage).
    """

    class Importance(models.TextChoices):
        HIGH = "HIGH", "High"
        MEDIUM = "MEDIUM", "Medium"
        LOW = "LOW", "Low"

    career = models.ForeignKey(
        Career, on_delete=models.CASCADE, related_name="requirements"
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="career_requirements"
    )
    target_level = models.PositiveSmallIntegerField(
        default=60, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    importance = models.CharField(
        max_length=10, choices=Importance.choices, default=Importance.MEDIUM
    )

    class Meta:
        # -target_level approximates importance ordering without relying on
        # string comparison of the importance choices.
        ordering = ["-target_level", "skill__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["career", "skill"], name="unique_career_skill_requirement"
            )
        ]

    def __str__(self) -> str:
        return f"{self.career.title} — {self.skill.name} ({self.target_level})"
