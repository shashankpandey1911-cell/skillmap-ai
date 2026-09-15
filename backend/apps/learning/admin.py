from django.contrib import admin

from .models import LearningResource, ResourceCompletion


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "type", "level", "is_active")
    list_filter = ("type", "level", "is_active", "skill")
    search_fields = ("title", "description", "skill__name")


@admin.register(ResourceCompletion)
class ResourceCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "resource", "completed_at")
    search_fields = ("user__email", "resource__title")
