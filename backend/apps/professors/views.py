"""Professor endpoints (Phase 14).

Students:
    GET  /professors/students              list students (search, filter by branch/year)
    GET  /professors/students/<id>/dossier  full student dossier

Guidance:
    GET  /professors/students/<id>/guidance      list guidance for a student
    POST /professors/students/<id>/guidance      add guidance note
    DELETE /professors/guidance/<id>             delete own guidance note

Analytics:
    GET  /professors/analytics           cohort analytics (career ready, gaps, scores, goals)
"""

from django.db import models
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsProfessor
from apps.users.models import User

from .models import GuidanceNote
from .serializers import (
    StudentListSerializer,
    StudentDossierSerializer,
    GuidanceNoteSerializer,
    GuidanceNoteCreateSerializer,
)


class ProfessorStudentListView(APIView):
    """GET /professors/students — list students with search and filters."""

    permission_classes = [IsProfessor]

    def get(self, request):
        queryset = User.objects.filter(role=User.Role.STUDENT)

        from apps.students.models import StudentProfile

        # Search
        search = request.query_params.get("search", "").strip()
        if search:
            profile_ids = StudentProfile.objects.filter(
                Q(college__icontains=search) | Q(course__icontains=search)
            ).values_list("user_id", flat=True)
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(id__in=profile_ids)
            )

        # Filters
        branch = request.query_params.get("branch", "").strip()
        if branch:
            branch_ids = StudentProfile.objects.filter(
                branch__icontains=branch
            ).values_list("user_id", flat=True)
            queryset = queryset.filter(id__in=branch_ids)

        year = request.query_params.get("year", "").strip()
        if year:
            year_ids = StudentProfile.objects.filter(
                year=year
            ).values_list("user_id", flat=True)
            queryset = queryset.filter(id__in=year_ids)

        college = request.query_params.get("college", "").strip()
        if college:
            college_ids = StudentProfile.objects.filter(
                college__icontains=college
            ).values_list("user_id", flat=True)
            queryset = queryset.filter(id__in=college_ids)

        # Ordering
        order = request.query_params.get("order", "-date_joined")
        if order in [
            "date_joined",
            "-date_joined",
            "first_name",
            "-first_name",
            "year",
            "-year",
        ]:
            queryset = queryset.order_by(order)

        serializer = StudentListSerializer(queryset, many=True)
        return Response(serializer.data)


class ProfessorStudentDossierView(APIView):
    """GET /professors/students/<id>/dossier — full student dossier."""

    permission_classes = [IsProfessor]

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
        serializer = StudentDossierSerializer(student)
        return Response(serializer.data)


class ProfessorStudentGuidanceView(APIView):
    """GET/POST /professors/students/<id>/guidance — list or add guidance."""

    permission_classes = [IsProfessor]

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
        notes = GuidanceNote.objects.filter(
            professor=request.user, student=student
        ).select_related("professor", "student")

        # Allow viewing all professors' notes for this student
        if request.query_params.get("all") == "true":
            notes = GuidanceNote.objects.filter(student=student).select_related(
                "professor", "student"
            )

        serializer = GuidanceNoteSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
        serializer = GuidanceNoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = GuidanceNote.objects.create(
            professor=request.user,
            student=student,
            **serializer.validated_data,
        )

        # Notify student of professor guidance
        from apps.notifications.services import notify_professor_guidance
        professor_name = request.user.get_full_name() or request.user.username
        notify_professor_guidance(student, professor_name, note.title)

        return Response(
            GuidanceNoteSerializer(note).data,
            status=status.HTTP_201_CREATED,
        )


class ProfessorGuidanceDeleteView(APIView):
    """DELETE /professors/guidance/<id> — delete own guidance note."""

    permission_classes = [IsProfessor]

    def delete(self, request, pk):
        note = get_object_or_404(
            GuidanceNote, pk=pk, professor=request.user
        )
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfessorAnalyticsView(APIView):
    """GET /professors/analytics — cohort analytics for charts."""

    permission_classes = [IsProfessor]

    def get(self, request):
        from apps.skills.models import UserSkill
        from apps.careers.models import Career, CareerSkillRequirement
        from apps.core.services.gap import compute_gaps, readiness_score
        from apps.assessments.models import StudentAttempt, Question
        from apps.students.models import StudentProfile
        from apps.students.services import profile_completeness

        students = User.objects.filter(role=User.Role.STUDENT)
        total_students = students.count()

        # Career readiness per student
        career = Career.objects.filter(is_active=True).first()
        requirements = []
        if career:
            requirements = list(
                CareerSkillRequirement.objects.filter(career=career).select_related("skill")
            )

        career_ready_count = 0
        students_with_gaps = 0
        readiness_scores = []

        for student in students:
            user_skills = UserSkill.objects.filter(user=student).select_related("skill")
            skill_scores = {us.skill_id: us.proficiency_level * 20 for us in user_skills}

            if requirements:
                gaps = compute_gaps(skill_scores, requirements, career.title)
                readiness = round(readiness_score(gaps))
                readiness_scores.append(readiness)

                if readiness >= 70:
                    career_ready_count += 1

                gap_count = sum(1 for g in gaps if g.gap_class in ("LOW", "MEDIUM", "HIGH"))
                if gap_count > 0:
                    students_with_gaps += 1

        # Average assessment score
        attempts = StudentAttempt.objects.filter(status=StudentAttempt.Status.SUBMITTED)
        avg_score = 0
        if attempts.exists():
            total_score = 0
            count = 0
            for attempt in attempts:
                total_q = Question.objects.filter(assessment=attempt.assessment).count()
                if total_q > 0:
                    total_score += attempt.score / total_q * 100
                    count += 1
            avg_score = round(total_score / count, 1) if count > 0 else 0

        # Popular career goals
        profiles = StudentProfile.objects.exclude(career_goal="").values_list(
            "career_goal", flat=True
        )
        career_goals = {}
        for goal in profiles:
            goal_lower = goal.lower().strip()
            career_goals[goal_lower] = career_goals.get(goal_lower, 0) + 1
        popular_goals = sorted(
            [{"goal": g, "count": c} for g, c in career_goals.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:5]

        # Common skill gaps
        gap_skills = {}
        for student in students:
            user_skills = UserSkill.objects.filter(user=student).select_related("skill")
            skill_scores = {us.skill_id: us.proficiency_level * 20 for us in user_skills}

            if requirements:
                gaps = compute_gaps(skill_scores, requirements, career.title)
                for g in gaps:
                    if g.gap_class in ("MEDIUM", "HIGH"):
                        if g.skill_name not in gap_skills:
                            gap_skills[g.skill_name] = {"count": 0, "total_gap": 0}
                        gap_skills[g.skill_name]["count"] += 1
                        gap_skills[g.skill_name]["total_gap"] += g.gap_percentage

        common_gaps = sorted(
            [
                {
                    "skill": s,
                    "affected_students": d["count"],
                    "avg_gap": round(d["total_gap"] / d["count"], 1),
                }
                for s, d in gap_skills.items()
            ],
            key=lambda x: x["affected_students"],
            reverse=True,
        )[:5]

        # Students by year
        year_dist = (
            students
            .annotate(year_val=models.F("student_profile__year"))
            .values("year_val")
            .annotate(count=Count("id"))
            .order_by("year_val")
        )
        students_by_year = [
            {"year": item["year_val"] or 0, "count": item["count"]} for item in year_dist
        ]

        # Readiness distribution
        readiness_dist = {"high": 0, "medium": 0, "low": 0}
        for score in readiness_scores:
            if score >= 70:
                readiness_dist["high"] += 1
            elif score >= 40:
                readiness_dist["medium"] += 1
            else:
                readiness_dist["low"] += 1

        return Response(
            {
                "total_students": total_students,
                "career_ready_students": career_ready_count,
                "students_with_gaps": students_with_gaps,
                "avg_assessment_score": avg_score,
                "popular_career_goals": popular_goals,
                "common_skill_gaps": common_gaps,
                "students_by_year": students_by_year,
                "readiness_distribution": readiness_dist,
            }
        )
