"""Admin views — CRUD for every platform entity + analytics."""

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.skills.models import Skill
from apps.assessments.models import Assessment, Question
from apps.careers.models import Career, CareerSkillRequirement
from apps.learning.models import LearningResource
from apps.opportunities.models import Opportunity, OpportunityRequirement
from apps.applications.models import Application
from apps.skills.models import UserSkill

from .serializers import (
    AdminAnalyticsSerializer,
    AdminAssessmentDetailSerializer,
    AdminAssessmentSerializer,
    AdminCareerSerializer,
    AdminChangePasswordSerializer,
    AdminLearningResourceSerializer,
    AdminOpportunitySerializer,
    AdminSkillSerializer,
    AdminUserCreateSerializer,
    AdminUserSerializer,
)

User = get_user_model()


# ─── Dashboard summary ────────────────────────────────────────────────────
class AdminDashboardSummaryView(APIView):
    """Quick counts for the admin overview cards."""
    permission_classes = [IsAdmin]

    def get(self, _request):
        return Response({
            "total_users": User.objects.count(),
            "students": User.objects.filter(role="STUDENT").count(),
            "professors": User.objects.filter(role="PROFESSOR").count(),
            "admins": User.objects.filter(role="ADMIN").count(),
        })


# ─── Users ────────────────────────────────────────────────────────────────
class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        qs = User.objects.all().order_by("-date_joined")
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(email__icontains=search)
                | Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ("true", "1"))
        return qs


class AdminUserCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        ser = AdminUserCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(AdminUserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()

    def partial_update(self, request, *args, **kwargs):
        """Allow toggling active, changing role."""
        user = self.get_object()
        if "role" in request.data:
            user.role = request.data["role"]
        if "is_active" in request.data:
            user.is_active = request.data["is_active"]
        if "phone" in request.data:
            user.phone = request.data["phone"]
        user.save()
        return Response(AdminUserSerializer(user).data)


class AdminUserChangePasswordView(APIView):
    """Admin-initiated password reset for any user.

    Only authenticated admins may call this endpoint. The password is hashed
    with Django's default algorithm (PBKDF2) via ``set_password()`` and Django's
    password validators are enforced before storage. The user's username, email,
    role and other fields are not touched.
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if user is None:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Password updated successfully. The new password is now active."},
            status=status.HTTP_200_OK,
        )


# ─── Skills ───────────────────────────────────────────────────────────────
class AdminSkillListView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminSkillSerializer

    def get_queryset(self):
        qs = Skill.objects.all()
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(name__icontains=search)
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ("true", "1"))
        return qs


class AdminSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminSkillSerializer
    queryset = Skill.objects.all()


# ─── Careers ──────────────────────────────────────────────────────────────
class AdminCareerListView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminCareerSerializer

    def get_queryset(self):
        qs = Career.objects.prefetch_related("requirements__skill").all()
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(category__icontains=search)
            )
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ("true", "1"))
        return qs


class AdminCareerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminCareerSerializer
    queryset = Career.objects.prefetch_related("requirements__skill").all()


# ─── Assessments ──────────────────────────────────────────────────────────
class AdminAssessmentListView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminAssessmentSerializer

    def get_queryset(self):
        qs = Assessment.objects.select_related("skill").all()
        skill = self.request.query_params.get("skill")
        if skill:
            qs = qs.filter(skill_id=skill)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(skill__name__icontains=search)
            )
        return qs


class AdminAssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminAssessmentDetailSerializer
    queryset = Assessment.objects.select_related("skill").prefetch_related(
        "questions__options"
    ).all()


# ─── Opportunities ────────────────────────────────────────────────────────
class AdminOpportunityListView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminOpportunitySerializer

    def get_queryset(self):
        qs = Opportunity.objects.prefetch_related("requirements__skill").all()
        opp_type = self.request.query_params.get("type")
        if opp_type:
            qs = qs.filter(opportunity_type=opp_type)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(company__icontains=search)
            )
        return qs


class AdminOpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminOpportunitySerializer
    queryset = Opportunity.objects.prefetch_related("requirements__skill").all()


# ─── Learning Resources ───────────────────────────────────────────────────
class AdminLearningResourceListView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminLearningResourceSerializer

    def get_queryset(self):
        qs = LearningResource.objects.select_related("skill").all()
        skill = self.request.query_params.get("skill")
        if skill:
            qs = qs.filter(skill_id=skill)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(skill__name__icontains=search)
            )
        resource_type = self.request.query_params.get("type")
        if resource_type:
            qs = qs.filter(type=resource_type)
        return qs


class AdminLearningResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminLearningResourceSerializer
    queryset = LearningResource.objects.select_related("skill").all()


# ─── Applications ─────────────────────────────────────────────────────────
class AdminApplicationListView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = None  # we return raw dicts

    def get(self, request, *args, **kwargs):
        qs = Application.objects.select_related(
            "student", "opportunity"
        ).all().order_by("-applied_at")

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(student__email__icontains=search)
                | Q(student__first_name__icontains=search)
                | Q(student__last_name__icontains=search)
                | Q(opportunity__title__icontains=search)
                | Q(opportunity__company__icontains=search)
            )

        data = []
        for app in qs[:100]:
            data.append({
                "id": app.id,
                "student_name": app.student.get_full_name() or app.student.username,
                "student_email": app.student.email,
                "opportunity_title": app.opportunity.title,
                "opportunity_company": app.opportunity.company,
                "status": app.status,
                "applied_at": app.applied_at,
                "notes": app.notes,
            })
        return Response(data)


# ─── Notifications ────────────────────────────────────────────────────────
class AdminNotificationCreateView(APIView):
    """Send a notification to users."""
    permission_classes = [IsAdmin]

    def post(self, request):
        title = request.data.get("title", "").strip()
        body = request.data.get("body", "").strip()
        target = request.data.get("target", "all")  # all, students, professors
        if not title or not body:
            return Response(
                {"detail": "title and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.notifications.models import Notification

        if target == "students":
            users = User.objects.filter(role="STUDENT")
        elif target == "professors":
            users = User.objects.filter(role="PROFESSOR")
        else:
            users = User.objects.all()

        notifications = [
            Notification(
                user=u,
                notification_type=Notification.Type.SYSTEM,
                title=title,
                body=body,
            )
            for u in users
        ]
        Notification.objects.bulk_create(notifications)
        return Response({"detail": f"Notification sent to {len(notifications)} users."})


# ─── Analytics ────────────────────────────────────────────────────────────
class AdminAnalyticsView(APIView):
    """Platform-wide analytics for the admin dashboard."""
    permission_classes = [IsAdmin]

    def get(self, _request):
        # User counts by role
        users_by_role = list(
            User.objects.values("role").annotate(count=Count("id")).order_by("role")
        )

        # Users by month (last 12 months)
        from django.db.models.functions import TruncMonth
        users_by_month = list(
            User.objects.filter(date_joined__isnull=False)
            .annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("-month")[:12]
        )
        for item in users_by_month:
            item["month"] = item["month"].isoformat() if item["month"] else None

        # Popular skills (most user_skills)
        popular_skills = list(
            Skill.objects.filter(is_active=True)
            .annotate(student_count=Count("user_skills"))
            .order_by("-student_count")[:10]
            .values("name", "category", "student_count")
        )

        # Popular careers (most skill requirements)
        popular_careers = list(
            Career.objects.filter(is_active=True)
            .annotate(req_count=Count("requirements"))
            .order_by("-req_count")[:10]
            .values("title", "category", "req_count")
        )

        # Applications by status
        applications_by_status = list(
            Application.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        # Common skill gaps (skills that appear in most career requirements
        # but have low average student proficiency)
        skill_gap_stats = []
        for skill in Skill.objects.filter(is_active=True):
            avg_req = CareerSkillRequirement.objects.filter(skill=skill).aggregate(
                avg=Count("id")
            )["avg"]
            user_count = UserSkill.objects.filter(skill=skill).count()
            if avg_req and user_count:
                skill_gap_stats.append({
                    "skill": skill.name,
                    "category": skill.category,
                    "required_by": avg_req,
                    "students_have": user_count,
                })
        common_skill_gaps = sorted(skill_gap_stats, key=lambda x: x["required_by"] - x["students_have"], reverse=True)[:10]

        # Selected students (accepted applications)
        selected_count = Application.objects.filter(status="SELECTED").values(
            "student"
        ).distinct().count()

        return Response({
            "total_users": User.objects.count(),
            "total_students": User.objects.filter(role="STUDENT").count(),
            "total_professors": User.objects.filter(role="PROFESSOR").count(),
            "total_admins": User.objects.filter(role="ADMIN").count(),
            "total_skills": Skill.objects.count(),
            "total_careers": Career.objects.count(),
            "total_assessments": Assessment.objects.count(),
            "total_opportunities": Opportunity.objects.count(),
            "total_applications": Application.objects.count(),
            "total_learning_resources": LearningResource.objects.count(),
            "selected_students": selected_count,
            "active_opportunities": Opportunity.objects.filter(status="ACTIVE").count(),
            "published_assessments": Assessment.objects.filter(is_published=True).count(),
            "users_by_role": users_by_role,
            "users_by_month": users_by_month,
            "popular_skills": popular_skills,
            "popular_careers": popular_careers,
            "applications_by_status": applications_by_status,
            "common_skill_gaps": common_skill_gaps,
        })
