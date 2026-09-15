"""Notification service — generates notifications for various platform events.

All functions are idempotent: they won't create duplicate notifications for the
same event within a short time window.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification

User = get_user_model()


def _recent_duplicate(user, notification_type, title, minutes=5):
    """Check if a similar notification was created recently."""
    cutoff = timezone.now() - timedelta(minutes=minutes)
    return Notification.objects.filter(
        user=user,
        notification_type=notification_type,
        title=title,
        created_at__gte=cutoff,
    ).exists()


def notify_opportunity_match(user, opportunity, match_percent):
    """Notify student about a new matching opportunity."""
    title = f"New opportunity: {opportunity.title}"
    body = (
        f"{opportunity.company} is hiring — {opportunity.opportunity_type.lower()}. "
        f"Your match: {match_percent:.0f}%."
    )
    link = f"/student/opportunities/{opportunity.id}"
    if _recent_duplicate(user, Notification.Type.OPPORTUNITY_MATCH, title):
        return
    Notification.objects.create(
        user=user,
        notification_type=Notification.Type.OPPORTUNITY_MATCH,
        title=title,
        body=body,
        link=link,
    )


def notify_application_status(application, old_status, new_status):
    """Notify student when their application status changes."""
    status_display = new_status.replace("_", " ").title()
    title = f"Application update: {application.opportunity.title}"
    body = (
        f"Your application to {application.opportunity.company} is now "
        f"\"{status_display}\"."
    )
    link = "/student/applications"
    if _recent_duplicate(
        application.student, Notification.Type.APPLICATION_STATUS, title, minutes=10
    ):
        return
    Notification.objects.create(
        user=application.student,
        notification_type=Notification.Type.APPLICATION_STATUS,
        title=title,
        body=body,
        link=link,
    )


def notify_deadline_reminder(user, opportunity, days_left):
    """Notify student about an upcoming opportunity deadline."""
    title = f"Deadline approaching: {opportunity.title}"
    body = (
        f"{opportunity.company} — deadline in {days_left} day(s). "
        f"Don't miss out!"
    )
    link = f"/student/opportunities/{opportunity.id}"
    if _recent_duplicate(user, Notification.Type.DEADLINE_REMINDER, title, minutes=60):
        return
    Notification.objects.create(
        user=user,
        notification_type=Notification.Type.DEADLINE_REMINDER,
        title=title,
        body=body,
        link=link,
    )


def notify_skill_gap(user, skill_name, gap_percent, career_title):
    """Notify student about a detected skill gap."""
    title = f"Skill gap detected: {skill_name}"
    body = (
        f"You have a {gap_percent:.0f}% gap in {skill_name} for the "
        f"{career_title} career path."
    )
    link = "/student/careers"
    if _recent_duplicate(user, Notification.Type.SKILL_GAP, title):
        return
    Notification.objects.create(
        user=user,
        notification_type=Notification.Type.SKILL_GAP,
        title=title,
        body=body,
        link=link,
    )


def notify_assessment_result(user, assessment_title, score):
    """Notify student after completing an assessment."""
    title = f"Assessment result: {assessment_title}"
    body = f"You scored {score:.1f}% on {assessment_title}."
    link = "/student/assessments"
    if _recent_duplicate(user, Notification.Type.ASSESSMENT_RESULT, title):
        return
    Notification.objects.create(
        user=user,
        notification_type=Notification.Type.ASSESSMENT_RESULT,
        title=title,
        body=body,
        link=link,
    )


def notify_learning_recommendation(user, resource_title, skill_name):
    """Notify student about a recommended learning resource."""
    title = f"Recommended: {resource_title}"
    body = f"We recommend \"{resource_title}\" to improve your {skill_name} skills."
    link = "/student/learning"
    if _recent_duplicate(user, Notification.Type.LEARNING_RECOMMEND, title):
        return
    Notification.objects.create(
        user=user,
        notification_type=Notification.Type.LEARNING_RECOMMEND,
        title=title,
        body=body,
        link=link,
    )


def notify_professor_guidance(user, professor_name, guidance_title):
    """Notify student that a professor left guidance."""
    title = f"Guidance from {professor_name}"
    body = f"{professor_name} added guidance: \"{guidance_title}\"."
    link = "/student/dashboard"
    if _recent_duplicate(user, Notification.Type.PROFESSOR_GUIDANCE, title):
        return
    Notification.objects.create(
        user=user,
        notification_type=Notification.Type.PROFESSOR_GUIDANCE,
        title=title,
        body=body,
        link=link,
    )


def notify_system(user, title, body, link=""):
    """Send a general system notification."""
    Notification.objects.create(
        user=user,
        notification_type=Notification.Type.SYSTEM,
        title=title,
        body=body,
        link=link,
    )
