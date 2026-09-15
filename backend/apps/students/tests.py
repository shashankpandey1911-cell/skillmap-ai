"""API tests for the student career profile (Phase 3)."""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/students/me"
PROJECTS_URL = "/api/v1/students/me/projects"
CERTS_URL = "/api/v1/students/me/certifications"

PASSWORD = "Tr0ub4dor&3"


def register_student(client, email, **profile_overrides):
    payload = {
        "full_name": "Riya Sharma",
        "email": email,
        "password": PASSWORD,
        "role": "STUDENT",
        "college": "NIT Trichy",
        "course": "B.Tech CSE",
        "year": 3,
    }
    payload.update(profile_overrides)
    return client.post(REGISTER_URL, payload, format="json")


def login(client, email):
    res = client.post(LOGIN_URL, {"email": email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
    return res.data


class ProfileTests(APITestCase):
    def setUp(self):
        self.email = "riya@example.com"
        register_student(self.client, self.email)
        login(self.client, self.email)

    def test_get_profile_returns_user_profile_and_completeness(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"]["email"], self.email)
        self.assertEqual(res.data["profile"]["college"], "NIT Trichy")
        self.assertIn("overall", res.data["completeness"])
        self.assertIn("sections", res.data["completeness"])
        sections = res.data["completeness"]["sections"]
        self.assertIn("personal", sections)
        self.assertIn("academic", sections)
        self.assertIn("career", sections)
        self.assertIn("projects", sections)
        self.assertIn("certifications", sections)

    def test_patch_updates_user_and_profile_fields(self):
        res = self.client.patch(
            ME_URL,
            {
                "first_name": "Riyaa",
                "phone": "+91 98765 43210",
                "branch": "CSE",
                "cgpa": "8.75",
                "semester": 5,
                "achievements": "Winner, Smart India Hackathon 2025",
                "career_goal": "Software Engineer at a product company",
                "preferred_domain": "AI/ML",
                "interests": "Deep learning, open source, hackathons",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"]["first_name"], "Riyaa")
        self.assertEqual(res.data["user"]["phone"], "+91 98765 43210")
        profile = res.data["profile"]
        self.assertEqual(profile["branch"], "CSE")
        self.assertEqual(profile["cgpa"], "8.75")
        self.assertEqual(profile["semester"], 5)
        self.assertEqual(profile["career_goal"], "Software Engineer at a product company")

        # Persisted, not just echoed.
        user = User.objects.get(email=self.email)
        self.assertEqual(user.first_name, "Riyaa")
        self.assertEqual(user.student_profile.cgpa, 8.75)

    def test_patch_rejects_invalid_cgpa_and_semester(self):
        res = self.client.patch(ME_URL, {"cgpa": "14", "semester": 99}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cgpa", res.data)
        self.assertIn("semester", res.data)

    def test_patch_partial_does_not_clear_other_fields(self):
        self.client.patch(ME_URL, {"branch": "CSE"}, format="json")
        res = self.client.patch(ME_URL, {"career_goal": "Data Scientist"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["profile"]["branch"], "CSE")
        self.assertEqual(res.data["profile"]["career_goal"], "Data Scientist")

    def test_completeness_increases_with_filled_sections(self):
        base = self.client.get(ME_URL).data["completeness"]["overall"]
        self.client.patch(
            ME_URL,
            {
                "phone": "+91 90000 00000",
                "branch": "CSE",
                "cgpa": "8.5",
                "semester": 5,
                "achievements": "Dean's list",
                "career_goal": "SDE",
                "preferred_domain": "Backend",
                "interests": "Distributed systems",
            },
            format="json",
        )
        self.client.post(
            PROJECTS_URL,
            {"name": "SkillMap API", "description": "REST API", "technologies": "Django, DRF"},
            format="json",
        )
        self.client.post(
            CERTS_URL,
            {"name": "AWS Cloud Practitioner", "provider": "Amazon", "issued_date": "2025-06-01"},
            format="json",
        )
        res = self.client.get(ME_URL).data["completeness"]
        self.assertGreater(res["overall"], base)
        self.assertEqual(res["sections"]["projects"], 100)
        self.assertEqual(res["sections"]["certifications"], 100)
        self.assertEqual(res["sections"]["career"], 100)


class ProjectCrudTests(APITestCase):
    def setUp(self):
        register_student(self.client, "riya@example.com")
        login(self.client, "riya@example.com")

    def test_create_list_update_delete_project(self):
        # Create
        res = self.client.post(
            PROJECTS_URL,
            {
                "name": "Campus Placement Tracker",
                "description": "Web app to track campus placement drives.",
                "technologies": "React, Django",
                "github_url": "https://github.com/riya/placement-tracker",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pid = res.data["id"]

        # List
        res = self.client.get(PROJECTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        # Update
        res = self.client.patch(
            f"{PROJECTS_URL}/{pid}",
            {"technologies": "React, Django, PostgreSQL"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["technologies"], "React, Django, PostgreSQL")

        # Delete
        res = self.client.delete(f"{PROJECTS_URL}/{pid}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(self.client.get(PROJECTS_URL).data), 0)

    def test_project_is_owner_scoped(self):
        res = self.client.post(
            PROJECTS_URL, {"name": "Riya's project"}, format="json"
        )
        pid = res.data["id"]

        # A second student cannot see or touch it.
        register_student(self.client, "other@example.com")
        login(self.client, "other@example.com")
        self.assertEqual(self.client.get(PROJECTS_URL).data, [])
        self.assertEqual(self.client.get(f"{PROJECTS_URL}/{pid}").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.patch(f"{PROJECTS_URL}/{pid}", {"name": "hacked"}, format="json").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(f"{PROJECTS_URL}/{pid}").status_code, status.HTTP_404_NOT_FOUND)


class CertificationCrudTests(APITestCase):
    def setUp(self):
        register_student(self.client, "riya@example.com")
        login(self.client, "riya@example.com")

    def test_create_list_update_delete_certification(self):
        res = self.client.post(
            CERTS_URL,
            {
                "name": "AWS Cloud Practitioner",
                "provider": "Amazon Web Services",
                "issued_date": "2025-06-01",
                "credential_url": "https://credly.com/badge/123",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cid = res.data["id"]

        res = self.client.get(CERTS_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["provider"], "Amazon Web Services")

        res = self.client.patch(f"{CERTS_URL}/{cid}", {"provider": "AWS"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["provider"], "AWS")

        self.assertEqual(self.client.delete(f"{CERTS_URL}/{cid}").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(self.client.get(CERTS_URL).data), 0)

    def test_certification_is_owner_scoped(self):
        res = self.client.post(CERTS_URL, {"name": "Riya's cert"}, format="json")
        cid = res.data["id"]
        register_student(self.client, "other@example.com")
        login(self.client, "other@example.com")
        self.assertEqual(self.client.get(CERTS_URL).data, [])
        self.assertEqual(self.client.get(f"{CERTS_URL}/{cid}").status_code, status.HTTP_404_NOT_FOUND)


class AccessControlTests(APITestCase):
    def test_profile_requires_authentication(self):
        for url in (ME_URL, PROJECTS_URL, CERTS_URL):
            self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_professor_cannot_use_student_endpoints(self):
        self.client.post(
            REGISTER_URL,
            {
                "full_name": "Anita Desai",
                "email": "anita@example.com",
                "password": PASSWORD,
                "role": "PROFESSOR",
            },
            format="json",
        )
        login(self.client, "anita@example.com")
        for url in (ME_URL, PROJECTS_URL, CERTS_URL):
            self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)