from django.contrib import admin

from apps.skills.models import Skill, UserSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name",)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "proficiency_level", "experience_level", "assessment_score")
    list_filter = ("skill__category", "experience_level")
    search_fields = ("user__username", "skill__name")
