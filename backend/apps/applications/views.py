"""Application endpoints (Phase 11).

Students:
    GET    /students/me/applications            own applications (status/search)
    POST   /students/me/applications            apply to an open opportunity
    GET    /students/me/applications/<id>       own application detail
    PATCH  /students/me/applications/<id>       add notes (nothing else)

Professors / admins can read one student's applications:
    GET    /applications?student_id=<id>

Admins drive the pipeline:
    GET    /admin/applications                  all applications (filters)
    GET    /admin/applications/<id>             detail
    PATCH  /admin/applications/<id>             status / interview_date / notes
"""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.feedback.services import generate_application_feedback
from apps.opportunities.models import Opportunity

from .models import Application
from .serializers import (
    AdminApplicationListSerializer,
    AdminApplicationWriteSerializer,
    ApplicationCreateSerializer,
    ApplicationSerializer,
    StudentNotesWriteSerializer,
)

User = get_user_model()

VALID_STATUSES = {choice.value for choice in Application.Status}


def _applyable(opportunity: Opportunity) -> bool:
    """A posting can be applied to while ACTIVE and not past its deadline."""
    if opportunity.status != Opportunity.Status.ACTIVE:
        return False
    if opportunity.deadline is not None and opportunity.deadline < timezone.localdate():
        return False
    return True


def _application_queryset():
    return Application.objects.select_related("opportunity", "student")


class MyApplicationListCreateView(APIView):
    """GET (own list) + POST (apply) for the logged-in student."""

    def get(self, request):
        if not request.user.is_student:
            return Response(
                {"detail": "Only students have applications."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = _application_queryset().filter(student=request.user)

        opp_status = request.query_params.get("status", "").strip()
        if opp_status:
            if opp_status not in VALID_STATUSES:
                return Response(
                    {"detail": f"Unknown status '{opp_status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(status=opp_status)
        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(opportunity__title__icontains=search)
                | Q(opportunity__company__icontains=search)
            )
        return Response(ApplicationSerializer(qs, many=True).data)

    def post(self, request):
        if not request.user.is_student:
            return Response(
                {"detail": "Only students can apply."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        opportunity = serializer.validated_data["opportunity"]
        if not _applyable(opportunity):
            return Response(
                {"detail": "This opportunity is no longer accepting applications."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Application.objects.filter(
            student=request.user, opportunity=opportunity
        ).exists():
            return Response(
                {"detail": "You have already applied to this opportunity."},
                status=status.HTTP_409_CONFLICT,
            )
        application = Application.objects.create(
            student=request.user, opportunity=opportunity
        )
        return Response(
            ApplicationSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )


class MyApplicationDetailView(APIView):
    """GET / PATCH the student's own application (notes only on PATCH)."""

    def _get_owned(self, request, pk):
        if not request.user.is_student:
            return None
        return get_object_or_404(
            Application.objects.filter(student=request.user).select_related(
                "opportunity"
            ),
            pk=pk,
        )

    def get(self, request, pk):
        application = self._get_owned(request, pk)
        if application is None:
            return Response(
                {"detail": "Only students can view their own applications."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(ApplicationSerializer(application).data)

    def patch(self, request, pk):
        if not request.user.is_student:
            return Response(
                {"detail": "Only students can edit their own applications."},
                status=status.HTTP_403_FORBIDDEN,
            )
        application = get_object_or_404(
            Application.objects.filter(student=request.user), pk=pk
        )
        forbidden = set(request.data.keys()) - {"notes"}
        if forbidden:
            return Response(
                {
                    "detail": (
                        "Students can only edit the notes field "
                        f"(got: {', '.join(sorted(forbidden))})."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = StudentNotesWriteSerializer(
            application, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ApplicationSerializer(application).data)


class StudentApplicationsView(APIView):
    """GET /applications?student_id= — one student's applications for
    professors/admins (guidance and review workflows)."""

    def get(self, request):
        student_id = request.query_params.get("student_id", "").strip()
        if request.user.is_student:
            return Response(
                {"detail": "Use /students/me/applications for your own list."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not (request.user.is_professor or request.user.is_admin_user):
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not student_id:
            return Response(
                {"detail": "A student_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        target = get_object_or_404(
            User.objects.filter(role=User.Role.STUDENT), pk=student_id
        )
        qs = _application_queryset().filter(student=target)
        opp_status = request.query_params.get("status", "").strip()
        if opp_status:
            if opp_status not in VALID_STATUSES:
                return Response(
                    {"detail": f"Unknown status '{opp_status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(status=opp_status)
        return Response(ApplicationSerializer(qs, many=True).data)


class AdminApplicationListView(APIView):
    """GET /admin/applications — every application, filterable by status,
    search, or a specific student. Only admins may see cross-student data."""

    permission_classes = [IsAdmin]

    def get(self, request):
        qs = _application_queryset()
        opp_status = request.query_params.get("status", "").strip()
        if opp_status:
            if opp_status not in VALID_STATUSES:
                return Response(
                    {"detail": f"Unknown status '{opp_status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(status=opp_status)
        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(opportunity__title__icontains=search)
                | Q(opportunity__company__icontains=search)
                | Q(student__email__icontains=search)
                | Q(student__first_name__icontains=search)
            )
        student_id = request.query_params.get("student_id", "").strip()
        if student_id:
            qs = qs.filter(student_id=student_id)
        return Response(AdminApplicationListSerializer(qs, many=True).data)


class AdminApplicationDetailView(APIView):
    """GET / PATCH one application as an admin.

    PATCH accepts status (any lifecycle stage), interview_date and notes;
    every other field is rejected. This is where the pipeline is driven.
    """

    permission_classes = [IsAdmin]

    def get_object(self, pk):
        return get_object_or_404(_application_queryset(), pk=pk)

    def get(self, request, pk):
        return Response(AdminApplicationListSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        application = self.get_object(pk)
        allowed = {"status", "interview_date", "notes"}
        unknown = set(request.data.keys()) - allowed
        if unknown:
            return Response(
                {
                    "detail": (
                        "Only status, interview_date and notes can be updated "
                        f"(got: {', '.join(sorted(unknown))})."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        old_status = application.status
        serializer = AdminApplicationWriteSerializer(
            application, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Terminal decisions (Phase 12) produce career feedback automatically:
        # rejections get a gap analysis, selections an achievement record.
        if application.status != old_status and application.status in (
            Application.Status.REJECTED,
            Application.Status.SELECTED,
        ):
            generate_application_feedback(application)
        # Notify student of status change
        from apps.notifications.services import notify_application_status
        notify_application_status(application, old_status, application.status)
        return Response(AdminApplicationListSerializer(application).data)
