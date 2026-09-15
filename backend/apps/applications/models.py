"""Student job / internship application tracking (Phase 11).

Application — one student's application to one opportunity. The status moves
through the platform's review lifecycle (Applied → Submitted → Under Review →
Shortlisted → Interview → Selected), with Rejected as a terminal outcome.
Admins drive the status forward (and set the interview date); the student who
applied can read everything, add notes, and see each opportunity's deadline
alongside their application.

Unique per (student, opportunity): a student applies to a posting at most once
and tracks that single application through the pipeline.
"""

from django.conf import settings
from django.db import models


class Application(models.Model):
    """A student's application to an opportunity, tracked to a decision."""

    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        SUBMITTED = "SUBMITTED", "Submitted"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        INTERVIEW = "INTERVIEW", "Interview"
        SELECTED = "SELECTED", "Selected"
        REJECTED = "REJECTED", "Rejected"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
        limit_choices_to={"role": "STUDENT"},
    )
    opportunity = models.ForeignKey(
        "opportunities.Opportunity",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.APPLIED
    )
    notes = models.TextField(blank=True)
    # Set by the admin once the application reaches the Interview stage.
    interview_date = models.DateField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "opportunity"],
                name="unique_student_opportunity_application",
            )
        ]

    def __str__(self) -> str:
        return f"{self.student} → {self.opportunity.title} ({self.status})"
