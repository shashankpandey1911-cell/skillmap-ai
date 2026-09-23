"""Shared logic for student profiles (used by students + analytics views)."""

from .models import StudentProfile


def _pct(values) -> int:
    filled = sum(1 for value in values if value)
    return round(filled / len(values) * 100)


def profile_completeness_sections(profile: StudentProfile) -> dict:
    """Completeness broken down by profile section, plus an overall score.

    Sections mirror the profile page: personal, academic, career, projects,
    certifications — each 0-100; overall is their average.
    """
    user = profile.user
    sections = {
        "personal": _pct(
            [
                user.first_name,
                user.email,
                user.phone,
                profile.college,
                profile.course,
                profile.branch,
                profile.year,
            ]
        ),
        "academic": _pct(
            [profile.cgpa, profile.semester, profile.achievements]
        ),
        "career": _pct(
            [profile.career_goal, profile.preferred_domain, profile.interests]
        ),
        "projects": 100 if user.projects.exists() else 0,
        "certifications": 100 if user.certifications.exists() else 0,
    }
    overall = round(sum(sections.values()) / len(sections))
    return {"overall": overall, "sections": sections}


def profile_completeness(profile: StudentProfile) -> int:
    """Overall profile completeness percent (0-100)."""
    return profile_completeness_sections(profile)["overall"]
