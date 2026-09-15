"""Tests for professor endpoints (Phase 14)."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.permissions import IsProfessor
from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog

User = get_user_model()


def register_and_login(client, email="prof@test.com", role="PROFESSOR"):
    """Register a user and return the auth token."""
    user = User.objects.create_user(
        username=email.split("@")[0],
        email=email,
        password="TestPass123!",
        role=role,
        first_name="Test",
        last_name="User",
    )
    res = client.post(
        reverse("auth-login"),
        {"email": email, "password": "TestPass123!"},
        format="json",
    )
    return res.data.get("access"), user


class ProfessorStudentListTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.token, self.professor = register_and_login(self.client)
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Create students
        self.students = []
        for i in range(3):
            student = User.objects.create_user(
                username=f"student{i}",
                email=f"student{i}@test.com",
                password="TestPass123!",
                role="STUDENT",
                first_name=f"Student{i}",
                last_name="Test",
            )
            self.students.append(student)

    def test_professor_can_list_students(self):
        res = self.client.get("/api/v1/professors/students", **self.auth)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_professor_can_search_students(self):
        res = self.client.get(
            "/api/v1/professors/students?search=student0", **self.auth
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["email"], "student0@test.com")

    def test_student_cannot_access_student_list(self):
        _, student = register_and_login(
            self.client, email="s@test.com", role="STUDENT"
        )
        token2 = self.client.post(
            reverse("auth-login"),
            {"email": "s@test.com", "password": "TestPass123!"},
            format="json",
        ).data.get("access")
        res = self.client.get(
            "/api/v1/professors/students",
            HTTP_AUTHORIZATION=f"Bearer {token2}",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        res = self.client.get("/api/v1/professors/students")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfessorStudentDossierTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.token, self.professor = register_and_login(self.client)
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.student = User.objects.create_user(
            username="dossierstudent",
            email="dossier@test.com",
            password="TestPass123!",
            role="STUDENT",
            first_name="Dossier",
            last_name="Student",
        )

        # Add a skill
        skill = Skill.objects.filter(name="Python").first()
        if skill:
            UserSkill.objects.create(
                user=self.student,
                skill=skill,
                proficiency_level=4,
                experience_level="ADVANCED",
            )

    def test_professor_can_get_dossier(self):
        res = self.client.get(
            f"/api/v1/professors/students/{self.student.pk}/dossier",
            **self.auth,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "dossier@test.com")
        self.assertIn("skills", res.data)
        self.assertIn("profile", res.data)
        self.assertIn("career_readiness", res.data)

    def test_professor_cannot_get_nonexistent_student(self):
        res = self.client.get(
            "/api/v1/professors/students/99999/dossier", **self.auth
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_access_dossier(self):
        _, student = register_and_login(
            self.client, email="s@test.com", role="STUDENT"
        )
        token2 = self.client.post(
            reverse("auth-login"),
            {"email": "s@test.com", "password": "TestPass123!"},
            format="json",
        ).data.get("access")
        res = self.client.get(
            f"/api/v1/professors/students/{self.student.pk}/dossier",
            HTTP_AUTHORIZATION=f"Bearer {token2}",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class ProfessorGuidanceTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.token, self.professor = register_and_login(self.client)
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.student = User.objects.create_user(
            username="guidancestudent",
            email="guidance@test.com",
            password="TestPass123!",
            role="STUDENT",
            first_name="Guidance",
            last_name="Student",
        )

    def test_professor_can_add_guidance(self):
        res = self.client.post(
            f"/api/v1/professors/students/{self.student.pk}/guidance",
            {
                "title": "Focus on DSA",
                "message": "Practice LeetCode daily",
                "category": "SKILL",
            },
            **self.auth,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "Focus on DSA")

    def test_professor_can_list_guidance(self):
        # Add a note first
        self.client.post(
            f"/api/v1/professors/students/{self.student.pk}/guidance",
            {"title": "Test", "message": "Test message", "category": "GENERAL"},
            **self.auth,
            format="json",
        )

        res = self.client.get(
            f"/api/v1/professors/students/{self.student.pk}/guidance",
            **self.auth,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_professor_can_delete_own_guidance(self):
        # Add a note
        add_res = self.client.post(
            f"/api/v1/professors/students/{self.student.pk}/guidance",
            {"title": "To delete", "message": "Delete me", "category": "GENERAL"},
            **self.auth,
            format="json",
        )
        note_id = add_res.data["id"]

        # Delete it
        res = self.client.delete(
            f"/api/v1/professors/guidance/{note_id}", **self.auth
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_professor_cannot_delete_others_guidance(self):
        # Create another professor and add a note
        token2, prof2 = register_and_login(
            self.client, email="prof2@test.com", role="PROFESSOR"
        )
        add_res = self.client.post(
            f"/api/v1/professors/students/{self.student.pk}/guidance",
            {"title": "Other prof note", "message": "Not yours", "category": "GENERAL"},
            HTTP_AUTHORIZATION=f"Bearer {token2}",
            format="json",
        )
        note_id = add_res.data["id"]

        # Try to delete with first professor
        res = self.client.delete(
            f"/api/v1/professors/guidance/{note_id}", **self.auth
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ProfessorAnalyticsTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.token, self.professor = register_and_login(self.client)
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Create a student
        self.student = User.objects.create_user(
            username="analyticsstudent",
            email="analytics@test.com",
            password="TestPass123!",
            role="STUDENT",
            first_name="Analytics",
            last_name="Student",
        )

    def test_professor_can_get_analytics(self):
        res = self.client.get("/api/v1/professors/analytics", **self.auth)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("total_students", res.data)
        self.assertIn("career_ready_students", res.data)
        self.assertIn("students_with_gaps", res.data)
        self.assertIn("popular_career_goals", res.data)
        self.assertIn("common_skill_gaps", res.data)

    def test_student_cannot_access_analytics(self):
        _, student = register_and_login(
            self.client, email="s@test.com", role="STUDENT"
        )
        token2 = self.client.post(
            reverse("auth-login"),
            {"email": "s@test.com", "password": "TestPass123!"},
            format="json",
        ).data.get("access")
        res = self.client.get(
            "/api/v1/professors/analytics",
            HTTP_AUTHORIZATION=f"Bearer {token2}",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
