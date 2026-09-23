"""Assessment endpoints.

Students:
    GET    /assessments                     published assessments + my stats
    GET    /assessments/<id>                one assessment
    POST   /assessments/<id>/start          start (or resume) an attempt
    POST   /assessments/<id>/submit         score + persist result + skill
    GET    /students/me/assessment-results  my past results (with reviews)

Admins (build the bank; students never see correct answers pre-submit):
    GET/POST   /admin/assessments
    GET/PATCH/DELETE /admin/assessments/<id>
    GET/POST   /admin/assessments/<id>/questions
    GET/PATCH/DELETE /admin/questions/<id>
"""

from collections import Counter

from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsVerifiedStudent

from .models import Assessment, AssessmentResult, Question, StudentAttempt
from .serializers import (
    AdminAssessmentReadSerializer,
    AdminAssessmentWriteSerializer,
    AdminQuestionReadSerializer,
    AdminQuestionWriteSerializer,
    AssessmentPublicSerializer,
    AssessmentResultSerializer,
    QuestionPublicSerializer,
    SubmitAttemptSerializer,
)
from .services import submit_attempt


def _attempt_stats(user) -> tuple[dict[int, float], dict[int, int]]:
    """Per-assessment {last score, attempt count} for the student."""
    attempts = StudentAttempt.objects.filter(
        user=user, status=StudentAttempt.Status.SUBMITTED
    ).order_by("-submitted_at")
    last_scores: dict[int, float] = {}
    counts: dict[int, int] = Counter()
    for attempt in attempts:
        counts[attempt.assessment_id] += 1
        if attempt.assessment_id not in last_scores and attempt.score is not None:
            last_scores[attempt.assessment_id] = float(attempt.score)
    return last_scores, counts


def _public_context(user) -> dict:
    last_scores, counts = _attempt_stats(user)
    return {"last_scores": last_scores, "attempt_counts": dict(counts)}


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------


class AssessmentListView(generics.ListAPIView):
    """Published assessments the student can take, with their own stats."""

    permission_classes = [IsVerifiedStudent]
    serializer_class = AssessmentPublicSerializer
    pagination_class = None

    def get_queryset(self):
        return Assessment.objects.filter(is_published=True).select_related("skill")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(_public_context(self.request.user))
        return context


class AssessmentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsVerifiedStudent]
    serializer_class = AssessmentPublicSerializer

    def get_queryset(self):
        return Assessment.objects.filter(is_published=True).select_related("skill")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(_public_context(self.request.user))
        return context


class StartAttemptView(APIView):
    """POST start: create a new attempt or resume the in-progress one.

    Response includes the question bank *without* correct answers — those are
    only revealed in the post-submission result.
    """

    permission_classes = [IsVerifiedStudent]

    def post(self, request, pk):
        assessment = get_object_or_404(
            Assessment.objects.filter(is_published=True), pk=pk
        )
        attempt, _ = StudentAttempt.objects.get_or_create(
            user=request.user,
            assessment=assessment,
            status=StudentAttempt.Status.IN_PROGRESS,
        )
        questions = list(
            assessment.questions.prefetch_related("options").order_by("order", "id")
        )
        data = {
            "attempt": {
                "id": attempt.id,
                "status": attempt.status,
                "started_at": attempt.started_at,
            },
            "assessment": AssessmentPublicSerializer(
                assessment, context=_public_context(request.user)
            ).data,
            "questions": QuestionPublicSerializer(questions, many=True).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class SubmitAttemptView(APIView):
    """POST submit: score the run, persist the result, update the skill."""

    permission_classes = [IsVerifiedStudent]

    def post(self, request, pk):
        payload = SubmitAttemptSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        attempt = StudentAttempt.objects.filter(
            user=request.user,
            assessment_id=pk,
            pk=payload.validated_data["attempt_id"],
        ).first()
        if attempt is None:
            return Response(
                {"detail": "Attempt not found for this assessment."},
                status=status.HTTP_404_NOT_FOUND,
            )
        result = submit_attempt(
            request.user, attempt, payload.validated_data["answers"]
        )
        return Response(
            AssessmentResultSerializer(
                result, context=_public_context(request.user)
            ).data,
            status=status.HTTP_200_OK,
        )


class MyResultsView(generics.ListAPIView):
    """The student's completed assessments, newest first, with reviews."""

    permission_classes = [IsVerifiedStudent]
    serializer_class = AssessmentResultSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            AssessmentResult.objects.filter(attempt__user=self.request.user)
            .select_related("attempt", "assessment", "assessment__skill")
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(_public_context(self.request.user))
        return context


# ---------------------------------------------------------------------------
# Admins
# ---------------------------------------------------------------------------


class AdminAssessmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    pagination_class = None

    def get_queryset(self):
        return Assessment.objects.select_related("skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminAssessmentReadSerializer
        return AdminAssessmentWriteSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AdminAssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Assessment.objects.select_related("skill")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminAssessmentReadSerializer
        return AdminAssessmentWriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": "This assessment has student attempts and cannot be "
                    "deleted. Unpublish it instead."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminQuestionListCreateView(generics.ListCreateAPIView):
    """Questions under one assessment; creation accepts nested options."""

    permission_classes = [IsAdmin]
    pagination_class = None

    def get_queryset(self):
        return Question.objects.filter(assessment_id=self.kwargs["pk"])

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminQuestionReadSerializer
        return AdminQuestionWriteSerializer

    def perform_create(self, serializer):
        assessment = get_object_or_404(Assessment, pk=self.kwargs["pk"])
        serializer.save(assessment=assessment)


class AdminQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = Question.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminQuestionReadSerializer
        return AdminQuestionWriteSerializer
