"""Personalized learning roadmap builder (Phase 8).

build_roadmap(student, career) turns the Phase 6 skill-gap analysis into a
concrete, ordered upskilling plan for the student:

    Skill Gap  → the computed gap (current vs required)
    Topic      → what to learn about the skill
    Resource   → curated courses / videos / docs for the skill
    Practice   → hands-on exercises and projects
    Assessment → quiz material + the platform's published skill assessment
    Improvement→ what "done" looks like (target score closes the gap)

Every item shown comes from the LearningResource catalog or the assessments
app — nothing is fabricated. Progress (completed ÷ recommended) is computed
live from the student's ResourceCompletion rows over exactly the items the
roadmap displays, so the numbers always reconcile with the UI.
"""

from django.db.models import Count

from apps.assessments.models import Assessment, StudentAttempt
from apps.core.services.gap import SkillGap, compute_gaps, readiness_score
from apps.skills.models import UserSkill

from .models import LearningResource, ResourceCompletion

# Type grouping used to route resources into the right roadmap step.
LEARN_TYPES = [
    LearningResource.Type.COURSE,
    LearningResource.Type.VIDEO,
    LearningResource.Type.DOCUMENTATION,
]
PRACTICE_TYPES = [
    LearningResource.Type.PRACTICE,
    LearningResource.Type.PROJECT,
]
QUIZ_TYPES = [LearningResource.Type.QUIZ]

TYPE_INDEX = {
    t: i
    for i, t in enumerate(
        [
            LearningResource.Type.COURSE,
            LearningResource.Type.VIDEO,
            LearningResource.Type.DOCUMENTATION,
            LearningResource.Type.PRACTICE,
            LearningResource.Type.PROJECT,
            LearningResource.Type.QUIZ,
        ]
    )
}
LEVEL_INDEX = {
    LearningResource.Level.BEGINNER: 0,
    LearningResource.Level.INTERMEDIATE: 1,
    LearningResource.Level.ADVANCED: 2,
}

# A bigger gap means the student should start from easier material.
EXPECTED_LEVEL = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

PER_STEP_LIMITS = {"resource": 3, "practice": 2, "assessment": 2}


def _recommended_resources(
    skill_id: int, types: list[str], gap_class: str, limit: int
) -> list[LearningResource]:
    """Best-fit active resources for a skill gap, deterministically ordered.

    Ordering favours the difficulty closest to the student's need (a HIGH gap
    surfaces Beginner material first) and then a sensible type order, so a
    roadmap reads top-to-bottom like a curriculum.
    """
    expected = EXPECTED_LEVEL[gap_class]
    queryset = LearningResource.objects.filter(
        skill_id=skill_id, is_active=True, type__in=types
    )

    def sort_key(resource: LearningResource):
        level_distance = abs(LEVEL_INDEX[resource.level] - expected)
        return (
            level_distance,
            TYPE_INDEX[resource.type],
            resource.title.lower(),
        )

    return sorted(queryset, key=sort_key)[:limit]


def recommend_resources(
    skill_id: int, gap_class: str, limit: int = 4
) -> list[LearningResource]:
    """Best-fit active resources (learn + practice types) for one skill gap.

    Shared with the feedback loop (Phase 12) so the recommendations on a
    rejected application use exactly the same level-aware picking as the
    roadmap.
    """
    return _recommended_resources(
        skill_id, LEARN_TYPES + PRACTICE_TYPES, gap_class, limit
    )


def roadmap_for_gap(gap: SkillGap, user) -> dict:
    """A full five-step skill roadmap for one gap, completion-stamped.

    Used by the feedback loop to add accepted rejection gaps to the student's
    learning roadmap.
    """
    completed_ids = set(
        ResourceCompletion.objects.filter(user=user, resource__skill_id=gap.skill_id)
        .values_list("resource_id", flat=True)
    )
    return _skill_roadmap(gap, completed_ids, user)


def _resource_item(resource: LearningResource, completed: bool) -> dict:
    return {
        "id": resource.id,
        "title": resource.title,
        "description": resource.description,
        "type": resource.type,
        "level": resource.level,
        "url": resource.url,
        "estimated_duration_minutes": resource.estimated_duration_minutes,
        "completed": completed,
    }


def _platform_assessment(skill_id: int, user) -> dict | None:
    """The published platform assessment for the skill (if any) plus the
    student's most recent score, so the roadmap can point at a real test."""
    assessment = (
        Assessment.objects.filter(skill_id=skill_id, is_published=True)
        .annotate(question_count=Count("questions"))
        .order_by("-created_at")
        .first()
    )
    if assessment is None:
        return None
    last = (
        StudentAttempt.objects.filter(
            user=user,
            assessment_id=assessment.id,
            status=StudentAttempt.Status.SUBMITTED,
        )
        .order_by("-submitted_at")
        .first()
    )
    return {
        "id": assessment.id,
        "title": assessment.title,
        "difficulty": assessment.difficulty,
        "question_count": assessment.question_count,
        "my_last_score": (
            float(last.score) if last and last.score is not None else None
        ),
    }


def _skill_roadmap(gap: SkillGap, completed_ids: set[int], user) -> dict:
    """One skill gap expanded into its ordered roadmap steps."""
    level_bucket = EXPECTED_LEVEL[gap.gap_class]
    gap_label = gap.gap_class.title()

    learn = _recommended_resources(
        gap.skill_id, LEARN_TYPES, gap.gap_class, PER_STEP_LIMITS["resource"]
    )
    practice = _recommended_resources(
        gap.skill_id, PRACTICE_TYPES, gap.gap_class, PER_STEP_LIMITS["practice"]
    )
    quizzes = _recommended_resources(
        gap.skill_id, QUIZ_TYPES, gap.gap_class, PER_STEP_LIMITS["assessment"]
    )

    def items(resources):
        return [_resource_item(r, r.id in completed_ids) for r in resources]

    start_hint = (
        "beginner" if level_bucket == 0 else "intermediate" if level_bucket == 1 else "advanced"
    )
    topic_text = (
        f"Build a working command of {gap.skill_name} (a {gap.category.lower()} "
        f"skill). This is a {gap_label.lower()} gap for your target career, so "
        f"start at the {start_hint}-friendly end of the materials below and "
        "work your way up."
    )
    resource_text = (
        f"Work through these curated materials to build a solid {gap.skill_name} "
        "foundation. Take notes and code along where you can."
    )
    practice_text = (
        f"Apply {gap.skill_name} hands-on — exercises and a small project make "
        "the concepts stick and give you something to show."
    )
    platform_assessment = _platform_assessment(gap.skill_id, user)
    if platform_assessment:
        assessment_text = (
            f"Quiz yourself now, then take “{platform_assessment['title']}” on the "
            "platform to get an objective score for your profile."
        )
    else:
        assessment_text = (
            "Quiz yourself with the questions below. A scored assessment is "
            "coming soon for this skill."
        )
    improvement_text = (
        f"Raise {gap.skill_name} from {gap.current_level:g}% to the "
        f"{gap.required_level}% bar for this career. Once you complete the "
        "steps above, retake the assessment and aim for a score at or above "
        "the target — your skill score updates automatically and this gap closes."
    )

    return {
        "skill": {
            "id": gap.skill_id,
            "name": gap.skill_name,
            "category": gap.category,
        },
        "gap": {
            "current_level": gap.current_level,
            "required_level": gap.required_level,
            "gap_percentage": gap.gap_percentage,
            "gap_class": gap.gap_class,
            "priority": gap.priority,
        },
        "recommended_action": gap.recommended_action,
        "steps": [
            {"key": "topic", "title": "Learning Topic", "description": topic_text, "items": []},
            {"key": "resource", "title": "Resource", "description": resource_text, "items": items(learn)},
            {"key": "practice", "title": "Practice", "description": practice_text, "items": items(practice)},
            {
                "key": "assessment",
                "title": "Assessment",
                "description": assessment_text,
                "items": items(quizzes),
                "platform_assessment": platform_assessment,
            },
            {"key": "improvement", "title": "Skill Improvement", "description": improvement_text, "items": []},
        ],
    }


def _displayed_resource_ids(roadmap: list[dict]) -> list[int]:
    """The resource ids actually shown on the roadmap (what progress counts)."""
    return [
        item["id"]
        for skill_roadmap in roadmap
        for step in skill_roadmap["steps"]
        for item in step["items"]
    ]


def build_roadmap(student, career) -> dict:
    """Full learning roadmap for one student against one target career.

    Only skills with an open gap (priority != NONE) get a roadmap; skills the
    student already meets are excluded because there is nothing to improve.
    Progress is the share of recommended resources the student has completed.
    """
    scores = {
        us.skill_id: us.score
        for us in UserSkill.objects.filter(user=student).select_related("skill")
    }
    requirements = list(career.requirements.select_related("skill"))
    gaps = compute_gaps(scores, requirements, career.title)
    open_gaps = [g for g in gaps if g.priority != "NONE"]

    roadmap = [_skill_roadmap(g, set(), student) for g in open_gaps]
    displayed_ids = list(
        dict.fromkeys(
            item["id"]
            for skill_roadmap in roadmap
            for step in skill_roadmap["steps"]
            for item in step["items"]
        )
    )
    completed_ids = set(
        ResourceCompletion.objects.filter(user=student, resource_id__in=displayed_ids)
        .values_list("resource_id", flat=True)
    )
    # Stamp the real flags onto the already-built items (pick is independent).
    for skill_roadmap in roadmap:
        for step in skill_roadmap["steps"]:
            for item in step["items"]:
                item["completed"] = item["id"] in completed_ids

    total = len(displayed_ids)
    done = sum(1 for rid in displayed_ids if rid in completed_ids)
    progress_percentage = round(done / total * 100) if total else 0

    return {
        "career": {
            "id": career.id,
            "title": career.title,
            "category": career.category,
        },
        "readiness_percentage": readiness_score(gaps),
        "progress": {
            "total_resources": total,
            "completed_resources": done,
            "remaining_resources": total - done,
            "progress_percentage": progress_percentage,
        },
        "priority_skills": [
            {
                "skill_id": g.skill_id,
                "skill_name": g.skill_name,
                "gap_class": g.gap_class,
                "priority": g.priority,
                "gap_percentage": g.gap_percentage,
            }
            for g in open_gaps
        ],
        "roadmap": roadmap,
    }
