"""SkillMap AI — root URL configuration.

All API endpoints live under /api/v1/. Each Django app owns its own url module
and is mounted here, so the API stays modular as features are added.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

api_v1 = [
    path("auth/", include("apps.users.urls")),
    path("", include("apps.students.urls")),
    path("", include("apps.skills.urls")),
    path("", include("apps.assessments.urls")),
    path("", include("apps.careers.urls")),
    path("", include("apps.opportunities.urls")),
    path("", include("apps.applications.urls")),
    path("", include("apps.feedback.urls")),
    path("", include("apps.learning.urls")),
    path("", include("apps.recommendations.urls")),
    path("", include("apps.analytics.urls")),
    path("", include("apps.professors.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.admins.urls")),
    path("", include("apps.ai_assistant.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
