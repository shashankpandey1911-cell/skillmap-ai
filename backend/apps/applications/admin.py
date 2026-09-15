from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "opportunity", "status", "interview_date", "applied_at")
    list_filter = ("status", "opportunity__opportunity_type")
    search_fields = (
        "student__email",
        "student__first_name",
        "opportunity__title",
        "opportunity__company",
    )
    autocomplete_fields = ["student", "opportunity"]
