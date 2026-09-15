"""Assessment submission flow.

submit_attempt() is the single place where an attempt becomes a result:

    1. Validates the payload against the attempt's question bank.
    2. Writes StudentAnswer snapshots inside a transaction.
    3. Scores the run and persists StudentAttempt + AssessmentResult.
    4. Updates (or creates) the student's UserSkill.assessment_score.

build_review() renders a per-question correct/incorrect summary that is safe
to show after submission (it exposes correct answers only then).
"""

from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.services.scoring import (
    build_improvement_suggestions,
    experience_level_for_score,
    score_percentage,
)
from apps.skills.models import UserSkill

from .models import AssessmentResult, Option, Question, StudentAnswer, StudentAttempt


def submit_attempt(
    user,
    attempt: StudentAttempt,
    answers: list[dict[str, int]],
) -> AssessmentResult:
    """Score a submitted attempt and return the immutable result."""
    if attempt.user_id != user.id:
        raise ValidationError({"detail": "This attempt does not belong to you."})
    if attempt.status == StudentAttempt.Status.SUBMITTED:
        raise ValidationError({"detail": "This attempt has already been submitted."})

    questions = list(attempt.assessment.questions.all())
    if not questions:
        raise ValidationError({"detail": "This assessment has no questions."})

    question_ids = {q.id for q in questions}
    chosen: dict[int, Option] = {}

    for item in answers:
        qid = item.get("question_id")
        oid = item.get("option_id")
        if qid not in question_ids:
            raise ValidationError(
                {"answers": f"Question {qid} is not part of this assessment."}
            )
        if qid in chosen:
            raise ValidationError(
                {"answers": f"Question {qid} was answered more than once."}
            )
        if oid is None:
            # Treat a missing pick like an unanswered question.
            continue
        try:
            option = Option.objects.select_related("question").get(pk=oid)
        except Option.DoesNotExist:
            raise ValidationError(
                {"answers": f"Option {oid} is not valid for question {qid}."}
            )
        if option.question_id != qid:
            raise ValidationError(
                {"answers": f"Option {oid} does not belong to question {qid}."}
            )
        chosen[qid] = option

    unanswered = [q for q in questions if q.id not in chosen]
    if unanswered:
        raise ValidationError(
            {
                "answers": "Answer every question before submitting. "
                f"Missing: {len(unanswered)} question(s)."
            }
        )

    correct_count = sum(1 for q in questions if chosen[q.id].is_correct)
    total = len(questions)
    score = score_percentage(correct_count, total)

    missed_texts = [q.text for q in questions if not chosen[q.id].is_correct]

    with transaction.atomic():
        attempt = StudentAttempt.objects.select_for_update().get(pk=attempt.pk)
        if attempt.status == StudentAttempt.Status.SUBMITTED:
            raise ValidationError({"detail": "This attempt has already been submitted."})

        for q in questions:
            StudentAnswer.objects.create(
                attempt=attempt,
                question=q,
                selected_option=chosen[q.id],
                is_correct=chosen[q.id].is_correct,
            )

        attempt.status = StudentAttempt.Status.SUBMITTED
        attempt.submitted_at = timezone.now()
        attempt.score = score
        attempt.correct_count = correct_count
        attempt.total_questions = total
        attempt.save(update_fields=["status", "submitted_at", "score", "correct_count", "total_questions"])

        suggestions = build_improvement_suggestions(
            float(score), attempt.assessment.skill.name, missed_texts
        )
        result = AssessmentResult.objects.create(
            attempt=attempt,
            assessment=attempt.assessment,
            score=score,
            correct_count=correct_count,
            total_questions=total,
            improvement_suggestions=suggestions,
        )

        _sync_user_skill_score(user, attempt.assessment.skill_id, score)

        # Notify student of assessment result
        from apps.notifications.services import notify_assessment_result
        notify_assessment_result(user, attempt.assessment.title, float(score))

    return result


def _sync_user_skill_score(user, skill_id: int, score) -> None:
    """Write the objective score back to the student's skill record.

    If the student has not added the skill yet, a minimal record is created
    (self-rating 1) so the assessment result has somewhere to live.
    """
    skill_row, created = UserSkill.objects.get_or_create(
        user=user,
        skill_id=skill_id,
        defaults={"proficiency_level": 1},
    )
    if created:
        skill_row.experience_level = experience_level_for_score(float(score))
    skill_row.assessment_score = score
    skill_row.save(
        update_fields=["assessment_score"]
        + (["experience_level"] if created else [])
    )


def build_review(attempt: StudentAttempt) -> list[dict[str, Any]]:
    """Per-question summary: what was chosen, what was correct.

    Only meaningful after submission (StudentAnswer rows exist); safe for the
    student to read then, since `is_correct` flags are exposed in the result.
    """
    answers = (
        StudentAnswer.objects.filter(attempt=attempt)
        .select_related("question", "selected_option")
        .order_by("question__order", "question__id")
    )
    review = []
    for answer in answers:
        correct_option = (
            answer.question.options.filter(is_correct=True).first()
        )
        review.append(
            {
                "question_id": answer.question_id,
                "question_text": answer.question.text,
                "selected_option_text": (
                    answer.selected_option.text if answer.selected_option else None
                ),
                "correct_option_text": correct_option.text if correct_option else None,
                "is_correct": answer.is_correct,
            }
        )
    return review
