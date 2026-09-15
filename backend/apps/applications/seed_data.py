"""Demo applications for the demo student (Phase 11).

Gives the walkthrough a realistic tracker: several applications at different
stages of the pipeline so the status timeline and filters demo well.
Idempotent — a (student, opportunity) pair is created at most once.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.opportunities.models import Opportunity

from .models import Application

User = get_user_model()

# (opportunity title, company, desired status, days since applied)
DEMO_APPLICATIONS = [
    ("Software Engineering Intern", "Zoho Corporation", Application.Status.APPLIED, 1),
    (
        "Associate Software Engineer (Backend)",
        "Razorpay",
        Application.Status.UNDER_REVIEW,
        4,
    ),
    (
        "Software Development Engineer Intern",
        "Walmart Global Tech India",
        Application.Status.SHORTLISTED,
        8,
    ),
]


def ensure_demo_applications() -> int:
    """Create demo applications that do not exist yet. Returns count created."""
    student = User.objects.filter(email="student@skillmap.ai").first()
    if student is None:
        return 0
    created = 0
    now = timezone.now()
    for title, company, status_, days_ago in DEMO_APPLICATIONS:
        opportunity = Opportunity.objects.filter(title=title, company=company).first()
        if opportunity is None:
            continue
        if Application.objects.filter(
            student=student, opportunity=opportunity
        ).exists():
            continue
        Application.objects.create(
            student=student,
            opportunity=opportunity,
            status=status_,
            applied_at=now - timezone.timedelta(days=days_ago),
        )
        created += 1
    return created
