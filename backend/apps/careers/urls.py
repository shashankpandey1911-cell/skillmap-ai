"""Career catalog and skill gap analysis endpoints (Phase 6)."""

from django.urls import path

from apps.careers import views

urlpatterns = [
    path("careers", views.CareerListView.as_view(), name="career-list"),
    path("careers/matches", views.CareerMatchListView.as_view(), name="career-matches"),
    path("careers/<int:pk>", views.CareerDetailView.as_view(), name="career-detail"),
    path(
        "careers/<int:pk>/gap-analysis",
        views.CareerGapAnalysisView.as_view(),
        name="career-gap-analysis",
    ),
    path(
        "admin/careers",
        views.AdminCareerListCreateView.as_view(),
        name="admin-career-list",
    ),
    path(
        "admin/careers/<int:pk>",
        views.AdminCareerDetailView.as_view(),
        name="admin-career-detail",
    ),
    path(
        "admin/careers/<int:pk>/requirements",
        views.AdminRequirementListCreateView.as_view(),
        name="admin-career-requirements",
    ),
    path(
        "admin/careers/<int:pk>/requirements/<int:req_pk>",
        views.AdminRequirementDetailView.as_view(),
        name="admin-career-requirement-detail",
    ),
]