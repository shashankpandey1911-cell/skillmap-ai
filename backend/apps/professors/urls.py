"""Professor endpoints (Phase 14)."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "professors/students",
        views.ProfessorStudentListView.as_view(),
        name="professor-student-list",
    ),
    path(
        "professors/students/<int:pk>/dossier",
        views.ProfessorStudentDossierView.as_view(),
        name="professor-student-dossier",
    ),
    path(
        "professors/students/<int:pk>/guidance",
        views.ProfessorStudentGuidanceView.as_view(),
        name="professor-student-guidance",
    ),
    path(
        "professors/guidance/<int:pk>",
        views.ProfessorGuidanceDeleteView.as_view(),
        name="professor-guidance-delete",
    ),
    path(
        "professors/analytics",
        views.ProfessorAnalyticsView.as_view(),
        name="professor-analytics",
    ),
]
