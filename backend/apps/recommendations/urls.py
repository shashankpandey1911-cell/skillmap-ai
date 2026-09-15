"""Recommendation endpoints (Phase 4-5). Computed, not stored.

Planned routes under /api/v1/:
    GET recommendations/gap-analysis     current score vs. target per skill
    GET recommendations/career-matches   careers ranked by match %
    GET recommendations/learning-paths   paths that close top-priority gaps
    GET recommendations/opportunities    jobs/internships matching the profile

Logic lives in apps/core/services/ (gap.py, matching.py) and is wrapped by
the service layer in this app.
"""

from django.urls import path

urlpatterns = []