"""Career feedback loop (Phase 12).

ApplicationFeedback — generated the moment an application reaches a terminal
decision. When an application is REJECTED the posting's requirements are
compared against the student's real skill levels, the missing skills are
recorded as FeedbackGap rows (a snapshot of the analysis at decision time),
and live learning-resource recommendations are surfaced alongside. When an
application is SELECTED the feedback records the achievement instead.

FeedbackGap — one skill the student was missing for that posting, with the
current vs required levels and the classified gap at the time of rejection.

Nothing about the student's profile is ever changed automatically: the
student explicitly accepts a rejection's feedback (status ACCEPTED) to add
those skills to their learning roadmap, or dismisses it (status DISMISSED).
"""

from django.conf import settings
from django.db import models


class ApplicationFeedback(models.Model):
    """The terminal-decision record for one application."""

    class Kind(models.TextChoices):
        REJECTED = "REJECTED", "Rejected"
        SELECTED = "SELECTED", "Selected"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        DISMISSED = "DISMISSED", "Dismissed"

    application = models.OneToOneField(
        "applications.Application",
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="career_feedback",
        limit_choices_to={"role": "STUDENT"},
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    # Plain-language explanation of the outcome and (for rejections) the gaps.
    summary = models.TextField(blank=True)
    # The student's own notes about this outcome / their plan.
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            f"{self.student} — {self.application.opportunity.title} "
            f"({self.kind} / {self.status})"
        )


class FeedbackGap(models.Model):
    """One unmet requirement of a rejected posting, snapshotted at decision time."""

    feedback = models.ForeignKey(
        ApplicationFeedback, on_delete=models.CASCADE, related_name="gaps"
    )
    skill = models.ForeignKey(
        "skills.Skill", on_delete=models.CASCADE, related_name="feedback_gaps"
    )
    current_level = models.DecimalField(max_digits=5, decimal_places=1)
    required_level = models.PositiveSmallIntegerField()
    gap_percentage = models.DecimalField(max_digits=5, decimal_places=1)
    gap_class = models.CharField(max_length=20)  # LOW | MEDIUM | HIGH
    priority = models.CharField(max_length=20)  # LOW | MEDIUM | HIGH
    recommended_action = models.TextField(blank=True)

    class Meta:
        ordering = ["-gap_percentage", "skill__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["feedback", "skill"], name="unique_feedback_skill_gap"
            )
        ]

    def __str__(self) -> str:
        return f"{self.feedback.application.opportunity.title} — {self.skill.name}"
