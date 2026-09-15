"""Demo career feedback for the walkthrough (Phase 12).

Gives the demo student both sides of the loop:
  - a REJECTED application (PhonePe Product Engineering Intern) with a real
    gap analysis and pending recommendations the student can accept, and
  - a SELECTED application (Infosys Graduate Trainee Program) recorded as an
    achievement on the dashboard.

Idempotent: existing applications are left untouched and feedback is only
generated when missing.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.applications.models import Application
from apps.opportunities.models import Opportunity

from .models import ApplicationFeedback
from .services import generate_application_feedback

User = get_user_model()

# (opportunity title, company, terminal status, days since applied)
DEMO_DECISIONS = [
    ("Product Engineering Intern", "PhonePe", Application.Status.REJECTED, 12),
    ("Graduate Trainee Program", "Infosys", Application.Status.SELECTED, 20),
]


def ensure_demo_feedback() -> int:
    """Create demo terminal applications + feedback that do not exist yet."""
    student = User.objects.filter(email="student@skillmap.ai").first()
    if student is None:
        return 0
    created = 0
    now = timezone.now()
    for title, company, status_, days_ago in DEMO_DECISIONS:
        opportunity = Opportunity.objects.filter(title=title, company=company).first()
        if opportunity is None:
            continue
        application, app_created = Application.objects.get_or_create(
            student=student,
            opportunity=opportunity,
            defaults={
                "status": status_,
                "applied_at": now - timezone.timedelta(days=days_ago),
            },
        )
        if not app_created and application.status != status_:
            continue  # live state diverged from the demo spec; do not override
        existed = ApplicationFeedback.objects.filter(application=application).exists()
        # Always (re)generate: repairs rows a failed earlier run left partial.
        if generate_application_feedback(application) is not None and not existed:
            created += 1
    return created