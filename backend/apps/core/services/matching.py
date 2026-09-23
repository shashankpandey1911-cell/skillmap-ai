"""Career matching engine (Phase 7).

Combines four explainable signals into a 0-100 match percentage:

    skills   (70%) - importance-weighted readiness against the career's
                     required skill levels (reuses the gap engine's inputs)
    interest (15%) - how much of the career's domain vocabulary appears in
                     the student's interests / preferred domain
    projects (10%) - how many of the student's projects demonstrate the
                     career's skills or domain
    goal     ( 5%) - whether the stated career goal mentions the role

Everything the recommendation page shows — the percentage, the matching and
missing skills, the explanation and the next steps — is derived from the same
inputs, so the page can always show its work.

Career recommendations are guidance for exploration, never guaranteed
outcomes; every response carries DISCLAIMER.
"""

import re

SKILL_WEIGHT = 0.70
INTEREST_WEIGHT = 0.15
PROJECT_WEIGHT = 0.10
GOAL_WEIGHT = 0.05

IMPORTANCE_WEIGHT = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

DISCLAIMER = (
    "These matches are guidance based on your current profile — skills, interests, "
    "projects and goals. They are not a guarantee of job success or placement."
)


def _normalize(text: str) -> str:
    """Lowercase and collapse punctuation so 'full-stack' matches 'full stack'."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower())


def _words(text: str) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", text.lower()) if len(w) > 2}


def skill_match(scores: dict[int, float], requirements) -> float:
    """Importance-weighted readiness: average of current/required, capped at 1.

    scores maps skill_id -> current 0-100 level (assessment score when one
    exists, otherwise self-rated proficiency scaled). A missing skill is 0.
    """
    acc = 0.0
    total = 0
    for req in requirements:
        weight = IMPORTANCE_WEIGHT[req.importance]
        if req.target_level > 0:
            current = scores.get(req.skill_id, 0.0)
            acc += min(current / req.target_level, 1.0) * weight
            total += weight
    return round(acc / total * 100, 1) if total else 0.0


def interest_match(career, profile) -> float:
    """Fraction of the career's domain keywords found in the student's
    interests + preferred domain."""
    text = _normalize(f"{profile.interests or ''} {profile.preferred_domain or ''}")
    keywords = career.domain_keywords_list
    if not keywords or not text:
        return 0.0
    hits = sum(1 for kw in keywords if kw in text)
    return round(hits / len(keywords) * 100, 1)


def project_match(career, requirements, projects) -> float:
    """Fraction of the student's projects whose technologies/description
    mention a required skill or a domain keyword."""
    vocab = [r.skill.name.lower() for r in requirements] + career.domain_keywords_list
    if not projects:
        return 0.0
    evidenced = 0
    for project in projects:
        blob = _normalize(f"{project.technologies or ''} {project.description or ''}")
        if any(term in blob for term in vocab):
            evidenced += 1
    return round(evidenced / len(projects) * 100, 1)


def goal_match(career, profile) -> float:
    """Fraction of the career's title/category words found in the goal text."""
    goal = (profile.career_goal or "").lower()
    if not goal:
        return 0.0
    terms = _words(career.title) | _words(career.category)
    if not terms:
        return 0.0
    hits = sum(1 for term in terms if term in goal)
    return round(hits / len(terms) * 100, 1)


def _explanation(career, matching, missing, interest, project, goal) -> str:
    parts = [
        f"You meet {len(matching)} of {len(matching) + len(missing)} required "
        f"skills for {career.title}."
    ]
    if interest > 0:
        parts.append(f"Your interests line up with the {career.category} domain.")
    if project > 0:
        parts.append("Your projects demonstrate these skills in practice.")
    if goal > 0:
        parts.append("This role fits your stated career goal.")
    if not matching and interest == 0 and project == 0 and goal == 0:
        parts.append(
            "Add skills, projects and interests to your profile for more accurate matches."
        )
    return " ".join(parts)


def _next_steps(gaps, career, project_score, interest_score) -> list[str]:
    """Up to four actionable steps, led by the highest-priority gaps."""
    steps: list[str] = []
    for gap in gaps:
        if gap.gap_class == "NONE" or len(steps) >= 3:
            continue
        verb = (
            "Learn"
            if gap.priority == "HIGH"
            else "Strengthen"
            if gap.priority == "MEDIUM"
            else "Brush up on"
        )
        steps.append(
            f"{verb} {gap.skill_name} to close your {int(gap.gap_percentage)}% gap — "
            f"take the {gap.skill_name} assessment and a structured course."
        )
    if all(gap.gap_class == "NONE" for gap in gaps):
        steps.append(
            f"You meet every requirement for {career.title} — keep sharp with an "
            "advanced assessment or a portfolio project."
        )
    if project_score < 100:
        open_gaps = [g.skill_name for g in gaps if g.gap_class != "NONE"]
        focus = ", ".join(open_gaps[:3]) if open_gaps else "your strongest skills"
        steps.append(f"Build a project using {focus} to demonstrate what you know.")
    if interest_score < 100:
        steps.append(
            f"Explore the {career.category} domain — internships, talks and small "
            "experiments confirm whether it fits you."
        )
    return steps[:4]


def career_match(career, requirements, scores, profile, projects) -> dict:
    """One career's full recommendation for a student.

    Returns a dict ready for CareerMatchSerializer (career is an ORM object).
    """
    skill = skill_match(scores, requirements)
    interest = interest_match(career, profile)
    project = project_match(career, requirements, projects)
    goal = goal_match(career, profile)
    match_pct = round(
        skill * SKILL_WEIGHT
        + interest * INTEREST_WEIGHT
        + project * PROJECT_WEIGHT
        + goal * GOAL_WEIGHT,
        1,
    )

    matching = [
        r.skill.name
        for r in requirements
        if scores.get(r.skill_id, 0.0) >= r.target_level
    ]
    missing = [
        r.skill.name
        for r in requirements
        if scores.get(r.skill_id, 0.0) < r.target_level
    ]

    from apps.core.services.gap import compute_gaps

    gaps = compute_gaps(scores, requirements, career.title)

    return {
        "career": career,
        "match_percentage": match_pct,
        "matching_skills": matching,
        "missing_skills": missing,
        "breakdown": {
            "skills": skill,
            "interests": interest,
            "projects": project,
            "goal": goal,
        },
        "explanation": _explanation(
            career, matching, missing, interest, project, goal
        ),
        "recommended_next_steps": _next_steps(gaps, career, project, interest),
    }
