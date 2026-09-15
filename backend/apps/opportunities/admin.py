from django.contrib import admin

from .models import Opportunity, OpportunityRequirement


class OpportunityRequirementInline(admin.TabularInline):
    model = OpportunityRequirement
    extra = 0
    autocomplete_fields = ["skill"]


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "opportunity_type",
        "location",
        "deadline",
        "status",
        "created_at",
    )
    list_filter = ("opportunity_type", "status", "is_remote")
    search_fields = ("title", "company", "description")
    inlines = [OpportunityRequirementInline]
