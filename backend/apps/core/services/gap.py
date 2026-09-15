"""Skill gap analysis engine.

Pure, deterministic functions that turn a career's required skill levels and
a student's current levels (0-100 each) into the numbers behind the Skill Gap
Dashboard:

    compute_gaps       - per-requirement current vs required, gap %, class
    classify_gap       - NONE / LOW / MEDIUM / HIGH from the gap size
    priority_for       - combined importance + gap class
    recommended_action - human-readable, deterministic guidance
    readiness_score    - overall career readiness (average of capped ratios)

Everything is side-effect free so it is trivially unit-testable; the views in
apps/careers assemble the inputs from the database and call into here.

Gap semantics:
    current < required  -> gap = required - current, classified by size
    current >= required -> "No Gap"
    skill not on the student's profile -> current = 0 (full gap)
"""

from dataclasses import dataclass

# A gap >= 40 points is HIGH, >= 20 is MEDIUM, anything above 0 is LOW.
GAP_CLASS_THRESHOLDS: list[tuple[int, str]] = [(40, "HIGH"), (20, "MEDIUM"), (0, "LOW")]

IMPORTANCE_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
RANK_LABEL = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}


@dataclass(frozen=True)
class SkillGap:
    skill_id: int
    skill_name: str
    category: str
    current_level: float
    required_level: int
    gap_percentage: float
    gap_class: str  # NONE | LOW | MEDIUM | HIGH
    importance: str  # LOW | MEDIUM | HIGH
    priority: str  # NONE | LOW | MEDIUM | HIGH
    recommended_action: str


def classify_gap(gap_percentage: float) -> str:
    """Classify a gap size (0-100) as NONE / LOW / MEDIUM / HIGH."""
    if gap_percentage <= 0:
        return "NONE"
    for threshold, label in GAP_CLASS_THRESHOLDS:
        if gap_percentage >= threshold:
            return label
    return "LOW"  # pragma: no cover - thresholds cover all positive values


def priority_for(importance: str, gap_class: str) -> str:
    """Combine a skill's importance with its gap class into one priority.

    Either dimension being HIGH makes the priority HIGH; otherwise either
    being MEDIUM makes it MEDIUM; a no-gap skill has no priority.
    """
    if gap_class == "NONE":
        return "NONE"
    combined = max(IMPORTANCE_RANK[importance], IMPORTANCE_RANK[gap_class])
    return RANK_LABEL[combined]


def recommended_action(
    skill_name: str, career_title: str, gap_class: str, priority: str
) -> str:
    """Deterministic guidance keyed off the computed gap state."""
    if gap_class == "NONE":
        return (
            f"You already meet the {career_title} bar for {skill_name} — keep it "
            "sharp with practice or an advanced assessment."
        )
    if priority == "HIGH":
        return (
            f"{skill_name} is critical for {career_title}. Take the {skill_name} "
            "assessment, finish a structured course, and build a hands-on project "
            "to close this gap."
        )
    if priority == "MEDIUM":
        return (
            f"Strengthen {skill_name} with guided practice and a small project, "
            f"then retake the {skill_name} assessment to verify your progress."
        )
    return (
        f"Brush up on {skill_name} fundamentals — review the basics and attempt a "
        "beginner-level assessment."
    )


def compute_gaps(
    student_scores: dict[int, float],
    requirements,
    career_title: str,
) -> list[SkillGap]:
    """Compare a student's current levels against a career's requirements.

    student_scores maps skill_id -> current 0-100 level (from UserSkill).
    requirements is an iterable of CareerSkillRequirement rows (with the
    related skill loaded).
    """
    gaps: list[SkillGap] = []
    for req in requirements:
        current = round(float(student_scores.get(req.skill_id, 0.0)), 1)
        required = int(req.target_level)
        gap_pct = round(max(0.0, required - current), 1)
        gap_class = classify_gap(gap_pct)
        priority = priority_for(req.importance, gap_class)
        gaps.append(
            SkillGap(
                skill_id=req.skill_id,
                skill_name=req.skill.name,
                category=req.skill.category,
                current_level=current,
                required_level=required,
                gap_percentage=gap_pct,
                gap_class=gap_class,
                importance=req.importance,
                priority=priority,
                recommended_action=recommended_action(
                    req.skill.name, career_title, gap_class, priority
                ),
            )
        )
    # Highest-priority gaps first, then the biggest gaps.
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}
    gaps.sort(key=lambda g: (order[g.priority], -g.gap_percentage, g.skill_name))
    return gaps


def readiness_score(gaps: list[SkillGap]) -> float:
    """Overall readiness 0-100: average of current/required, capped at 100%.

    A missing skill (current 0) contributes 0; a met requirement contributes
    the full 100.
    """
    if not gaps:
        return 0.0
    total = 0.0
    for gap in gaps:
        if gap.required_level <= 0:
            ratio = 1.0
        else:
            ratio = min(gap.current_level / gap.required_level, 1.0)
        total += ratio
    return round((total / len(gaps)) * 100, 1)


def gap_summary(gaps: list[SkillGap]) -> dict:
    """Counts per gap class for the dashboard's summary cards."""
    summary = {"total": len(gaps), "no_gap": 0, "low": 0, "medium": 0, "high": 0}
    for gap in gaps:
        key = "no_gap" if gap.gap_class == "NONE" else gap.gap_class.lower()
        summary[key] += 1
    return summary