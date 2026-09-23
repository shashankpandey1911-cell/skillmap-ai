"""API tests for the skill catalog and student skills (Phase 4)."""

from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User

from .models import Skill, UserSkill
from .seed_data import ensure_skill_catalog

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
CATALOG_URL = "/api/v1/skills/catalog"
SKILLS_URL = "/api/v1/students/me/skills"

PASSWORD = "Tr0ub4dor&3"


def register_and_login(client, email="riya@example.com"):
    client.post(
        REGISTER_URL,
        {
            "full_name": "Riya Sharma",
            "email": email,
            "password": PASSWORD,
            "role": "STUDENT",
            "college": "NIT Trichy",
            "course": "B.Tech CSE",
            "year": 3,
        },
        format="json",
    )
    res = client.post(LOGIN_URL, {"email": email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


class CatalogTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()

    def test_catalog_returns_seeded_skills(self):
        register_and_login(self.client)
        res = self.client.get(CATALOG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 60)
        categories = {item["category"] for item in res.data}
        self.assertIn("Programming", categories)
        self.assertIn("Soft Skills", categories)

    def test_catalog_search(self):
        register_and_login(self.client)
        res = self.client.get(CATALOG_URL, {"search": "pyt"})
        names = [item["name"] for item in res.data]
        self.assertIn("Python", names)
        self.assertIn("PyTorch", names)
        self.assertNotIn("React", names)

    def test_catalog_category_filter(self):
        register_and_login(self.client)
        res = self.client.get(CATALOG_URL, {"category": "Database"})
        self.assertTrue(res.data)
        for item in res.data:
            self.assertEqual(item["category"], "Database")

    def test_catalog_requires_authentication(self):
        res = self.client.get(CATALOG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UserSkillCrudTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.python = Skill.objects.get(name="Python")
        self.sql = Skill.objects.get(name="SQL")

    def payload(self, skill, proficiency=3, experience="INTERMEDIATE"):
        return {
            "skill": skill.id if isinstance(skill, Skill) else skill,
            "proficiency_level": proficiency,
            "experience_level": experience,
        }

    def test_add_list_update_delete_skill(self):
        # Create
        res = self.client.post(SKILLS_URL, self.payload(self.python, 4, "ADVANCED"), format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["skill"]["name"], "Python")
        self.assertEqual(res.data["skill"]["category"], "Programming")
        self.assertEqual(res.data["proficiency_level"], 4)
        self.assertEqual(res.data["score"], 80)  # 4 x 20, no assessment yet
        self.assertIsNone(res.data["assessment_score"])
        sid = res.data["id"]

        # List
        res = self.client.get(SKILLS_URL)
        self.assertEqual(len(res.data), 1)

        # Update proficiency + experience
        res = self.client.patch(
            f"{SKILLS_URL}/{sid}",
            {"proficiency_level": 5, "experience_level": "EXPERT"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["proficiency_level"], 5)
        self.assertEqual(res.data["experience_level"], "EXPERT")
        self.assertEqual(res.data["score"], 100)

        # Delete
        res = self.client.delete(f"{SKILLS_URL}/{sid}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(self.client.get(SKILLS_URL).data), 0)

    def test_duplicate_skill_rejected(self):
        self.client.post(SKILLS_URL, self.payload(self.python), format="json")
        res = self.client.post(SKILLS_URL, self.payload(self.python), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("skill", res.data)
        self.assertEqual(UserSkill.objects.filter(user__email="riya@example.com").count(), 1)

    def test_invalid_proficiency_rejected(self):
        res = self.client.post(SKILLS_URL, self.payload(self.python, proficiency=7), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("proficiency_level", res.data)
        res = self.client.post(SKILLS_URL, self.payload(self.python, proficiency=0), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_experience_level_rejected(self):
        res = self.client.post(
            SKILLS_URL,
            {**self.payload(self.python), "experience_level": "SUPERSTAR"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("experience_level", res.data)

    def test_unknown_skill_rejected(self):
        res = self.client.post(SKILLS_URL, self.payload(skill=99999), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("skill", res.data)

    def test_student_cannot_write_assessment_score(self):
        res = self.client.post(
            SKILLS_URL,
            {**self.payload(self.python), "assessment_score": "99.9"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data["assessment_score"])
        row = UserSkill.objects.get()
        self.assertIsNone(row.assessment_score)

    def test_assessment_score_used_instead_of_proficiency(self):
        row = UserSkill.objects.create(
            user=User.objects.get(email="riya@example.com"),
            skill=self.sql,
            proficiency_level=2,
            experience_level=UserSkill.ExperienceLevel.BEGINNER,
        )
        # Simulate the assessment engine writing a real score.
        row.assessment_score = Decimal("75.0")
        row.save()
        res = self.client.get(SKILLS_URL)
        item = next(s for s in res.data if s["skill"]["name"] == "SQL")
        self.assertEqual(item["score"], 75.0)
        self.assertEqual(item["proficiency_level"], 2)

    def test_list_search_and_category_filter(self):
        self.client.post(SKILLS_URL, self.payload(self.python), format="json")
        self.client.post(SKILLS_URL, self.payload(self.sql), format="json")
        self.client.post(
            SKILLS_URL, self.payload(Skill.objects.get(name="React")), format="json"
        )

        res = self.client.get(SKILLS_URL, {"search": "sql"})
        self.assertEqual([s["skill"]["name"] for s in res.data], ["SQL"])

        res = self.client.get(SKILLS_URL, {"category": "Database"})
        self.assertEqual([s["skill"]["name"] for s in res.data], ["SQL"])

        res = self.client.get(SKILLS_URL)
        self.assertEqual(len(res.data), 3)

    def test_skill_is_owner_scoped(self):
        res = self.client.post(SKILLS_URL, self.payload(self.python), format="json")
        sid = res.data["id"]

        register_and_login(self.client, email="other@example.com")
        self.assertEqual(self.client.get(SKILLS_URL).data, [])
        self.assertEqual(self.client.get(f"{SKILLS_URL}/{sid}").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            self.client.patch(f"{SKILLS_URL}/{sid}", {"proficiency_level": 5}, format="json").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_professor_cannot_manage_student_skills(self):
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
        res = self.client.post(
            LOGIN_URL, {"email": "anita@example.com", "password": PASSWORD}, format="json"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        res = self.client.get(SKILLS_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
