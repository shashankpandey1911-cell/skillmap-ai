"""Analytics endpoints (read-only aggregations)."""

from django.urls import path

from apps.analytics import views

urlpatterns = [
    path(
        "professors/dashboard-summary",
        views.ProfessorDashboardSummaryView.as_view(),
        name="professor-dashboard-summary",
    ),
    path(
        "admin/dashboard-summary",
        views.AdminDashboardSummaryView.as_view(),
        name="admin-dashboard-summary",
    ),
]
