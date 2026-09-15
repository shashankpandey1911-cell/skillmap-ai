"""Application endpoints (Phase 11)."""

from django.urls import path

from apps.applications import views

urlpatterns = [
    path(
        "students/me/applications",
        views.MyApplicationListCreateView.as_view(),
        name="my-applications",
    ),
    path(
        "students/me/applications/<int:pk>",
        views.MyApplicationDetailView.as_view(),
        name="my-application-detail",
    ),
    path(
        "applications",
        views.StudentApplicationsView.as_view(),
        name="student-applications",
    ),
    path(
        "admin/applications",
        views.AdminApplicationListView.as_view(),
        name="admin-application-list",
    ),
    path(
        "admin/applications/<int:pk>",
        views.AdminApplicationDetailView.as_view(),
        name="admin-application-detail",
    ),
]
