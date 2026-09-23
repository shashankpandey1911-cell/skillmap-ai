"""Read-only aggregation endpoints for dashboards.

These are real database counts — no fabricated numbers. Additional
analytics (skill heatmaps, readiness distributions) land in Phases 6-7.
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessments.models import StudentAttempt
from apps.core.permissions import IsAdmin, IsProfessor
from apps.students.models import StudentProfile
from apps.students.services import profile_completeness
from apps.users.models import User


class ProfessorDashboardSummaryView(APIView):
    permission_classes = [IsProfessor]

    def get(self, request):
        profiles = list(StudentProfile.objects.select_related("user"))
        avg_completeness = (
            round(sum(profile_completeness(p) for p in profiles) / len(profiles))
            if profiles
            else 0
        )
        return Response(
            {
                "total_students": User.objects.filter(role=User.Role.STUDENT).count(),
                "students_with_profiles": len(profiles),
                "avg_profile_completeness": avg_completeness,
                "assessments_completed": StudentAttempt.objects.filter(
                    status=StudentAttempt.Status.SUBMITTED
                ).count(),
                "feedback_given": 0,  # Phase 6
            }
        )


class AdminDashboardSummaryView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(
            {
                "total_users": User.objects.count(),
                "students": User.objects.filter(role=User.Role.STUDENT).count(),
                "professors": User.objects.filter(role=User.Role.PROFESSOR).count(),
                "admins": User.objects.filter(role=User.Role.ADMIN).count(),
            }
        )
