"""Admin URL patterns."""

from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path("admin/dashboard-summary", views.AdminDashboardSummaryView.as_view(), name="admin-dashboard-summary"),

    # Users
    path("admin/users", views.AdminUserListView.as_view(), name="admin-users"),
    path("admin/users/create", views.AdminUserCreateView.as_view(), name="admin-user-create"),
    path("admin/users/<int:pk>", views.AdminUserDetailView.as_view(), name="admin-user-detail"),
    path(
        "admin/users/<int:pk>/change-password",
        views.AdminUserChangePasswordView.as_view(),
        name="admin-user-change-password",
    ),

    # Skills
    path("admin/skills", views.AdminSkillListView.as_view(), name="admin-skills"),
    path("admin/skills/<int:pk>", views.AdminSkillDetailView.as_view(), name="admin-skill-detail"),

    # Careers
    path("admin/careers", views.AdminCareerListView.as_view(), name="admin-careers"),
    path("admin/careers/<int:pk>", views.AdminCareerDetailView.as_view(), name="admin-career-detail"),

    # Assessments
    path("admin/assessments", views.AdminAssessmentListView.as_view(), name="admin-assessments"),
    path("admin/assessments/<int:pk>", views.AdminAssessmentDetailView.as_view(), name="admin-assessment-detail"),

    # Opportunities
    path("admin/opportunities", views.AdminOpportunityListView.as_view(), name="admin-opportunities"),
    path("admin/opportunities/<int:pk>", views.AdminOpportunityDetailView.as_view(), name="admin-opportunity-detail"),

    # Learning Resources
    path("admin/resources", views.AdminLearningResourceListView.as_view(), name="admin-resources"),
    path("admin/resources/<int:pk>", views.AdminLearningResourceDetailView.as_view(), name="admin-resource-detail"),

    # Applications
    path("admin/applications", views.AdminApplicationListView.as_view(), name="admin-applications"),

    # Notifications
    path("admin/notifications/send", views.AdminNotificationCreateView.as_view(), name="admin-notification-send"),

    # Analytics
    path("admin/analytics", views.AdminAnalyticsView.as_view(), name="admin-analytics"),
]
