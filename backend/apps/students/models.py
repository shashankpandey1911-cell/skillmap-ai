"""Student career profile models.

Phase 3 implements the complete digital profile: personal/academic/career
data on StudentProfile, plus Project and Certification (with Education and
CareerGoal-compatible fields folded into the profile).
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class StudentProfile(models.Model):
    """Digital career profile, one per student user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    # --- Personal / academic ---
    college = models.CharField(max_length=200, blank=True)
    course = models.CharField(max_length=150, blank=True)
    branch = models.CharField(max_length=150, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(6)])
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    semester = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    achievements = models.TextField(blank=True)

    # --- Career ---
    career_goal = models.CharField(max_length=300, blank=True)
    preferred_domain = models.CharField(max_length=150, blank=True)
    interests = models.TextField(blank=True)

    # --- About & links ---
    about = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.username} — {self.college or 'no college'}"


class Project(models.Model):
    """A project the student has worked on."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    technologies = models.CharField(max_length=300, blank=True)
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Certification(models.Model):
    """A certification the student has earned."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certifications",
    )
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=150, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_date", "-created_at"]

    def __str__(self) -> str:
        return self.name