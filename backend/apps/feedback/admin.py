from django.contrib import admin

from .models import ApplicationFeedback, FeedbackGap


class FeedbackGapInline(admin.TabularInline):
    model = FeedbackGap
    extra = 0
    readonly_fields = (
        "skill",
        "current_level",
        "required_level",
        "gap_percentage",
        "gap_class",
        "priority",
    )


@admin.register(ApplicationFeedback)
class ApplicationFeedbackAdmin(admin.ModelAdmin):
    list_display = ("student", "kind", "status", "created_at")
    list_filter = ("kind", "status")
    search_fields = (
        "student__email",
        "student__first_name",
        "application__opportunity__title",
        "application__opportunity__company",
    )
    readonly_fields = ("student", "application", "kind", "summary", "created_at")
    inlines = [FeedbackGapInline]