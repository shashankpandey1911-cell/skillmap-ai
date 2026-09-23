"""Student endpoints: profile (me), projects and certifications CRUD."""

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessments.models import StudentAttempt
from apps.core.permissions import IsVerifiedStudent
from apps.skills.models import UserSkill
from apps.users.serializers import UserSerializer

from .models import Certification, Project, StudentProfile
from .serializers import (
    CertificationSerializer,
    ProjectSerializer,
    StudentProfileSerializer,
    StudentProfileUpdateSerializer,
)
from .services import profile_completeness, profile_completeness_sections


def _me_payload(user) -> dict:
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return {
        "user": UserSerializer(user).data,
        "profile": StudentProfileSerializer(profile).data,
        "completeness": profile_completeness_sections(profile),
    }


class StudentMeView(APIView):
    """GET/PATCH the authenticated student's digital career profile."""

    permission_classes = [IsVerifiedStudent]

    def get(self, request):
        return Response(_me_payload(request.user))

    def patch(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        serializer = StudentProfileUpdateSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # serializer.update() wrote through a separate ORM fetch; reload the
        # request user so the response reflects the persisted values.
        request.user.refresh_from_db()
        return Response(_me_payload(request.user))


class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsVerifiedStudent]
    serializer_class = ProjectSerializer
    pagination_class = None  # a student's own projects: plain list

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Owner-scoped: other students' projects are indistinguishable from 404."""

    permission_classes = [IsVerifiedStudent]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class CertificationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsVerifiedStudent]
    serializer_class = CertificationSerializer
    pagination_class = None

    def get_queryset(self):
        return Certification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CertificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsVerifiedStudent]
    serializer_class = CertificationSerializer

    def get_queryset(self):
        return Certification.objects.filter(user=self.request.user)


class StudentDashboardSummaryView(APIView):
    """Comprehensive student dashboard data."""

    permission_classes = [IsVerifiedStudent]

    def get(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        from apps.applications.models import Application
        from apps.feedback.models import ApplicationFeedback
        from apps.careers.models import Career, CareerSkillRequirement
        from apps.core.services.gap import compute_gaps, readiness_score
        from apps.core.services.matching import career_match
        from apps.opportunities.models import Opportunity, OpportunityRequirement
        from apps.learning.models import ResourceCompletion, LearningResource
        from django.db.models import Count, Q
        from datetime import timedelta
        from django.utils import timezone

        user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')
        # skill_scores keyed by skill_id for compute_gaps; name-keyed for matching
        skill_scores_by_id = {us.skill_id: us.proficiency_level * 20 for us in user_skills}
        skill_scores = {us.skill.name: us.proficiency_level * 20 for us in user_skills}
        projects = Project.objects.filter(user=request.user)

        # Career readiness: use first active career if profile has a goal
        career_readiness = 0
        top_career_match = None
        active_careers = Career.objects.filter(is_active=True)[:5]
        career_requirements_qs = None
        if active_careers:
            career = active_careers[0]
            career_requirements_qs = CareerSkillRequirement.objects.filter(career=career).select_related('skill')
            gaps = compute_gaps(skill_scores_by_id, career_requirements_qs, career.title)
            career_readiness = round(readiness_score(gaps))
            match_result = career_match(career, career_requirements_qs, skill_scores_by_id, profile, projects)
            top_career_match = {
                'title': career.title,
                'match_percentage': match_result['match_percentage'],
                'matching_skills': match_result['matching_skills'][:3],
            }

        # Top skills by proficiency
        top_skills = [
            {'name': us.skill.name, 'proficiency': us.proficiency_level * 20, 'category': us.skill.category}
            for us in user_skills.order_by('-proficiency_level')[:5]
        ]

        # Skill gaps count (across first active career)
        skill_gaps_count = 0
        if career_requirements_qs is not None:
            gaps = compute_gaps(skill_scores_by_id, career_requirements_qs, career.title)
            skill_gaps_count = sum(1 for g in gaps if g.gap_class in ('LOW', 'MEDIUM', 'HIGH'))

        # Career matches count
        career_matches_count = Career.objects.filter(is_active=True).count()

        # Recommended opportunities (top 3 by match)
        opps = Opportunity.objects.filter(status=Opportunity.Status.ACTIVE).prefetch_related('requirements__skill')[:10]
        opp_matches = []
        for opp in opps:
            opp_reqs = {r.skill.name: r.min_level for r in opp.requirements.all()}
            if not opp_reqs:
                continue
            matching = sum(1 for s, l in opp_reqs.items() if skill_scores.get(s, 0) >= l)
            match_pct = round(matching / len(opp_reqs) * 100) if opp_reqs else 0
            opp_matches.append({'id': opp.id, 'title': opp.title, 'company': opp.company, 'match_percentage': match_pct})
        opp_matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        top_opportunities = opp_matches[:3]
        opportunities_count = len(opp_matches)

        # Learning progress
        total_resources = LearningResource.objects.filter(is_active=True).count()
        completed_resources = ResourceCompletion.objects.filter(user=request.user).count()
        learning_progress = round(completed_resources / total_resources * 100) if total_resources > 0 else 0

        # Applications by status
        apps_qs = Application.objects.filter(student=request.user)
        apps_by_status = dict(apps_qs.values_list('status').annotate(count=Count('id')).values_list('status', 'count'))
        applications_count = apps_qs.count()

        # Upcoming deadlines (next 5 closing opportunities)
        now = timezone.now()
        upcoming = Opportunity.objects.filter(
            status=Opportunity.Status.ACTIVE,
            deadline__gte=now
        ).order_by('deadline')[:5]
        upcoming_deadlines = [
            {'id': o.id, 'title': o.title, 'company': o.company, 'deadline': o.deadline.isoformat() if o.deadline else None}
            for o in upcoming
        ]

        # Achievements
        selected = ApplicationFeedback.objects.filter(
            student=request.user, kind=ApplicationFeedback.Kind.SELECTED
        ).select_related('application__opportunity')

        return Response({
            'profile_completeness': profile_completeness(profile),
            'skills_count': user_skills.count(),
            'assessments_taken': StudentAttempt.objects.filter(
                user=request.user, status=StudentAttempt.Status.SUBMITTED
            ).count(),
            'applications_count': applications_count,
            'career_readiness': career_readiness,
            'top_skills': top_skills,
            'skill_gaps_count': skill_gaps_count,
            'career_matches_count': career_matches_count,
            'top_career_match': top_career_match,
            'opportunities_count': opportunities_count,
            'top_opportunities': top_opportunities,
            'learning_progress': learning_progress,
            'completed_resources': completed_resources,
            'total_resources': total_resources,
            'applications_by_status': apps_by_status,
            'upcoming_deadlines': upcoming_deadlines,
            'achievements_count': selected.count(),
            'feedback_pending_count': ApplicationFeedback.objects.filter(
                student=request.user,
                kind=ApplicationFeedback.Kind.REJECTED,
                status=ApplicationFeedback.Status.PENDING,
            ).count(),
            'recent_achievements': [
                {
                    'feedback_id': feedback.id,
                    'title': feedback.application.opportunity.title,
                    'company': feedback.application.opportunity.company,
                    'opportunity_type': feedback.application.opportunity.opportunity_type,
                    'achieved_at': feedback.created_at.isoformat(),
                }
                for feedback in selected[:5]
            ],
        })
