"""Student endpoints."""

from django.urls import path

from apps.students import views

urlpatterns = [
    path("students/me", views.StudentMeView.as_view(), name="student-me"),
    path("students/me/projects", views.ProjectListCreateView.as_view(), name="project-list"),
    path("students/me/projects/<int:pk>", views.ProjectDetailView.as_view(), name="project-detail"),
    path(
        "students/me/certifications",
        views.CertificationListCreateView.as_view(),
        name="certification-list",
    ),
    path(
        "students/me/certifications/<int:pk>",
        views.CertificationDetailView.as_view(),
        name="certification-detail",
    ),
    path(
        "students/dashboard-summary",
        views.StudentDashboardSummaryView.as_view(),
        name="student-dashboard-summary",
    ),
]