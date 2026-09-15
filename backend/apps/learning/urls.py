"""Learning content and roadmap endpoints (Phase 8)."""

from django.urls import path

from apps.learning import views

urlpatterns = [
    path(
        "learning/resources",
        views.LearningResourceListView.as_view(),
        name="learning-resource-list",
    ),
    path(
        "learning/roadmap",
        views.LearningRoadmapView.as_view(),
        name="learning-roadmap",
    ),
    path(
        "learning/resources/<int:pk>/complete",
        views.ResourceCompleteView.as_view(),
        name="learning-resource-complete",
    ),
    path(
        "admin/learning/resources",
        views.AdminLearningResourceListCreateView.as_view(),
        name="admin-learning-resource-list",
    ),
    path(
        "admin/learning/resources/<int:pk>",
        views.AdminLearningResourceDetailView.as_view(),
        name="admin-learning-resource-detail",
    ),
]
