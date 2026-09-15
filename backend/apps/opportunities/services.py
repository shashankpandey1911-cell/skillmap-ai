"""Smart opportunity matching engine (Phase 10).

Combines three transparent signals into a 0-100 match percentage for one
posting, mirroring the Phase 7 career engine but for opportunities:

    skills   (70%) - how much of the posting's required skill levels the
                     student currently meets (assessment scores override
                     self-ratings, so completed platform assessments feed
                     straight into this signal)
    profile  (20%) - how much of the posting's vocabulary — title, company,
                     type and eligibility wording — appears in the student's
                     interests, career goal, course and branch, i.e. how well
                     their background lines up with the role's eligibility
    projects (10%) - how many of the student's projects demonstrate the
                     posting's required skills or domain

A posting that lists no required skills uses a redistributed profile 70% /
projects 30% blend instead of a skills component.

Everything shown on the recommendation UI — the percentage, the matching
skills, the gaps, the explanation and the next steps — is derived from the
same inputs, so the page can always show its work. Matches are guidance, never
a guarantee of selection (see DISCLAIMER).
"""

import re
from dataclasses import dataclass

SKILL_WEIGHT = 0.70
PROFILE_WEIGHT = 0.20
PROJECT_WEIGHT = 0.10
# Weights used when a posting has no listed required skills.
PROFILE_ONLY_WEIGHT = 0.70
PROJECT_ONLY_WEIGHT = 0.30

DISCLAIMER = (
    "Matches are guidance based on your current profile — skills, assessment "
    "scores, background and projects. They are not a guarantee that you will "
    "be shortlisted or selected."
)

# Generic words that carry no signal about a role's domain.
_STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "your",
    "you",
    "have",
    "has",
    "this",
    "that",
    "are",
    "will",
    "who",
    "not",
    "our",
    "their",
    "they",
    "were",
    "was",
    "into",
    "about",
    "over",
    "under",
}


def _normalize(text: str) -> str:
    """Lowercase and collapse punctuation so 'full-stack' matches 'full stack'."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower())


def _words(text: str) -> set[str]:
    return {
        w
        for w in re.split(r"[^a-z0-9]+", text.lower())
        if len(w) > 2 and w not in _STOP_WORDS
    }


def _opportunity_vocab(opportunity) -> set[str]:
    """Headline vocabulary of a posting: title, company, type and eligibility."""
    return _words(
        " ".join(
            [
                opportunity.title or "",
                opportunity.company or "",
                opportunity.opportunity_type or "",
                opportunity.eligibility or "",
            ]
        )
    )


def skills_score(scores: dict[int, float], requirements) -> float | None:
    """Average of current/required across a posting's requirements, capped.

    A missing skill counts 0; a skill the student already meets (or a
    requirement with no minimum) contributes the full 100. Returns None when
    the posting lists no requirements.
    """
    reqs = list(requirements)
    if not reqs:
        return None
    total = 0.0
    for req in reqs:
        if req.min_level <= 0:
            total += 1.0
        else:
            current = round(float(scores.get(req.skill_id, 0.0)), 1)
            total += min(current / req.min_level, 1.0)
    return round(total / len(reqs) * 100, 1)


def profile_score(opportunity, profile) -> float:
    """How much of the posting's vocabulary appears in the student's profile.

    The student side is their interests, preferred domain, career goal, about,
    course and branch — so echoing the eligibility wording (e.g. course and
    degree terms) raises the score.
    """
    student_text = _normalize(
        " ".join(
            [
                profile.interests or "",
                profile.preferred_domain or "",
                profile.career_goal or "",
                profile.about or "",
                profile.course or "",
                profile.branch or "",
            ]
        )
    )
    vocab = _opportunity_vocab(opportunity)
    if not vocab or not student_text:
        return 0.0
    hits = sum(1 for term in vocab if term in student_text)
    return round(hits / len(vocab) * 100, 1)


def projects_score(opportunity, requirements, projects) -> float:
    """Fraction of the student's projects that demonstrate the posting's
    required skills or domain."""
    vocab = [r.skill.name.lower() for r in requirements] + list(
        _opportunity_vocab(opportunity)
    )
    if not projects:
        return 0.0
    evidenced = 0
    for project in projects:
        blob = _normalize(f"{project.technologies or ''} {project.description or ''}")
        if any(term in blob for term in vocab):
            evidenced += 1
    return round(evidenced / len(projects) * 100, 1)


@dataclass(frozen=True)
class OpportunityMatch:
    match_percentage: float
    skills_score: float | None
    profile_score: float
    projects_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    matched_requirements: int
    total_requirements: int
    explanation: str
    recommended_next_steps: list[str]


def _explanation(opportunity, requirements, matching, missing, profile, projects) -> str:
    parts = []
    if requirements:
        parts.append(
            f"You meet {len(matching)} of {len(matching) + len(missing)} required "
            f"skills for {opportunity.title}."
        )
    else:
        parts.append(f"{opportunity.title} lists no specific required skills.")
    if matching:
        parts.append(f"Your {', '.join(matching)} skills are ready for this role.")
    if profile > 0:
        parts.append(
            "Your interests, course or career goal line up with what the posting asks for."
        )
    if projects > 0:
        parts.append("Your projects show these skills in practice.")
    if missing:
        parts.append(
            f"You are missing {', '.join(missing)}, which the role expects."
        )
    if not matching and profile == 0 and projects == 0 and missing:
        parts.append(
            "Add skills, projects and interests to your profile for a more accurate match."
        )
    return " ".join(parts)


def _next_steps(opportunity, requirements, missing, matching, projects) -> list[str]:
    steps: list[str] = []
    for name in missing[:2]:
        req = next((r for r in requirements if r.skill.name == name), None)
        bar = f" (the posting wants {req.min_level}%)" if req and req.min_level > 0 else ""
        steps.append(
            f"Close the {name} gap{bar} before applying — learn it and retake the "
            f"{name} assessment to update your score."
        )
    if matching and not missing:
        steps.append(
            f"You already meet the skills {opportunity.company} expects — tailor your "
            "resume to this role and apply while it is open."
        )
    if projects < 100:
        focus = ", ".join(missing[:2]) if missing else "your strongest skills"
        steps.append(f"Build or showcase a project using {focus} to demonstrate it.")
    if not steps:
        steps.append(
            "Start by adding this role's skills to your profile and taking their "
            "assessments."
        )
    return steps[:3]


def opportunity_match(opportunity, requirements, scores, profile, projects) -> OpportunityMatch:
    """One posting's full, explainable recommendation for a student.

    requirements: iterable of OpportunityRequirement rows with the related
    skill loaded. scores maps skill_id -> current 0-100 level. profile is the
    student's StudentProfile, projects their Project queryset/list.
    """
    reqs = list(requirements)
    skill = skills_score(scores, reqs)
    profile_p = profile_score(opportunity, profile)
    project_p = projects_score(opportunity, reqs, projects)

    if skill is None:
        # No listed skills: the match is driven by background + projects.
        match_pct = round(
            profile_p * PROFILE_ONLY_WEIGHT + project_p * PROJECT_ONLY_WEIGHT, 1
        )
    else:
        match_pct = round(
            skill * SKILL_WEIGHT
            + profile_p * PROFILE_WEIGHT
            + project_p * PROJECT_WEIGHT,
            1,
        )

    matching: list[str] = []
    missing: list[str] = []
    for req in reqs:
        if req.min_level <= 0 or scores.get(req.skill_id, 0.0) >= req.min_level:
            matching.append(req.skill.name)
        else:
            missing.append(req.skill.name)

    return OpportunityMatch(
        match_percentage=match_pct,
        skills_score=skill,
        profile_score=profile_p,
        projects_score=project_p,
        matching_skills=matching,
        missing_skills=missing,
        matched_requirements=len(matching),
        total_requirements=len(reqs),
        explanation=_explanation(
            opportunity, reqs, matching, missing, profile_p, project_p
        ),
        recommended_next_steps=_next_steps(
            opportunity, reqs, missing, matching, project_p
        ),
    )
