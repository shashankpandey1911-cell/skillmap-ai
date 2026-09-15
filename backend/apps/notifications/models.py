"""Notification models.

Notification — recipient (User), title, body, type, link, read_at, created_at.

Notification types:
    OPPORTUNITY_MATCH  — new matching opportunity found
    APPLICATION_STATUS — application status changed
    DEADLINE_REMINDER  — upcoming deadline
    SKILL_GAP          — skill gap detected
    ASSESSMENT_RESULT  — assessment completed
    LEARNING_RECOMMEND — learning resource recommended
    PROFESSOR_GUIDANCE — professor left guidance
    SYSTEM             — general system notification
"""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """A single notification for a user."""

    class Type(models.TextChoices):
        OPPORTUNITY_MATCH = "OPPORTUNITY_MATCH", "Opportunity Match"
        APPLICATION_STATUS = "APPLICATION_STATUS", "Application Status"
        DEADLINE_REMINDER = "DEADLINE_REMINDER", "Deadline Reminder"
        SKILL_GAP = "SKILL_GAP", "Skill Gap"
        ASSESSMENT_RESULT = "ASSESSMENT_RESULT", "Assessment Result"
        LEARNING_RECOMMEND = "LEARNING_RECOMMEND", "Learning Recommendation"
        PROFESSOR_GUIDANCE = "PROFESSOR_GUIDANCE", "Professor Guidance"
        SYSTEM = "SYSTEM", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices,
        default=Type.SYSTEM,
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.title}"

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
