"""Assessment endpoints under /api/v1/."""

from django.urls import path

from apps.assessments import views

urlpatterns = [
    path("assessments", views.AssessmentListView.as_view(), name="assessment-list"),
    path(
        "assessments/<int:pk>",
        views.AssessmentDetailView.as_view(),
        name="assessment-detail",
    ),
    path(
        "assessments/<int:pk>/start",
        views.StartAttemptView.as_view(),
        name="assessment-start",
    ),
    path(
        "assessments/<int:pk>/submit",
        views.SubmitAttemptView.as_view(),
        name="assessment-submit",
    ),
    path(
        "students/me/assessment-results",
        views.MyResultsView.as_view(),
        name="my-assessment-results",
    ),
    path(
        "admin/assessments",
        views.AdminAssessmentListCreateView.as_view(),
        name="admin-assessment-list",
    ),
    path(
        "admin/assessments/<int:pk>",
        views.AdminAssessmentDetailView.as_view(),
        name="admin-assessment-detail",
    ),
    path(
        "admin/assessments/<int:pk>/questions",
        views.AdminQuestionListCreateView.as_view(),
        name="admin-question-list",
    ),
    path(
        "admin/questions/<int:pk>",
        views.AdminQuestionDetailView.as_view(),
        name="admin-question-detail",
    ),
]
