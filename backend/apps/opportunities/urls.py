"""Opportunity endpoints (Phase 9)."""

from django.urls import path

from apps.opportunities import views

urlpatterns = [
    path("opportunities", views.OpportunityListView.as_view(), name="opportunity-list"),
    path(
        "opportunities/recommendations",
        views.OpportunityRecommendationsView.as_view(),
        name="opportunity-recommendations",
    ),
    path(
        "opportunities/<int:pk>",
        views.OpportunityDetailView.as_view(),
        name="opportunity-detail",
    ),
    path(
        "admin/opportunities",
        views.AdminOpportunityListCreateView.as_view(),
        name="admin-opportunity-list",
    ),
    path(
        "admin/opportunities/<int:pk>",
        views.AdminOpportunityDetailView.as_view(),
        name="admin-opportunity-detail",
    ),
    path(
        "admin/opportunities/<int:pk>/activate",
        views.AdminOpportunityActivateView.as_view(),
        name="admin-opportunity-activate",
    ),
    path(
        "admin/opportunities/<int:pk>/deactivate",
        views.AdminOpportunityDeactivateView.as_view(),
        name="admin-opportunity-deactivate",
    ),
    path(
        "admin/opportunities/<int:pk>/requirements",
        views.AdminRequirementListCreateView.as_view(),
        name="admin-opportunity-requirements",
    ),
    path(
        "admin/opportunities/<int:pk>/requirements/<int:req_pk>",
        views.AdminRequirementDetailView.as_view(),
        name="admin-opportunity-requirement-detail",
    ),
]
