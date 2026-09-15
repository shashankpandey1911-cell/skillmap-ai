"""Assessment scoring engine.

Pure, deterministic functions that turn raw answer counts into the numbers
that drive the UI and the student's skill records:

    percentage  - 0-100 (correct / total)
    banding     - 0-100 score -> proficiency (1-5) and experience level
    suggestions - actionable, human-readable improvement advice

Everything here is side-effect free so it is trivially unit-testable; the
submission flow that calls it lives in apps/assessments/services.py.
"""

from decimal import Decimal, ROUND_HALF_UP

# Assessment score -> experience level (used when a skill record is first
# created from an assessment result).
EXPERIENCE_BANDS = [
    (85, "EXPERT"),
    (70, "ADVANCED"),
    (50, "INTERMEDIATE"),
    (0, "BEGINNER"),
]

# Assessment score -> self-rating-equivalent proficiency (1-5).
PROFICIENCY_BANDS = [
    (85, 5),
    (70, 4),
    (50, 3),
    (30, 2),
    (0, 1),
]


def score_percentage(correct_count: int, total_questions: int) -> Decimal:
    """Correct count as a 0-100 percentage, rounded to one decimal place."""
    if total_questions <= 0:
        return Decimal("0.0")
    raw = (correct_count / total_questions) * 100
    return Decimal(str(raw)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def experience_level_for_score(score: float) -> str:
    """Map a 0-100 score onto the UserSkill experience vocabulary."""
    for threshold, level in EXPERIENCE_BANDS:
        if score >= threshold:
            return level
    return "BEGINNER"  # pragma: no cover - bands cover 0-100


def proficiency_for_score(score: float) -> int:
    """Map a 0-100 score onto the 1-5 proficiency scale."""
    for threshold, level in PROFICIENCY_BANDS:
        if score >= threshold:
            return level
    return 1  # pragma: no cover - bands cover 0-100


def _band_message(score: float, skill_name: str) -> str:
    if score >= 85:
        return (
            f"Excellent! You have a strong command of {skill_name}. "
            "Consider an advanced assessment or real-world projects to push further."
        )
    if score >= 70:
        return (
            f"Good grasp of {skill_name}. A few focused corrections will make it solid — "
            "review the missed questions below and retake when ready."
        )
    if score >= 50:
        return (
            f"You have a working foundation in {skill_name}, but key concepts need "
            "reinforcement. Go through the missed questions, then practise with "
            "hands-on exercises before retaking."
        )
    return (
        f"Your {skill_name} fundamentals need work. Start with the basics — courses and "
        "guided tutorials — then attempt this assessment again."
    )


def build_improvement_suggestions(
    score: float,
    skill_name: str,
    missed_question_texts: list[str],
) -> list[str]:
    """Human-readable advice stored on the AssessmentResult."""
    suggestions = [_band_message(score, skill_name)]
    if missed_question_texts:
        preview = ", ".join(
            f"“{text.strip()[:80]}{'…' if len(text) > 80 else ''}”"
            for text in missed_question_texts[:3]
        )
        remaining = len(missed_question_texts) - 3
        tail = f" and {remaining} more" if remaining > 0 else ""
        suggestions.append(
            f"Revise the concept behind the {len(missed_question_texts)} question(s) "
            f"you missed: {preview}{tail}."
        )
    else:
        suggestions.append(
            "Keep your skills sharp — try the next-difficulty assessment or build a "
            "small project using what you just validated."
        )
    return suggestions
