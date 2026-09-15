"""AI assistant URL patterns.

Routes under /api/v1/:
    GET  ai/status                      is AI provider configured?
    POST ai/extract-resume              extract skills from resume text
    POST ai/approve-extraction          save approved extracted data
    POST ai/career-recommendation       AI career suggestions
    POST ai/learning-recommendation     AI learning roadmap
    POST ai/opportunity-explanation     AI explanation for an opportunity
"""

from django.urls import path

from . import views

urlpatterns = [
    path("ai/status", views.AIStatusView.as_view(), name="ai-status"),
    path(
        "ai/extract-resume",
        views.ResumeExtractView.as_view(),
        name="ai-extract-resume",
    ),
    path(
        "ai/approve-extraction",
        views.ResumeApproveView.as_view(),
        name="ai-approve-extraction",
    ),
    path(
        "ai/career-recommendation",
        views.AICareerRecommendationView.as_view(),
        name="ai-career-recommendation",
    ),
    path(
        "ai/learning-recommendation",
        views.AILearningRecommendationView.as_view(),
        name="ai-learning-recommendation",
    ),
    path(
        "ai/opportunity-explanation",
        views.AIOpportunityExplanationView.as_view(),
        name="ai-opportunity-explanation",
    ),
]
