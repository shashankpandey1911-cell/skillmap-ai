"""Career catalog and skill gap analysis endpoints.

Students:
    GET  /careers                       career catalog
    GET  /careers/<id>                  one career with its requirements
    GET  /careers/<id>/gap-analysis     the student's own skill gaps

Professors / admins can request another student's analysis:
    GET  /careers/<id>/gap-analysis?student_id=7

Admins maintain the catalog (UI lands in Phase 7):
    GET/POST       /admin/careers
    GET/PATCH/DELETE /admin/careers/<id>
    GET/POST       /admin/careers/<id>/requirements
    PATCH/DELETE   /admin/careers/<id>/requirements/<rid>
"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.core.services.gap import compute_gaps, gap_summary, readiness_score
from apps.core.services.matching import DISCLAIMER, career_match
from apps.skills.models import UserSkill
from apps.students.models import Project, StudentProfile

from .models import Career, CareerSkillRequirement
from .serializers import (
    AdminCareerWriteSerializer,
    AdminRequirementWriteSerializer,
    CareerDetailSerializer,
    CareerListSerializer,
    CareerRequirementSerializer,
    GapAnalysisSerializer,
)

User = get_user_model()


class CareerListView(generics.ListAPIView):
    """GET /careers — active careers, optionally filtered by ?search=."""

    serializer_class = CareerListSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Career.objects.filter(is_active=True)
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset


class CareerDetailView(generics.RetrieveAPIView):
    """GET /careers/<id> — full career with required skills and levels."""

    serializer_class = CareerDetailSerializer

    def get_queryset(self):
        return Career.objects.filter(is_active=True).prefetch_related(
            "requirements__skill"
        )


class CareerMatchListView(APIView):
    """GET /careers/matches — every active career ranked by match percentage.

    Students get their own recommendations; professors/admins pass
    ?student_id=<id> to see another student's. The match combines skills,
    interests, projects and the career goal (see apps/core/services/matching.py)
    and always carries the guidance disclaimer.
    """

    def get(self, request):
        target_user = request.user
        student_id = request.query_params.get("student_id")
        if student_id:
            if not (request.user.is_professor or request.user.is_admin_user):
                return Response(
                    {"detail": "You can only view your own career matches."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            target_user = get_object_or_404(
                User.objects.filter(role=User.Role.STUDENT), pk=student_id
            )
        elif not request.user.is_student:
            return Response(
                {"detail": "A student_id is required for this role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile, _ = StudentProfile.objects.get_or_create(user=target_user)
        scores = {
            us.skill_id: us.score
            for us in UserSkill.objects.filter(user=target_user).select_related("skill")
        }
        projects = list(Project.objects.filter(user=target_user))

        matches = []
        careers = Career.objects.filter(is_active=True).prefetch_related(
            "requirements__skill"
        )
        for career in careers:
            requirements = list(career.requirements.all())
            matches.append(
                career_match(career, requirements, scores, profile, projects)
            )
        matches.sort(key=lambda m: (-m["match_percentage"], m["career"].title))

        return Response(
            {
                "disclaimer": DISCLAIMER,
                "matches": [
                    {**m, "career": CareerListSerializer(m["career"]).data}
                    for m in matches
                ],
            }
        )


class CareerGapAnalysisView(APIView):
    """GET /careers/<id>/gap-analysis — compare a student's skills with the
    career's requirements.

    Students always see their own analysis; professors/admins pass
    ?student_id=<id> to analyze any student. Cross-role reads are forbidden.
    """

    def get(self, request, pk):
        career = get_object_or_404(
            Career.objects.filter(is_active=True), pk=pk
        )
        target_user = request.user
        student_id = request.query_params.get("student_id")
        if student_id:
            if not (request.user.is_professor or request.user.is_admin_user):
                return Response(
                    {"detail": "You can only view your own skill gap analysis."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            target_user = get_object_or_404(
                User.objects.filter(role=User.Role.STUDENT), pk=student_id
            )
        elif not request.user.is_student:
            return Response(
                {"detail": "A student_id is required for this role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        scores = {
            us.skill_id: us.score
            for us in UserSkill.objects.filter(user=target_user).select_related("skill")
        }
        requirements = list(career.requirements.select_related("skill"))
        gaps = compute_gaps(scores, requirements, career.title)
        payload = GapAnalysisSerializer(
            {
                "career": career,
                "readiness_percentage": readiness_score(gaps),
                "gaps": gaps,
                "summary": gap_summary(gaps),
            }
        ).data
        return Response(payload)


# ---------------------------------------------------------------------------
# Admin CRUD
# ---------------------------------------------------------------------------


class AdminCareerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    pagination_class = None

    def get_queryset(self):
        return Career.objects.prefetch_related("requirements__skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CareerDetailSerializer
        return AdminCareerWriteSerializer


class AdminCareerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Career.objects.prefetch_related("requirements__skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CareerDetailSerializer
        return AdminCareerWriteSerializer


class AdminRequirementListCreateView(generics.ListCreateAPIView):
    """Requirements under one career; creation enforces unique skills."""

    permission_classes = [IsAdmin]
    pagination_class = None

    def get_queryset(self):
        return CareerSkillRequirement.objects.filter(career_id=self.kwargs["pk"])

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CareerRequirementSerializer
        return AdminRequirementWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["career"] = get_object_or_404(Career, pk=self.kwargs["pk"])
        return context

    def perform_create(self, serializer):
        serializer.save(career=self.get_serializer_context()["career"])


class AdminRequirementDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return CareerSkillRequirement.objects.filter(career_id=self.kwargs["pk"])

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CareerRequirementSerializer
        return AdminRequirementWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["career"] = get_object_or_404(Career, pk=self.kwargs["pk"])
        return context
