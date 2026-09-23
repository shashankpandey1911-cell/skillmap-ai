"""Career feedback loop engine (Phase 12).

generate_application_feedback — called whenever an application reaches a
terminal decision (REJECTED or SELECTED). Rejections snapshot the posting's
unmet requirements against the student's real skill levels as FeedbackGap
rows and produce a plain-language summary; selections record the achievement.

The loop deliberately NEVER mutates the student's profile or skills. The
student decides what to do with rejection feedback:

    accept  -> the gap's skills join the student's learning roadmap
    dismiss -> the feedback is set aside (nothing changes)

Recommendations are computed live from the learning-resource catalog each
time the feedback is read, so links never go stale and closed gaps stop
being recommended.
"""

from apps.core.services.gap import (
    SkillGap,
    classify_gap,
    priority_for,
    recommended_action,
)
from apps.learning.models import ResourceCompletion
from apps.learning.services import recommend_resources, roadmap_for_gap
from apps.skills.models import UserSkill

from .models import ApplicationFeedback, FeedbackGap

_PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def _student_score(user, skill_id: int) -> float:
    """The student's live 0-100 level for a skill (assessment score wins)."""
    us = UserSkill.objects.filter(user=user, skill_id=skill_id).first()
    return us.score if us else 0.0


def _build_gaps(application) -> list[FeedbackGap]:
    """Snapshot every unmet requirement of the posting vs the student's skills.

    Only real gaps (current < required) are recorded — a requirement the
    student already meets is not feedback. Importance is HIGH because the
    posting explicitly asked for the skill.
    """
    scores = {
        us.skill_id: us.score
        for us in UserSkill.objects.filter(user=application.student).select_related("skill")
    }
    gaps: list[FeedbackGap] = []
    for req in application.opportunity.requirements.select_related("skill"):
        current = round(float(scores.get(req.skill_id, 0.0)), 1)
        required = int(req.min_level)
        gap_pct = round(max(0.0, required - current), 1)
        if gap_pct <= 0:
            continue
        gap_class = classify_gap(gap_pct)
        priority = priority_for("HIGH", gap_class)
        gaps.append(
            FeedbackGap(
                skill=req.skill,
                current_level=current,
                required_level=required,
                gap_percentage=gap_pct,
                gap_class=gap_class,
                priority=priority,
                recommended_action=recommended_action(
                    req.skill.name, application.opportunity.title, gap_class, priority
                ),
            )
        )
    gaps.sort(
        key=lambda g: (_PRIORITY_ORDER[g.priority], -float(g.gap_percentage), g.skill.name)
    )
    return gaps


def generate_application_feedback(application) -> ApplicationFeedback | None:
    """Create (or refresh) the feedback for a terminal application decision.

    Idempotent: one feedback row per application. Returns None when the
    application has not reached a terminal decision.
    """
    kind = application.status
    if kind not in (
        ApplicationFeedback.Kind.REJECTED,
        ApplicationFeedback.Kind.SELECTED,
    ):
        return None

    feedback, _created = ApplicationFeedback.objects.get_or_create(
        application=application,
        defaults={"student": application.student, "kind": kind},
    )
    # Always rebuild the analysis for the current decision: the call site
    # (admin status update) only invokes this on a status change, and a
    # rebuild also repairs rows a failed earlier run may have left partial.
    feedback.kind = kind
    feedback.gaps.all().delete()

    opportunity = application.opportunity
    if kind == ApplicationFeedback.Kind.SELECTED:
        feedback.summary = (
            f"Congratulations — your application for {opportunity.title} at "
            f"{opportunity.company} was successful! This achievement is recorded "
            "on your profile and dashboard."
        )
    else:
        gaps = _build_gaps(application)
        if gaps:
            for gap in gaps:
                gap.feedback = feedback
            feedback.gaps.bulk_create(gaps)
        if gaps:
            names = ", ".join(
                f"{g.skill.name} ({float(g.gap_percentage):g}% gap)" for g in gaps
            )
            feedback.summary = (
                f"Your application for {opportunity.title} at {opportunity.company} was "
                f"not selected. Comparing the posting's requirements with your skills, "
                f"the main gaps are: {names}. Close these gaps to raise your match score "
                "and your chances with similar roles."
            )
        else:
            feedback.summary = (
                f"Your application for {opportunity.title} at {opportunity.company} was "
                "not selected — you already met every listed requirement, so the outcome "
                "likely came down to competition, headcount or other factors. Keep "
                "building strong projects and applying to similar roles."
            )
    feedback.save()
    return feedback


def gap_recommendations(gap: FeedbackGap) -> list[dict]:
    """Live catalog picks for one feedback gap (same picking as the roadmap).

    Falls back to a concrete practice suggestion when the catalog has no
    material for the skill yet.
    """
    picks = recommend_resources(gap.skill_id, gap.gap_class, 4)
    recommendations = [
        {
            "resource_id": resource.id,
            "title": resource.title,
            "kind": resource.type,
            "level": resource.level,
            "url": resource.url,
            "estimated_duration_minutes": resource.estimated_duration_minutes,
        }
        for resource in picks
    ]
    if not recommendations:
        recommendations.append(
            {
                "resource_id": None,
                "title": f"{gap.skill.name} practice",
                "kind": "PRACTICE",
                "level": "BEGINNER",
                "url": "",
                "estimated_duration_minutes": None,
                "description": (
                    f"Work through {gap.skill.name} exercises and a small project — "
                    "curated links for this skill are coming soon."
                ),
            }
        )
    return recommendations


def build_feedback_roadmap(student) -> dict:
    """Roadmap entries from ACCEPTED rejection feedback, recomputed live.

    Skills whose gap has since been closed (the student's level now meets the
    posting's bar) drop out automatically. Returns the skill roadmaps plus
    resource counts so the learning view can merge them into overall progress.
    """
    skills: list[dict] = []
    feedbacks = (
        ApplicationFeedback.objects.filter(
            student=student,
            kind=ApplicationFeedback.Kind.REJECTED,
            status=ApplicationFeedback.Status.ACCEPTED,
        )
        .select_related("application__opportunity")
        .prefetch_related("gaps__skill")
    )
    for feedback in feedbacks:
        opportunity = feedback.application.opportunity
        for gap in feedback.gaps.all():
            current = _student_score(student, gap.skill_id)
            required = int(gap.required_level)
            remaining = round(max(0.0, required - current), 1)
            if remaining <= 0:
                continue  # gap already closed — nothing to recommend
            gap_class = classify_gap(remaining)
            priority = priority_for("HIGH", gap_class)
            live_gap = SkillGap(
                skill_id=gap.skill_id,
                skill_name=gap.skill.name,
                category=gap.skill.category,
                current_level=current,
                required_level=required,
                gap_percentage=remaining,
                gap_class=gap_class,
                importance="HIGH",
                priority=priority,
                recommended_action=recommended_action(
                    gap.skill.name, opportunity.title, gap_class, priority
                ),
            )
            roadmap = roadmap_for_gap(live_gap, student)
            roadmap["source"] = {
                "feedback_id": feedback.id,
                "kind": "feedback",
                "opportunity": opportunity.title,
                "company": opportunity.company,
            }
            skills.append(roadmap)

    displayed_ids = list(
        dict.fromkeys(
            item["id"]
            for skill_roadmap in skills
            for step in skill_roadmap["steps"]
            for item in step["items"]
        )
    )
    done = 0
    if displayed_ids:
        completed = set(
            ResourceCompletion.objects.filter(
                user=student, resource_id__in=displayed_ids
            ).values_list("resource_id", flat=True)
        )
        done = sum(1 for rid in displayed_ids if rid in completed)

    return {
        "skills": skills,
        "total_resources": len(displayed_ids),
        "completed_resources": done,
    }
