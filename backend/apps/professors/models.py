"""Professor guidance models (Phase 14)."""

from django.conf import settings
from django.db import models


class GuidanceNote(models.Model):
    """A professor's guidance note for a student."""

    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guidance_notes_given",
        limit_choices_to={"role": "PROFESSOR"},
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guidance_notes_received",
        limit_choices_to={"role": "STUDENT"},
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=[
            ("ACADEMIC", "Academic"),
            ("CAREER", "Career"),
            ("SKILL", "Skill Development"),
            ("GENERAL", "General"),
        ],
        default="GENERAL",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Guidance from {self.professor} to {self.student}: {self.title}"


class RecommendedResource(models.Model):
    """A professor's resource recommendation for a student."""

    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resources_recommended",
        limit_choices_to={"role": "PROFESSOR"},
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resources_received",
        limit_choices_to={"role": "STUDENT"},
    )
    resource = models.ForeignKey(
        "learning.LearningResource",
        on_delete=models.CASCADE,
        related_name="professor_recommendations",
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["professor", "student", "resource"]

    def __str__(self):
        return f"{self.professor} recommends {self.resource} to {self.student}"
