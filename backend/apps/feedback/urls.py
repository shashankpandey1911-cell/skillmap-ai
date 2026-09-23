"""Career feedback loop endpoints (Phase 12)."""

from django.urls import path

from apps.feedback import views

urlpatterns = [
    path("feedback", views.MyFeedbackListView.as_view(), name="my-feedback"),
    path(
        "feedback/<int:pk>",
        views.MyFeedbackDetailView.as_view(),
        name="my-feedback-detail",
    ),
    path(
        "feedback/<int:pk>/accept",
        views.FeedbackActionView.as_view(action="accept"),
        name="feedback-accept",
    ),
    path(
        "feedback/<int:pk>/dismiss",
        views.FeedbackActionView.as_view(action="dismiss"),
        name="feedback-dismiss",
    ),
]
