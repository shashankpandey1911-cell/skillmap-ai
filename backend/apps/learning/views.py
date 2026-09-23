"""Learning content and roadmap endpoints (Phase 8).

Students:
    GET  /learning/resources                    active resource catalog (optional
                                                ?skill_id= / ?search= / ?type= filters),
                                                annotated with the student's progress
    GET  /learning/roadmap?career_id=<id>       personalized learning roadmap built
                                                from the student's real skill gaps

Professors / admins can read any student's roadmap:
    GET  /learning/roadmap?career_id=1&student_id=7

All students (only themselves):
    POST   /learning/resources/<id>/complete    mark a resource completed
    DELETE /learning/resources/<id>/complete    un-mark it

Admins maintain the catalog:
    GET/POST       /admin/learning/resources
    GET/PATCH/DELETE /admin/learning/resources/<id>
"""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsVerifiedStudent
from apps.students.models import StudentProfile

from .models import LearningResource, ResourceCompletion
from .serializers import (
    AdminLearningResourceWriteSerializer,
    LearningResourceListSerializer,
)
from .services import build_roadmap

User = get_user_model()


def _resource_queryset(request):
    """Active resources, optionally narrowed by skill / search / type."""
    queryset = LearningResource.objects.filter(is_active=True).select_related("skill")
    params = request.query_params
    skill_id = params.get("skill_id")
    if skill_id:
        queryset = queryset.filter(skill_id=skill_id)
    search = params.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    rtype = params.get("type")
    if rtype:
        queryset = queryset.filter(type=rtype)
    return queryset


class LearningResourceListView(generics.ListAPIView):
    """Browse the active learning catalog (any authenticated user)."""

    serializer_class = LearningResourceListSerializer
    pagination_class = None

    def get_queryset(self):
        return _resource_queryset(self.request)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context["completed_ids"] = set(
                ResourceCompletion.objects.filter(user=self.request.user)
                .values_list("resource_id", flat=True)
            )
        return context


class LearningRoadmapView(APIView):
    """GET /learning/roadmap?career_id=<id> — the student's learning roadmap.

    Built from the student's own skill-gap analysis against the chosen career.
    Students always get their own roadmap; professors/admins pass ?student_id=
    to inspect any student.
    """

    def _resolve_student(self, request):
        student_id = request.query_params.get("student_id")
        if student_id:
            if not (request.user.is_professor or request.user.is_admin_user):
                return None, Response(
                    {"detail": "You can only view your own learning roadmap."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return get_object_or_404(
                User.objects.filter(role=User.Role.STUDENT), pk=student_id
            ), None
        if not request.user.is_student:
            return None, Response(
                {"detail": "A student_id is required for this role."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return request.user, None

    def get(self, request):
        career_id = request.query_params.get("career_id")
        if not career_id:
            return Response(
                {"detail": "A career_id is required to build a roadmap."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.careers.models import Career  # local import avoids cycles

        career = get_object_or_404(Career.objects.filter(is_active=True), pk=career_id)
        student, error = self._resolve_student(request)
        if error is not None:
            return error

        # A student may analyse before completing their profile.
        StudentProfile.objects.get_or_create(user=student)
        data = build_roadmap(student, career)

        # Phase 12: skills the student accepted from rejection feedback join
        # the roadmap too (only when they are still open gaps), and progress
        # counts everything the roadmap actually displays.
        from apps.feedback.services import build_feedback_roadmap

        feedback_data = build_feedback_roadmap(student)
        if feedback_data["skills"]:
            data["feedback_roadmap"] = feedback_data["skills"]
            # A resource recommended for the career and again for a feedback
            # skill is the same item: count unique resources once so ticking
            # one checkbox moves progress by exactly one.
            all_ids = list(
                dict.fromkeys(
                    item["id"]
                    for entry in list(data["roadmap"]) + feedback_data["skills"]
                    for step in entry["steps"]
                    for item in step["items"]
                )
            )
            done = ResourceCompletion.objects.filter(
                user=student, resource_id__in=all_ids
            ).count()
            data["progress"] = {
                "total_resources": len(all_ids),
                "completed_resources": done,
                "remaining_resources": max(0, len(all_ids) - done),
                "progress_percentage": round(done / len(all_ids) * 100) if all_ids else 0,
            }
        return Response(data)


class ResourceCompleteView(APIView):
    """POST/DELETE /learning/resources/<id>/complete — toggle completion.

    Students only, and only for themselves: completion is a personal action.
    """

    permission_classes = [IsVerifiedStudent]

    def _get_resource(self, pk):
        return get_object_or_404(
            LearningResource.objects.filter(is_active=True), pk=pk
        )

    def post(self, request, pk):
        resource = self._get_resource(pk)
        ResourceCompletion.objects.get_or_create(
            user=request.user, resource=resource
        )
        return Response({"id": resource.id, "completed": True})

    def delete(self, request, pk):
        resource = self._get_resource(pk)
        ResourceCompletion.objects.filter(
            user=request.user, resource=resource
        ).delete()
        return Response({"id": resource.id, "completed": False})


# ---------------------------------------------------------------------------
# Admin CRUD
# ---------------------------------------------------------------------------


class AdminLearningResourceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    pagination_class = None

    def get_queryset(self):
        return _resource_queryset(self.request)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return LearningResourceListSerializer
        return AdminLearningResourceWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == "GET":
            context["completed_ids"] = set()  # admin list shows no completion flag
        return context


class AdminLearningResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return LearningResource.objects.select_related("skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return LearningResourceListSerializer
        return AdminLearningResourceWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["completed_ids"] = set()
        return context
