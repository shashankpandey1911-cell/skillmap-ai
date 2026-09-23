from django.contrib import admin

from .models import Career, CareerSkillRequirement


class CareerSkillRequirementInline(admin.TabularInline):
    model = CareerSkillRequirement
    extra = 1


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "salary_range", "skill_count", "is_active")
    search_fields = ("title", "category")
    list_filter = ("category", "is_active")
    inlines = [CareerSkillRequirementInline]

    def skill_count(self, obj: Career) -> int:
        return obj.requirements.count()

    skill_count.short_description = "Required skills"


@admin.register(CareerSkillRequirement)
class CareerSkillRequirementAdmin(admin.ModelAdmin):
    list_display = ("career", "skill", "target_level", "importance")
    list_filter = ("importance",)
    search_fields = ("career__title", "skill__name")
