"""Serializers for professor endpoints (Phase 14)."""

from rest_framework import serializers

from apps.users.models import User


class StudentListSerializer(serializers.ModelSerializer):
    """Minimal student info for the professor's student list."""

    full_name = serializers.SerializerMethodField()
    profile_completeness = serializers.SerializerMethodField()
    skills_count = serializers.SerializerMethodField()
    career_readiness = serializers.SerializerMethodField()

    college = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "college",
            "course",
            "branch",
            "year",
            "profile_completeness",
            "skills_count",
            "career_readiness",
            "date_joined",
        ]

    def get_college(self, obj):
        from apps.students.models import StudentProfile
        profile, _ = StudentProfile.objects.get_or_create(user=obj)
        return profile.college

    def get_course(self, obj):
        from apps.students.models import StudentProfile
        profile, _ = StudentProfile.objects.get_or_create(user=obj)
        return profile.course

    def get_branch(self, obj):
        from apps.students.models import StudentProfile
        profile, _ = StudentProfile.objects.get_or_create(user=obj)
        return profile.branch

    def get_year(self, obj):
        from apps.students.models import StudentProfile
        profile, _ = StudentProfile.objects.get_or_create(user=obj)
        return profile.year

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_profile_completeness(self, obj):
        from apps.students.models import StudentProfile
        from apps.students.services import profile_completeness

        profile, _ = StudentProfile.objects.get_or_create(user=obj)
        return profile_completeness(profile)

    def get_skills_count(self, obj):
        from apps.skills.models import UserSkill

        return UserSkill.objects.filter(user=obj).count()

    def get_career_readiness(self, obj):
        from apps.skills.models import UserSkill
        from apps.careers.models import Career, CareerSkillRequirement
        from apps.core.services.gap import compute_gaps, readiness_score

        user_skills = UserSkill.objects.filter(user=obj).select_related("skill")
        skill_scores = {us.skill_id: us.proficiency_level * 20 for us in user_skills}

        career = Career.objects.filter(is_active=True).first()
        if not career:
            return 0

        requirements = CareerSkillRequirement.objects.filter(career=career).select_related("skill")
        if not requirements:
            return 0

        gaps = compute_gaps(skill_scores, requirements, career.title)
        return round(readiness_score(gaps))


class StudentDossierSerializer(serializers.ModelSerializer):
    """Full student dossier for professor view."""

    full_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    assessment_results = serializers.SerializerMethodField()
    skill_gaps = serializers.SerializerMethodField()
    career_readiness = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "phone",
            "profile",
            "skills",
            "assessment_results",
            "skill_gaps",
            "career_readiness",
            "projects",
            "certifications",
            "applications",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_profile(self, obj):
        from apps.students.models import StudentProfile
        from apps.students.services import profile_completeness

        profile, _ = StudentProfile.objects.get_or_create(user=obj)
        completeness = profile_completeness(profile)
        return {
            "college": profile.college,
            "course": profile.course,
            "branch": profile.branch,
            "year": profile.year,
            "cgpa": profile.cgpa,
            "semester": profile.semester,
            "achievements": profile.achievements,
            "career_goal": profile.career_goal,
            "preferred_domain": profile.preferred_domain,
            "interests": profile.interests,
            "about": profile.about,
            "linkedin_url": profile.linkedin_url,
            "github_url": profile.github_url,
            "completeness": completeness,
        }

    def get_skills(self, obj):
        from apps.skills.models import UserSkill

        skills = UserSkill.objects.filter(user=obj).select_related("skill")
        return [
            {
                "name": us.skill.name,
                "category": us.skill.category,
                "proficiency_level": us.proficiency_level,
                "proficiency_percent": us.proficiency_level * 20,
                "experience_level": us.experience_level,
                "assessment_score": us.assessment_score,
            }
            for us in skills
        ]

    def get_assessment_results(self, obj):
        from apps.assessments.models import StudentAttempt, Question

        attempts = StudentAttempt.objects.filter(
            user=obj, status=StudentAttempt.Status.SUBMITTED
        ).select_related("assessment")

        results = []
        for attempt in attempts:
            total = Question.objects.filter(assessment=attempt.assessment).count()
            correct = attempt.score if hasattr(attempt, "score") else 0
            results.append(
                {
                    "assessment_title": attempt.assessment.title,
                    "score": attempt.score,
                    "total_questions": total,
                    "percentage": round(attempt.score / total * 100) if total > 0 else 0,
                    "completed_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                }
            )
        return results

    def get_skill_gaps(self, obj):
        from apps.skills.models import UserSkill
        from apps.careers.models import Career, CareerSkillRequirement
        from apps.core.services.gap import compute_gaps

        user_skills = UserSkill.objects.filter(user=obj).select_related("skill")
        skill_scores = {us.skill_id: us.proficiency_level * 20 for us in user_skills}

        career = Career.objects.filter(is_active=True).first()
        if not career:
            return []

        requirements = CareerSkillRequirement.objects.filter(career=career).select_related("skill")
        gaps = compute_gaps(skill_scores, requirements, career.title)

        return [
            {
                "skill_name": g.skill_name,
                "category": g.category,
                "current_level": g.current_level,
                "required_level": g.required_level,
                "gap_percentage": g.gap_percentage,
                "gap_class": g.gap_class,
                "priority": g.priority,
                "recommended_action": g.recommended_action,
            }
            for g in gaps
            if g.gap_class != "NONE"
        ]

    def get_career_readiness(self, obj):
        from apps.skills.models import UserSkill
        from apps.careers.models import Career, CareerSkillRequirement
        from apps.core.services.gap import compute_gaps, readiness_score

        user_skills = UserSkill.objects.filter(user=obj).select_related("skill")
        skill_scores = {us.skill_id: us.proficiency_level * 20 for us in user_skills}

        career = Career.objects.filter(is_active=True).first()
        if not career:
            return 0

        requirements = CareerSkillRequirement.objects.filter(career=career).select_related("skill")
        if not requirements:
            return 0

        gaps = compute_gaps(skill_scores, requirements, career.title)
        return round(readiness_score(gaps))

    def get_projects(self, obj):
        from apps.students.models import Project

        projects = Project.objects.filter(user=obj)
        return [
            {
                "name": p.name,
                "description": p.description,
                "technologies": p.technologies,
                "github_url": p.github_url,
                "demo_url": p.demo_url,
            }
            for p in projects
        ]

    def get_certifications(self, obj):
        from apps.students.models import Certification

        certs = Certification.objects.filter(user=obj)
        return [
            {
                "name": c.name,
                "provider": c.provider,
                "issued_date": c.issued_date.isoformat() if c.issued_date else None,
                "credential_url": c.credential_url,
            }
            for c in certs
        ]

    def get_applications(self, obj):
        from apps.applications.models import Application

        apps = Application.objects.filter(student=obj).select_related("opportunity")
        return [
            {
                "opportunity_title": a.opportunity.title,
                "company": a.opportunity.company,
                "status": a.status,
                "applied_at": a.applied_at.isoformat(),
                "interview_date": a.interview_date.isoformat() if a.interview_date else None,
            }
            for a in apps
        ]


class GuidanceNoteSerializer(serializers.ModelSerializer):
    """Serializer for professor guidance notes."""

    professor_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        from apps.professors.models import GuidanceNote
        model = GuidanceNote
        fields = [
            "id",
            "professor_name",
            "student_name",
            "title",
            "message",
            "category",
            "created_at",
            "updated_at",
        ]

    def get_professor_name(self, obj):
        return obj.professor.get_full_name() or obj.professor.username

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username


class GuidanceNoteCreateSerializer(serializers.Serializer):
    """Serializer for creating guidance notes."""

    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    category = serializers.ChoiceField(
        choices=[
            ("ACADEMIC", "Academic"),
            ("CAREER", "Career"),
            ("SKILL", "Skill Development"),
            ("GENERAL", "General"),
        ],
        default="GENERAL",
    )


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for professor analytics."""

    total_students = serializers.IntegerField()
    career_ready_students = serializers.IntegerField()
    students_with_gaps = serializers.IntegerField()
    avg_assessment_score = serializers.FloatField()
    popular_career_goals = serializers.ListField()
    common_skill_gaps = serializers.ListField()
    students_by_year = serializers.ListField()
    readiness_distribution = serializers.ListField()
