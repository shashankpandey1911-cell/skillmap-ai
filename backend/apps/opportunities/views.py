"""Opportunity browse + recommendations + admin management endpoints.

Students (and professors/admins browsing the catalog):
    GET  /opportunities                  active postings (search / filter / sort)
    GET  /opportunities/recommendations  every active posting ranked by the
                                         smart match engine, with why-explanations
    GET  /opportunities/<id>             detail + per-skill match breakdown

    Smart match (skills+assessments, profile/eligibility affinity, projects)
    is computed for the caller when they are a student, or for
    ?student_id=<id> when the caller is a professor/admin. A student passing
    someone else's student_id gets 403.

Admins maintain postings (UI lands in the Admin Console phase):
    GET/POST            /admin/opportunities
    GET/PATCH/DELETE    /admin/opportunities/<id>
    POST                /admin/opportunities/<id>/activate | /deactivate
    GET/POST            /admin/opportunities/<id>/requirements
    PATCH/DELETE        /admin/opportunities/<id>/requirements/<rid>
"""

import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.models import Application
from apps.core.permissions import IsAdmin
from apps.skills.models import UserSkill
from apps.students.models import Project, StudentProfile

from .models import Opportunity, OpportunityRequirement
from .serializers import (
    AdminOpportunityDetailSerializer,
    AdminOpportunityWriteSerializer,
    AdminRequirementWriteSerializer,
    OpportunityDetailSerializer,
    OpportunityListSerializer,
    OpportunityRequirementSerializer,
)
from .services import DISCLAIMER, opportunity_match

User = get_user_model()

# Value used to sort postings without a deadline after those with one.
_FAR_FUTURE = datetime.date(9999, 12, 31)


def _resolve_match_inputs(request):
    """Assemble (scores, profile, projects) for the student whose matches are
    being shown.

    Returns (inputs_or_None, error_response_or_None). Students always resolve
    to their own data; professors/admins pass ?student_id= to target one; a
    caller that is not a student and provides no student_id gets (None, None)
    — the payload then omits match fields rather than fabricating them.
    """
    user = request.user
    student_id = request.query_params.get("student_id")
    if student_id:
        if not (user.is_professor or user.is_admin_user):
            return None, Response(
                {"detail": "You can only see matches for yourself."},
                status=status.HTTP_403_FORBIDDEN,
            )
        target = get_object_or_404(
            User.objects.filter(role=User.Role.STUDENT), pk=student_id
        )
    elif user.is_student:
        target = user
    else:
        return None, None

    profile, _ = StudentProfile.objects.get_or_create(user=target)
    scores = {
        us.skill_id: us.score
        for us in UserSkill.objects.filter(user=target).select_related("skill")
    }
    projects = list(Project.objects.filter(user=target))
    return (scores, profile, projects), None


def _active_queryset():
    """Postings students can see: ACTIVE and not past their deadline."""
    today = timezone.localdate()
    return Opportunity.objects.filter(
        status=Opportunity.Status.ACTIVE,
    ).filter(Q(deadline__isnull=True) | Q(deadline__gte=today))


class OpportunityListView(APIView):
    """GET /opportunities — active postings, filterable and sortable.

    Filters: search (title/company/description), type, location, remote.
    Sort: recent (default) | deadline (soonest first) | match (best first).
    """

    def get(self, request):
        inputs, error = _resolve_match_inputs(request)
        if error:
            return error

        qs = _active_queryset()
        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(company__icontains=search)
                | Q(description__icontains=search)
            )
        opp_type = request.query_params.get("type", "").strip()
        if opp_type:
            qs = qs.filter(opportunity_type=opp_type)
        location = request.query_params.get("location", "").strip()
        if location:
            qs = qs.filter(location__icontains=location)
        if request.query_params.get("remote") in ("1", "true", "yes"):
            qs = qs.filter(is_remote=True)

        sort = request.query_params.get("sort", "recent")
        sortable = list(
            qs.prefetch_related("requirements__skill")
            .annotate(
                _deadline=Coalesce("deadline", Value(_FAR_FUTURE))
            )
            .order_by("_deadline", "id")
        )
        if sort == "match" and inputs is not None:
            scores, profile, projects = inputs

            def _match_value(o: Opportunity) -> float:
                match = opportunity_match(
                    o, list(o.requirements.all()), scores, profile, projects
                )
                return match.match_percentage

            sortable.sort(key=lambda o: (-_match_value(o), o.title.lower()))
        elif sort != "deadline":
            # recent (default) — newest postings first
            sortable.sort(key=lambda o: o.created_at, reverse=True)

        serializer = OpportunityListSerializer(
            sortable,
            many=True,
            context={"request": request, "match_inputs": inputs},
        )
        return Response(serializer.data)


class OpportunityRecommendationsView(APIView):
    """GET /opportunities/recommendations — every active posting ranked by the
    smart match engine, sorted best first, each with matching/missing skills,
    a signal breakdown, an explanation and next steps.

    Students get their own recommendations. Professors/admins must pass
    ?student_id=<id> (there is no meaningful recommendation without a target
    student). Every response carries the guidance disclaimer.
    """

    def get(self, request):
        inputs, error = _resolve_match_inputs(request)
        if error:
            return error
        if inputs is None:
            return Response(
                {
                    "detail": (
                        "Recommendations need a target student — pass "
                        "?student_id=<id> with a professor or admin account."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        scores, profile, projects = inputs
        postings = list(
            _active_queryset()
            .prefetch_related("requirements__skill")
            .annotate(_deadline=Coalesce("deadline", Value(_FAR_FUTURE)))
            .order_by("_deadline", "id")
        )

        def _match_value(o: Opportunity) -> float:
            match = opportunity_match(
                o, list(o.requirements.all()), scores, profile, projects
            )
            return match.match_percentage

        postings.sort(key=lambda o: (-_match_value(o), o.title.lower()))

        serializer = OpportunityListSerializer(
            postings,
            many=True,
            context={"request": request, "match_inputs": inputs},
        )
        return Response({"disclaimer": DISCLAIMER, "items": serializer.data})


class OpportunityDetailView(APIView):
    """GET /opportunities/<id> — one posting with its per-skill breakdown."""

    def get(self, request, pk):
        inputs, error = _resolve_match_inputs(request)
        if error:
            return error
        opportunity = get_object_or_404(
            _active_queryset().prefetch_related("requirements__skill"), pk=pk
        )
        serializer = OpportunityDetailSerializer(
            opportunity, context={"request": request, "match_inputs": inputs}
        )
        data = serializer.data
        # The student's own application state so the UI can offer Apply vs Track.
        if request.user.is_student:
            application = Application.objects.filter(
                student=request.user, opportunity=opportunity
            ).first()
            data["my_application"] = (
                {
                    "id": application.id,
                    "status": application.status,
                    "applied_at": application.applied_at,
                }
                if application
                else None
            )
        return Response(data)


# ---------------------------------------------------------------------------
# Admin CRUD
# ---------------------------------------------------------------------------


class AdminOpportunityListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    pagination_class = None

    def get_queryset(self):
        qs = Opportunity.objects.prefetch_related("requirements__skill")
        opp_status = self.request.query_params.get("status", "").strip()
        if opp_status:
            qs = qs.filter(status=opp_status)
        return qs

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminOpportunityDetailSerializer
        return AdminOpportunityWriteSerializer


class AdminOpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Opportunity.objects.prefetch_related("requirements__skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminOpportunityDetailSerializer
        return AdminOpportunityWriteSerializer


class AdminOpportunityActivateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        opportunity = get_object_or_404(Opportunity, pk=pk)
        opportunity.status = Opportunity.Status.ACTIVE
        opportunity.save(update_fields=["status"])
        return Response(AdminOpportunityDetailSerializer(opportunity).data)


class AdminOpportunityDeactivateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        opportunity = get_object_or_404(Opportunity, pk=pk)
        opportunity.status = Opportunity.Status.DRAFT
        opportunity.save(update_fields=["status"])
        return Response(AdminOpportunityDetailSerializer(opportunity).data)


class AdminRequirementListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    pagination_class = None

    def get_queryset(self):
        return OpportunityRequirement.objects.filter(
            opportunity_id=self.kwargs["pk"]
        ).select_related("skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OpportunityRequirementSerializer
        return AdminRequirementWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["opportunity"] = get_object_or_404(Opportunity, pk=self.kwargs["pk"])
        return context

    def perform_create(self, serializer):
        serializer.save(opportunity=self.get_serializer_context()["opportunity"])


class AdminRequirementDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return OpportunityRequirement.objects.filter(
            opportunity_id=self.kwargs["pk"]
        ).select_related("skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OpportunityRequirementSerializer
        return AdminRequirementWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["opportunity"] = get_object_or_404(Opportunity, pk=self.kwargs["pk"])
        return context
