"""Career feedback loop endpoints (Phase 12).

Students:
    GET   /feedback                       own feedback (kind/status filters)
    GET   /feedback/<id>                  own feedback detail
    PATCH /feedback/<id>                  own notes only
    POST  /feedback/<id>/accept           add rejection gaps to my roadmap
    POST  /feedback/<id>/dismiss          set the feedback aside

Professors / admins can read one student's feedback:
    GET   /feedback?student_id=<id>
"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApplicationFeedback
from .serializers import (
    FeedbackNotesWriteSerializer,
    FeedbackSerializer,
)

User = get_user_model()


def _feedback_queryset():
    return ApplicationFeedback.objects.select_related(
        "application__opportunity"
    ).prefetch_related("gaps__skill")


class MyFeedbackListView(APIView):
    """GET /feedback — own feedback; professors/admins pass ?student_id=."""

    def get(self, request):
        if request.user.is_student:
            target = request.user
        elif request.user.is_professor or request.user.is_admin_user:
            student_id = request.query_params.get("student_id", "").strip()
            if not student_id:
                return Response(
                    {"detail": "A student_id query parameter is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            target = get_object_or_404(
                User.objects.filter(role=User.Role.STUDENT), pk=student_id
            )
        else:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        queryset = _feedback_queryset().filter(student=target)

        kind = request.query_params.get("kind", "").strip()
        if kind:
            if kind not in ApplicationFeedback.Kind.values:
                return Response(
                    {"detail": f"Unknown kind '{kind}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(kind=kind)
        fb_status = request.query_params.get("status", "").strip()
        if fb_status:
            if fb_status not in ApplicationFeedback.Status.values:
                return Response(
                    {"detail": f"Unknown status '{fb_status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(status=fb_status)
        return Response(FeedbackSerializer(queryset, many=True).data)


class MyFeedbackDetailView(APIView):
    """GET / PATCH one feedback — owner only; students edit notes only."""

    def _owned(self, request, pk):
        if not request.user.is_student:
            return None
        return get_object_or_404(
            ApplicationFeedback.objects.filter(student=request.user), pk=pk
        )

    def get(self, request, pk):
        feedback = self._owned(request, pk)
        if feedback is None:
            return Response(
                {"detail": "Only students can view their own career feedback."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(FeedbackSerializer(feedback).data)

    def patch(self, request, pk):
        if not request.user.is_student:
            return Response(
                {"detail": "Only students can edit their own career feedback."},
                status=status.HTTP_403_FORBIDDEN,
            )
        feedback = get_object_or_404(
            ApplicationFeedback.objects.filter(student=request.user), pk=pk
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
        serializer = FeedbackNotesWriteSerializer(
            feedback, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(FeedbackSerializer(feedback).data)


class FeedbackActionView(APIView):
    """POST /feedback/<id>/accept | /dismiss — the student's decision.

    Only rejection feedback can be acted on, and only by the student it
    belongs to. Accepting adds the gap skills to the learning roadmap;
    dismissing sets the feedback aside. Nothing is ever auto-changed.
    """

    action = "accept"

    def post(self, request, pk):
        if not request.user.is_student:
            return Response(
                {"detail": "Only students can act on their own career feedback."},
                status=status.HTTP_403_FORBIDDEN,
            )
        feedback = get_object_or_404(
            ApplicationFeedback.objects.filter(student=request.user), pk=pk
        )
        if feedback.kind != ApplicationFeedback.Kind.REJECTED:
            return Response(
                {"detail": "Only rejection feedback can be accepted or dismissed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if self.action == "accept":
            feedback.status = ApplicationFeedback.Status.ACCEPTED
        else:  # dismiss
            feedback.status = ApplicationFeedback.Status.DISMISSED
        feedback.save()
        return Response(FeedbackSerializer(feedback).data)
