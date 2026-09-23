"""AI assistant views — all four features."""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsVerifiedStudent
from apps.skills.models import Skill, UserSkill
from apps.students.models import StudentProfile

from .provider import ai_available
from .serializers import (
    AICareerResponseSerializer,
    AILearningResponseSerializer,
    AIOpportunityExplanationSerializer,
    ApprovedExtractRequestSerializer,
    ResumeExtractRequestSerializer,
    ResumeExtractResponseSerializer,
)
from .services import (
    ai_career_recommendation,
    ai_learning_recommendation,
    ai_opportunity_explanation,
    extract_from_resume,
)


class AIStatusView(APIView):
    """GET /ai/status — whether AI provider is configured."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, _request):
        return Response({"ai_available": ai_available()})


# ─── FEATURE 1: Resume Extraction ────────────────────────────────────────


class ResumeExtractView(APIView):
    """POST /ai/extract-resume — extract skills/projects from resume text."""
    permission_classes = [IsVerifiedStudent]

    def post(self, request):
        ser = ResumeExtractRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = extract_from_resume(ser.validated_data["resume_text"])
        return Response(result)


class ResumeApproveView(APIView):
    """POST /ai/approve-extraction — save approved extracted data to profile."""
    permission_classes = [IsVerifiedStudent]

    def post(self, request):
        ser = ApprovedExtractRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        created = {"skills": 0, "projects": 0}

        # Save approved skills
        for s in data.get("skills", []):
            skill_obj, _ = Skill.objects.get_or_create(
                name__iexact=s["name"],
                defaults={"name": s["name"], "category": s.get("category", "Other")},
            )
            # Use get_or_create with name__iexact by filtering first
            existing = Skill.objects.filter(name__iexact=s["name"]).first()
            if existing:
                skill_obj = existing
            _, was_created = UserSkill.objects.get_or_create(
                user=request.user,
                skill=skill_obj,
                defaults={
                    "proficiency_level": max(1, min(5, int(s.get("confidence", 0.5) * 5))),
                    "experience_level": "BEGINNER",
                },
            )
            if was_created:
                created["skills"] += 1

        return Response(
            {
                "detail": "Extracted data saved to your profile.",
                "created": created,
            }
        )


# ─── FEATURE 2: AI Career Recommendation ────────────────────────────────


class AICareerRecommendationView(APIView):
    """POST /ai/career-recommendation — AI-enhanced career suggestions."""
    permission_classes = [IsVerifiedStudent]

    def post(self, request):
        user = request.user
        profile = StudentProfile.objects.filter(user=user).first()
        user_skills = UserSkill.objects.filter(user=user).select_related("skill")

        profile_data = {
            "career_goal": getattr(profile, "career_goal", "") or "",
            "interests": getattr(profile, "interests", "") or "",
            "preferred_domain": getattr(profile, "preferred_domain", "") or "",
            "course": getattr(profile, "course", "") or "",
        }
        skills_data = [
            {
                "name": us.skill.name,
                "category": us.skill.category,
                "score": float(us.score),
                "proficiency_level": us.proficiency_level,
            }
            for us in user_skills
        ]

        # Get active careers with requirements
        from apps.careers.models import Career

        careers = list(
            Career.objects.filter(is_active=True).values(
                "id", "title", "category", "description"
            )
        )

        result = ai_career_recommendation(profile_data, skills_data, careers)
        serializer = AICareerResponseSerializer(data=result)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(result)


# ─── FEATURE 3: AI Learning Recommendation ──────────────────────────────


class AILearningRecommendationView(APIView):
    """POST /ai/learning-recommendation — personalized learning roadmap."""
    permission_classes = [IsVerifiedStudent]

    def post(self, request):
        career_title = request.data.get("career_title", "")
        if not career_title:
            return Response(
                {"detail": "career_title is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user_skills = UserSkill.objects.filter(user=user).select_related("skill")

        skills_data = [
            {
                "name": us.skill.name,
                "score": float(us.score),
                "proficiency_level": us.proficiency_level,
            }
            for us in user_skills
        ]

        # Compute skill gaps against the target career
        from apps.careers.models import Career, CareerSkillRequirement
        from apps.core.services.gap import compute_gaps

        career = Career.objects.filter(title__icontains=career_title, is_active=True).first()
        if not career:
            return Response(
                {"detail": f"Career '{career_title}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        requirements = CareerSkillRequirement.objects.filter(career=career).select_related("skill")
        scores = {us.skill_id: float(us.score) for us in user_skills}
        gaps = compute_gaps(scores, requirements, career.title)

        gap_data = [
            {
                "skill_name": g.skill_name,
                "gap_percentage": g.gap_percentage,
                "priority": g.priority,
            }
            for g in gaps
            if g.gap_class != "NONE"
        ]

        result = ai_learning_recommendation(skills_data, career.title, gap_data)
        serializer = AILearningResponseSerializer(data=result)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(result)


# ─── FEATURE 4: AI Opportunity Explanation ──────────────────────────────


class AIOpportunityExplanationView(APIView):
    """POST /ai/opportunity-explanation — explain why an opportunity matches."""
    permission_classes = [IsVerifiedStudent]

    def post(self, request):
        opportunity_id = request.data.get("opportunity_id")
        if not opportunity_id:
            return Response(
                {"detail": "opportunity_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.opportunities.models import Opportunity, OpportunityRequirement
        from apps.opportunities.services import opportunity_match
        from apps.students.models import Project, StudentProfile

        try:
            opp = Opportunity.objects.get(pk=opportunity_id, status="ACTIVE")
        except Opportunity.DoesNotExist:
            return Response(
                {"detail": "Opportunity not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user
        user_skills = UserSkill.objects.filter(user=user).select_related("skill")
        requirements = OpportunityRequirement.objects.filter(opportunity=opp).select_related("skill")
        scores = {us.skill_id: float(us.score) for us in user_skills}
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        projects = Project.objects.filter(user=user)

        # Get existing match data
        match_result = opportunity_match(opp, requirements, scores, profile, projects)

        opp_data = {
            "title": opp.title,
            "company": opp.company,
            "opportunity_type": opp.opportunity_type,
            "required_skills": ", ".join(r.skill.name for r in requirements),
        }

        student_skills = [
            {"name": us.skill.name, "score": float(us.score)}
            for us in user_skills
        ]

        result = ai_opportunity_explanation(student_skills, opp_data, match_result)
        serializer = AIOpportunityExplanationSerializer(data=result)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(result)
