"""Tests for admin CRUD and analytics endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.careers.models import Career, CareerSkillRequirement
from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.assessments.models import Assessment
from apps.opportunities.models import Opportunity
from apps.learning.models import LearningResource

User = get_user_model()


class AdminTestBase(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.admin = User.objects.create_user(
            username="admintest",
            email="admin@test.com",
            password="Admin@12345",
            role="ADMIN",
        )
        self.student = User.objects.create_user(
            username="studenttest",
            email="student@test.com",
            password="Student@12345",
            role="STUDENT",
        )
        self.client.force_authenticate(user=self.admin)


class AdminDashboardTests(AdminTestBase):
    def test_dashboard_summary(self):
        resp = self.client.get("/api/v1/admin/dashboard-summary")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("total_users", resp.data)
        self.assertEqual(resp.data["total_users"], 2)

    def test_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.student)
        resp = self.client.get("/api/v1/admin/dashboard-summary")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTests(AdminTestBase):
    def test_list_users(self):
        resp = self.client.get("/api/v1/admin/users")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data.get("results", resp.data)
        self.assertGreaterEqual(len(results), 2)

    def test_filter_by_role(self):
        resp = self.client.get("/api/v1/admin/users?role=STUDENT")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data.get("results", resp.data)
        for u in results:
            self.assertEqual(u["role"], "STUDENT")

    def test_create_user(self):
        resp = self.client.post("/api/v1/admin/users/create", {
            "full_name": "New User",
            "email": "new@test.com",
            "password": "Test@12345",
            "role": "STUDENT",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

    def test_toggle_active(self):
        resp = self.client.patch(
            f"/api/v1/admin/users/{self.student.id}",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)


class AdminSkillTests(AdminTestBase):
    def test_list_skills(self):
        resp = self.client.get("/api/v1/admin/skills")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data.get("results", resp.data)
        self.assertGreater(len(results), 0)

    def test_create_skill(self):
        resp = self.client.post("/api/v1/admin/skills", {
            "name": "GoLang",
            "category": "Programming",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_delete_skill(self):
        skill = Skill.objects.first()
        resp = self.client.delete(f"/api/v1/admin/skills/{skill.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class AdminCareerTests(AdminTestBase):
    def test_list_careers(self):
        resp = self.client.get("/api/v1/admin/careers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_career(self):
        resp = self.client.post("/api/v1/admin/careers", {
            "title": "Test Career",
            "description": "A test career",
            "category": "Tech",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class AdminOpportunityTests(AdminTestBase):
    def test_list_opportunities(self):
        resp = self.client.get("/api/v1/admin/opportunities")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_opportunity(self):
        resp = self.client.post("/api/v1/admin/opportunities", {
            "title": "Backend Dev",
            "company": "TechCorp",
            "opportunity_type": "JOB",
            "location": "Remote",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class AdminAnalyticsTests(AdminTestBase):
    def test_analytics(self):
        resp = self.client.get("/api/v1/admin/analytics")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("total_users", resp.data)
        self.assertIn("popular_skills", resp.data)
        self.assertIn("applications_by_status", resp.data)
        self.assertIn("common_skill_gaps", resp.data)
