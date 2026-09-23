from django.contrib import admin

from apps.students.models import Certification, Project, StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "college", "course", "branch", "year", "cgpa")
    search_fields = ("user__username", "user__email", "college", "course")
    list_filter = ("year",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "technologies", "created_at")
    search_fields = ("name", "user__username", "technologies")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "provider", "issued_date")
    search_fields = ("name", "user__username", "provider")
