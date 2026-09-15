"""Skill endpoints."""

from django.urls import path

from apps.skills import views

urlpatterns = [
    path("skills/catalog", views.SkillCatalogView.as_view(), name="skill-catalog"),
    path("students/me/skills", views.UserSkillListCreateView.as_view(), name="user-skill-list"),
    path("students/me/skills/<int:pk>", views.UserSkillDetailView.as_view(), name="user-skill-detail"),
]