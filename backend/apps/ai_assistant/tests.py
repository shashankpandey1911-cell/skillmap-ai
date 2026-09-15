"""Tests for AI assistant endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.skills.models import Skill, UserSkill
from apps.careers.seed_data import ensure_demo_careers
from apps.skills.seed_data import ensure_skill_catalog
from apps.students.models import StudentProfile

User = get_user_model()


class AITestBase(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        ensure_demo_careers()
        self.student = User.objects.create_user(
            username="aistudent",
            email="ai@test.com",
            password="Student@12345",
            role="STUDENT",
        )
        StudentProfile.objects.create(
            user=self.student,
            college="IIT Bombay",
            course="B.Tech CS",
            career_goal="Backend Developer at a top product company",
            interests="Machine learning, open source, competitive programming",
            preferred_domain="Full-stack / AI-ML",
        )
        # Add some skills
        for name, prof in [("Python", 5), ("Django", 4), ("SQL", 4), ("Git", 5)]:
            skill = Skill.objects.filter(name=name).first()
            if skill:
                UserSkill.objects.create(
                    user=self.student, skill=skill,
                    proficiency_level=prof, experience_level="ADVANCED",
                )
        self.client.force_authenticate(user=self.student)


class AIStatusTests(AITestBase):
    def test_status_endpoint(self):
        resp = self.client.get("/api/v1/ai/status")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("ai_available", resp.data)


class ResumeExtractionTests(AITestBase):
    def test_rule_based_extraction(self):
        """Without AI key, falls back to rule-based extraction."""
        resp = self.client.post(
            "/api/v1/ai/extract-resume",
            {"resume_text": "I know Python, JavaScript, React, Django, Docker, SQL, AWS, Git"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("skills", resp.data)
        self.assertGreater(len(resp.data["skills"]), 0)
        skill_names = [s["name"].lower() for s in resp.data["skills"]]
        self.assertIn("python", skill_names)
        self.assertIn("javascript", skill_names)

    def test_empty_resume(self):
        resp = self.client.post(
            "/api/v1/ai/extract-resume",
            {"resume_text": "Hello world"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["skills"]), 0)


class ResumeApproveTests(AITestBase):
    def test_approve_creates_skills(self):
        resp = self.client.post(
            "/api/v1/ai/approve-extraction",
            {
                "skills": [
                    {"name": "TypeScript", "category": "Programming", "confidence": 0.8},
                    {"name": "React", "category": "Web Development", "confidence": 0.9},
                ]
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(resp.data["created"]["skills"], 0)


class AICareerRecommendationTests(AITestBase):
    def test_career_recommendation(self):
        """Without AI key, returns empty recommendations."""
        resp = self.client.post(
            "/api/v1/ai/career-recommendation",
            {},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("ai_powered", resp.data)
        self.assertIn("recommendations", resp.data)


class AILearningRecommendationTests(AITestBase):
    def test_learning_recommendation(self):
        resp = self.client.post(
            "/api/v1/ai/learning-recommendation",
            {"career_title": "Backend Developer"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("ai_powered", resp.data)
        self.assertIn("roadmap", resp.data)

    def test_missing_career_title(self):
        resp = self.client.post(
            "/api/v1/ai/learning-recommendation",
            {},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class AIOpportunityExplanationTests(AITestBase):
    def test_missing_opportunity_id(self):
        resp = self.client.post(
            "/api/v1/ai/opportunity-explanation",
            {},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_opportunity(self):
        resp = self.client.post(
            "/api/v1/ai/opportunity-explanation",
            {"opportunity_id": 99999},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class NonStudentAccessTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="aiadmin", email="aiadm@test.com",
            password="Admin@12345", role="ADMIN",
        )
        self.client.force_authenticate(user=self.admin)

    def test_student_endpoints_forbidden_for_admin(self):
        for endpoint in [
            "/api/v1/ai/extract-resume",
            "/api/v1/ai/career-recommendation",
            "/api/v1/ai/learning-recommendation",
        ]:
            resp = self.client.post(endpoint, {}, format="json")
            self.assertIn(resp.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
