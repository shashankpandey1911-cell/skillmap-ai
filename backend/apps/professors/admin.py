"""Admin configuration for professor models."""

from django.contrib import admin

from .models import GuidanceNote, RecommendedResource


@admin.register(GuidanceNote)
class GuidanceNoteAdmin(admin.ModelAdmin):
    list_display = ["professor", "student", "title", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["professor__email", "student__email", "title"]


@admin.register(RecommendedResource)
class RecommendedResourceAdmin(admin.ModelAdmin):
    list_display = ["professor", "student", "resource", "created_at"]
    search_fields = ["professor__email", "student__email"]
