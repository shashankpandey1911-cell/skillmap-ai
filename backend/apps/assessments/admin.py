from django.contrib import admin

from .models import Assessment, AssessmentResult, Option, Question, StudentAnswer, StudentAttempt


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    show_change_link = True


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ("question", "selected_option", "is_correct")


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "difficulty", "question_count", "is_published")
    list_filter = ("is_published", "difficulty", "skill")
    search_fields = ("title", "skill__name")
    autocomplete_fields = ("skill",)
    inlines = [QuestionInline]

    @admin.display(description="Questions")
    def question_count(self, obj):
        return obj.questions.count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "marks", "order")
    search_fields = ("text", "assessment__title")
    list_filter = ("assessment",)
    inlines = [OptionInline]


@admin.register(StudentAttempt)
class StudentAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "assessment", "status", "score", "submitted_at")
    list_filter = ("status", "assessment")
    search_fields = ("user__email", "assessment__title")
    inlines = [StudentAnswerInline]


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ("assessment", "attempt", "score", "correct_count", "total_questions", "created_at")
    list_filter = ("assessment",)
