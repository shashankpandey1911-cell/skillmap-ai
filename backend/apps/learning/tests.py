"""API tests for the learning roadmap (Phase 8)."""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.careers.models import Career, CareerSkillRequirement
from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.users.models import User

from .models import LearningResource, ResourceCompletion

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
RESOURCES_URL = "/api/v1/learning/resources"
ROADMAP_URL = "/api/v1/learning/roadmap"
ADMIN_RESOURCES_URL = "/api/v1/admin/learning/resources"

PASSWORD = "Tr0ub4dor&3"


def register_and_login(client, email="riya@example.com", role="STUDENT"):
    payload = {
        "full_name": "Riya Sharma",
        "email": email,
        "password": PASSWORD,
        "role": role,
    }
    if role == "STUDENT":
        payload.update({"college": "NIT Trichy", "course": "B.Tech CSE", "year": 3})
    client.post(REGISTER_URL, payload, format="json")
    res = client.post(LOGIN_URL, {"email": email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def login_user(client, user, password=PASSWORD):
    res = client.post(LOGIN_URL, {"email": user.email, "password": password}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def make_career(title="Backend Developer", requirements=()):
    career = Career.objects.create(title=title, category="Software Development")
    for name, target, importance in requirements:
        skill = Skill.objects.get(name=name)
        CareerSkillRequirement.objects.create(
            career=career, skill=skill, target_level=target, importance=importance
        )
    return career


def give_skill(user, name, assessment_score=None, proficiency=1):
    skill = Skill.objects.get(name=name)
    return UserSkill.objects.create(
        user=user, skill=skill, proficiency_level=proficiency,
        assessment_score=assessment_score,
    )


def make_resource(skill_name, title, rtype="COURSE", level="BEGINNER"):
    skill = Skill.objects.get(name=skill_name)
    return LearningResource.objects.create(
        title=title, skill=skill, type=rtype, level=level,
        url="https://example.com/" + title.replace(" ", "-"),
    )


class RoadmapEngineTests(APITestCase):
    """build_roadmap() output: gap-driven steps, real resource items, progress."""

    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.career = make_career(
            "Backend Developer",
            [("Python", 80, "HIGH"), ("Data Structures & Algorithms", 80, "HIGH")],
        )
        give_skill(self.student, "Python", assessment_score=85)  # no gap
        # DSA missing -> full HIGH gap
        make_resource("Data Structures & Algorithms", "DSA Crash Course", "COURSE")
        make_resource("Data Structures & Algorithms", "LeetCode Practice", "PRACTICE")
        make_resource("Data Structures & Algorithms", "Big-O Quiz", "QUIZ")

    def roadmap(self):
        return self.client.get(ROADMAP_URL, {"career_id": self.career.pk})

    def test_only_open_gaps_get_a_roadmap(self):
        res = self.roadmap()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [r["skill"]["name"] for r in res.data["roadmap"]]
        # Python is met -> excluded; only DSA needs work.
        self.assertEqual(names, ["Data Structures & Algorithms"])

    def test_step_structure_follows_phase_8_spec(self):
        res = self.roadmap()
        steps = res.data["roadmap"][0]["steps"]
        keys = [s["key"] for s in steps]
        self.assertEqual(
            keys, ["topic", "resource", "practice", "assessment", "improvement"]
        )
        titles = [s["title"] for s in steps]
        self.assertEqual(
            titles,
            ["Learning Topic", "Resource", "Practice", "Assessment", "Skill Improvement"],
        )

    def test_resources_are_grouped_into_the_right_steps(self):
        res = self.roadmap()
        steps = {s["key"]: s for s in res.data["roadmap"][0]["steps"]}
        self.assertEqual(
            [i["title"] for i in steps["resource"]["items"]], ["DSA Crash Course"]
        )
        self.assertEqual(
            [i["title"] for i in steps["practice"]["items"]], ["LeetCode Practice"]
        )
        self.assertEqual(
            [i["title"] for i in steps["assessment"]["items"]], ["Big-O Quiz"]
        )
        self.assertIn("target", steps["improvement"]["description"].lower())

    def test_progress_counts_displayed_resources(self):
        res = self.roadmap()
        progress = res.data["progress"]
        self.assertEqual(progress["total_resources"], 3)
        self.assertEqual(progress["completed_resources"], 0)
        self.assertEqual(progress["remaining_resources"], 3)
        self.assertEqual(progress["progress_percentage"], 0)

        resource_id = res.data["roadmap"][0]["steps"][1]["items"][0]["id"]
        ResourceCompletion.objects.create(user=self.student, resource_id=resource_id)

        res2 = self.roadmap()
        progress2 = res2.data["progress"]
        self.assertEqual(progress2["completed_resources"], 1)
        self.assertEqual(progress2["progress_percentage"], 33)

    def test_gap_data_and_priority_skills_are_real(self):
        res = self.roadmap()
        gap = res.data["roadmap"][0]["gap"]
        self.assertEqual(gap["current_level"], 0)
        self.assertEqual(gap["required_level"], 80)
        self.assertEqual(gap["gap_percentage"], 80)
        self.assertEqual(gap["gap_class"], "HIGH")
        self.assertEqual(gap["priority"], "HIGH")
        self.assertEqual(res.data["priority_skills"][0]["skill_name"], "Data Structures & Algorithms")

    def test_resource_pick_prefers_easier_levels_for_high_gaps(self):
        # HIGH gap should surface beginner course before the advanced one.
        make_resource("Data Structures & Algorithms", "Advanced DSA Course", "COURSE", "ADVANCED")
        res = self.roadmap()
        items = res.data["roadmap"][0]["steps"][1]["items"]
        self.assertEqual(items[0]["title"], "DSA Crash Course")  # beginner first


class ResourceCompletionTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.resource = make_resource("Python", "Python for Everybody")

    def complete_url(self):
        return f"{RESOURCES_URL}/{self.resource.pk}/complete"

    def test_mark_and_unmark_complete(self):
        post = self.client.post(self.complete_url())
        self.assertEqual(post.status_code, status.HTTP_200_OK)
        self.assertTrue(post.data["completed"])
        self.assertTrue(ResourceCompletion.objects.filter(resource=self.resource).exists())

        delete = self.client.delete(self.complete_url())
        self.assertEqual(delete.status_code, status.HTTP_200_OK)
        self.assertFalse(delete.data["completed"])
        self.assertFalse(ResourceCompletion.objects.filter(resource=self.resource).exists())

    def test_completion_is_anonymous_to_other_students(self):
        self.client.post(self.complete_url())
        register_and_login(self.client, email="arjun@example.com")
        res = self.client.get(RESOURCES_URL)
        row = next(r for r in res.data if r["id"] == self.resource.pk)
        self.assertFalse(row["completed"])

    def test_professor_cannot_mark_completion(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.post(self.complete_url())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class RoadmapAccessTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.career = make_career("Backend Developer", [("Python", 80, "HIGH")])
        give_skill(self.student, "Python", assessment_score=50)

    def test_anonymous_is_rejected(self):
        self.client.credentials()
        res = self.client.get(ROADMAP_URL, {"career_id": self.career.pk})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_career_id_is_required(self):
        res = self.client.get(ROADMAP_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_career_404s(self):
        res = self.client.get(ROADMAP_URL, {"career_id": 99999})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_read_another_student(self):
        register_and_login(self.client, email="arjun@example.com")
        res = self.client.get(
            ROADMAP_URL, {"career_id": self.career.pk, "student_id": self.student.pk}
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_can_read_any_student(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.get(
            ROADMAP_URL, {"career_id": self.career.pk, "student_id": self.student.pk}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_professor_without_student_id_gets_400(self):
        register_and_login(self.client, email="prof2@example.com", role="PROFESSOR")
        res = self.client.get(ROADMAP_URL, {"career_id": self.career.pk})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ResourceCatalogTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.python_course = make_resource("Python", "Python 101")
        self.django_doc = make_resource("Django", "Django Docs", rtype="DOCUMENTATION")

    def test_list_is_active_only(self):
        inactive = make_resource("Python", "Retired Course")
        LearningResource.objects.filter(pk=inactive.pk).update(is_active=False)
        res = self.client.get(RESOURCES_URL)
        ids = [r["id"] for r in res.data]
        self.assertIn(self.python_course.pk, ids)
        self.assertNotIn(inactive.pk, ids)

    def test_filters(self):
        res = self.client.get(RESOURCES_URL, {"search": "Django"})
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Django Docs")

        res = self.client.get(RESOURCES_URL, {"type": "DOCUMENTATION"})
        self.assertEqual(len(res.data), 1)

    def test_serializer_shape(self):
        res = self.client.get(RESOURCES_URL, {"search": "Python"})
        row = res.data[0]
        for key in ["id", "title", "level", "type", "url",
                    "estimated_duration_minutes", "completed", "skill_id", "skill_name"]:
            self.assertIn(key, row)


class AdminResourceCrudTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.admin = User.objects.create_user(
            username="boss", email="boss@example.com",
            password=PASSWORD, role=User.Role.ADMIN,
        )

    def login(self, role="ADMIN"):
        if role == "ADMIN":
            login_user(self.client, self.admin)
        else:
            register_and_login(self.client, email="prof@example.com", role="PROFESSOR")

    def test_create_and_read(self):
        self.login()
        python = Skill.objects.get(name="Python")
        res = self.client.post(
            ADMIN_RESOURCES_URL,
            {
                "title": "Python Advanced Course",
                "skill": python.pk,
                "level": "ADVANCED",
                "type": "COURSE",
                "url": "https://example.com/python-advanced",
                "estimated_duration_minutes": 300,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        detail = self.client.get(f"{ADMIN_RESOURCES_URL}/{res.data['id']}")
        self.assertEqual(detail.data["title"], "Python Advanced Course")
        self.assertEqual(detail.data["skill_name"], "Python")

    def test_patch_and_delete(self):
        self.login()
        resource = make_resource("Python", "Course To Edit")
        patch = self.client.patch(
            f"{ADMIN_RESOURCES_URL}/{resource.pk}",
            {"title": "Renamed Course", "is_active": False},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        resource.refresh_from_db()
        self.assertEqual(resource.title, "Renamed Course")
        self.assertFalse(resource.is_active)

        delete = self.client.delete(f"{ADMIN_RESOURCES_URL}/{resource.pk}")
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LearningResource.objects.filter(pk=resource.pk).exists())

    def test_invalid_type_rejected(self):
        self.login()
        python = Skill.objects.get(name="Python")
        res = self.client.post(
            ADMIN_RESOURCES_URL,
            {"title": "Bad Type", "skill": python.pk, "type": "MOOC", "level": "BEGINNER"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_professor_cannot_manage_resources(self):
        self.login(role="PROFESSOR")
        res = self.client.post(ADMIN_RESOURCES_URL, {"title": "Nope"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
