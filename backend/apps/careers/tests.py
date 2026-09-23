"""API tests for career catalog and skill gap analysis (Phase 6)."""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.services.matching import (
    INTEREST_WEIGHT,
    PROJECT_WEIGHT,
    SKILL_WEIGHT,
    career_match,
)
from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.students.models import Project, StudentProfile
from apps.users.models import User

from .models import Career, CareerSkillRequirement

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
CAREERS_URL = "/api/v1/careers"
ADMIN_CAREERS_URL = "/api/v1/admin/careers"

PASSWORD = "Tr0ub4dor&3"


def register_and_login(client, email="riya@example.com", role="STUDENT"):
    payload = {
        "full_name": "Riya Sharma",
        "email": email,
        "password": PASSWORD,
        "role": role,
    }
    if role == "STUDENT":
        payload.update(
            {"college": "NIT Trichy", "course": "B.Tech CSE", "year": 3}
        )
    client.post(REGISTER_URL, payload, format="json")
    res = client.post(LOGIN_URL, {"email": email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def login_user(client, user, password=PASSWORD):
    res = client.post(LOGIN_URL, {"email": user.email, "password": password}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def make_career(title="Backend Developer", requirements=()):
    career = Career.objects.create(
        title=title,
        category="Software Development",
        description=f"Description for {title}",
        salary_range="₹8–24 LPA",
    )
    for name, target, importance in requirements:
        skill = Skill.objects.get(name=name)
        CareerSkillRequirement.objects.create(
            career=career, skill=skill, target_level=target, importance=importance
        )
    return career


def give_skill(user, name, assessment_score=None, proficiency=1):
    skill = Skill.objects.get(name=name)
    return UserSkill.objects.create(
        user=user,
        skill=skill,
        proficiency_level=proficiency,
        assessment_score=assessment_score,
    )


def analysis_payload(client, career_pk, student_id=None):
    params = {"student_id": student_id} if student_id else {}
    return client.get(f"{CAREERS_URL}/{career_pk}/gap-analysis", params)


class GapEngineExampleTests(APITestCase):
    """The Phase 6 worked example, verbatim from the requirements."""

    def setUp(self):
        ensure_skill_catalog()
        # Backend Developer: Python 80, Django 70, SQL 70, DSA 80, Git 60
        self.career = make_career(
            "Backend Developer",
            [
                ("Python", 80, "HIGH"),
                ("Django", 70, "HIGH"),
                ("SQL", 70, "HIGH"),
                ("Data Structures & Algorithms", 80, "HIGH"),
                ("Git", 60, "MEDIUM"),
            ],
        )
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        # Student: Python 85, Django 50, SQL 75, DSA 40, Git 70
        give_skill(self.student, "Python", assessment_score=85)
        give_skill(self.student, "Django", assessment_score=50)
        give_skill(self.student, "SQL", assessment_score=75)
        give_skill(self.student, "Data Structures & Algorithms", proficiency=2)
        give_skill(self.student, "Git", assessment_score=70)

    def gap_map(self, data):
        return {g["skill_name"]: g for g in data["gaps"]}

    def test_worked_example_results(self):
        res = analysis_payload(self.client, self.career.pk)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        gaps = self.gap_map(res.data)

        self.assertEqual(gaps["Python"]["gap_percentage"], 0)
        self.assertEqual(gaps["Python"]["gap_class"], "NONE")
        self.assertEqual(gaps["SQL"]["gap_class"], "NONE")
        self.assertEqual(gaps["Git"]["gap_class"], "NONE")

        self.assertEqual(gaps["Django"]["current_level"], 50)
        self.assertEqual(gaps["Django"]["required_level"], 70)
        self.assertEqual(gaps["Django"]["gap_percentage"], 20)
        self.assertEqual(gaps["Django"]["gap_class"], "MEDIUM")

        self.assertEqual(gaps["Data Structures & Algorithms"]["current_level"], 40)
        self.assertEqual(gaps["Data Structures & Algorithms"]["required_level"], 80)
        self.assertEqual(gaps["Data Structures & Algorithms"]["gap_percentage"], 40)
        self.assertEqual(gaps["Data Structures & Algorithms"]["gap_class"], "HIGH")

    def test_no_gap_when_current_exceeds_requirement(self):
        res = analysis_payload(self.client, self.career.pk)
        gaps = self.gap_map(res.data)
        # Python 85 vs 80: current above required -> gap floored at 0
        self.assertEqual(gaps["Python"]["gap_percentage"], 0)
        self.assertEqual(gaps["Python"]["priority"], "NONE")

    def test_priority_combines_importance_and_gap(self):
        res = analysis_payload(self.client, self.career.pk)
        gaps = self.gap_map(res.data)
        # HIGH-importance skill with HIGH gap -> HIGH priority
        self.assertEqual(gaps["Data Structures & Algorithms"]["priority"], "HIGH")
        # HIGH-importance skill with MEDIUM gap -> HIGH priority
        self.assertEqual(gaps["Django"]["priority"], "HIGH")
        # MEDIUM-importance, no gap -> NONE
        self.assertEqual(gaps["Git"]["priority"], "NONE")

    def test_recommended_actions_are_present_and_specific(self):
        res = analysis_payload(self.client, self.career.pk)
        gaps = self.gap_map(res.data)
        self.assertIn("Python", gaps["Python"]["recommended_action"])
        self.assertIn("Backend Developer", gaps["Django"]["recommended_action"])
        self.assertTrue(gaps["Django"]["recommended_action"])

    def test_readiness_score_is_real_average(self):
        res = analysis_payload(self.client, self.career.pk)
        # ratios: 85/80=1, 50/70=.714, 75/70=1, 40/80=.5, 70/60=1 -> avg .8428...
        expected = round((1 + 50 / 70 + 1 + 0.5 + 1) / 5 * 100, 1)
        self.assertAlmostEqual(res.data["readiness_percentage"], expected)

    def test_summary_counts(self):
        res = analysis_payload(self.client, self.career.pk)
        self.assertEqual(res.data["summary"]["total"], 5)
        self.assertEqual(res.data["summary"]["no_gap"], 3)
        self.assertEqual(res.data["summary"]["medium"], 1)
        self.assertEqual(res.data["summary"]["high"], 1)


class GapClassificationTests(APITestCase):
    """Boundary behaviour of the LOW / MEDIUM / HIGH buckets."""

    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")

    def test_boundaries(self):
        career = make_career(
            "Boundary Career",
            [
                ("Python", 50, "LOW"),  # gap 19 -> LOW
                ("SQL", 50, "LOW"),  # gap 20 -> MEDIUM
                ("Git", 50, "LOW"),  # gap 39 -> MEDIUM
                ("Django", 50, "LOW"),  # gap 40 -> HIGH
            ],
        )
        give_skill(self.student, "Python", assessment_score=31)
        give_skill(self.student, "SQL", assessment_score=30)
        give_skill(self.student, "Git", assessment_score=11)
        give_skill(self.student, "Django", assessment_score=10)

        res = analysis_payload(self.client, career.pk)
        gaps = {g["skill_name"]: g for g in res.data["gaps"]}
        self.assertEqual(gaps["Python"]["gap_class"], "LOW")
        self.assertEqual(gaps["SQL"]["gap_class"], "MEDIUM")
        self.assertEqual(gaps["Git"]["gap_class"], "MEDIUM")
        self.assertEqual(gaps["Django"]["gap_class"], "HIGH")

    def test_importance_raises_low_gap_priority(self):
        career = make_career(
            "Importance Career",
            [("Python", 60, "HIGH"), ("Git", 60, "LOW")],
        )
        give_skill(self.student, "Python", assessment_score=50)
        give_skill(self.student, "Git", assessment_score=50)
        res = analysis_payload(self.client, career.pk)
        gaps = {g["skill_name"]: g for g in res.data["gaps"]}
        # Both have a 10-point gap (LOW class); HIGH importance -> HIGH priority
        self.assertEqual(gaps["Python"]["priority"], "HIGH")
        # LOW importance + LOW gap -> LOW priority
        self.assertEqual(gaps["Git"]["priority"], "LOW")

    def test_missing_skill_counts_as_full_gap(self):
        career = make_career("Missing Skill Career", [("Docker", 70, "HIGH")])
        res = analysis_payload(self.client, career.pk)
        gap = res.data["gaps"][0]
        self.assertEqual(gap["current_level"], 0)
        self.assertEqual(gap["gap_percentage"], 70)
        self.assertEqual(gap["gap_class"], "HIGH")
        self.assertEqual(res.data["readiness_percentage"], 0)


class MultipleStudentsAndCareersTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client, email="riya@example.com")
        self.riya = User.objects.get(email="riya@example.com")
        give_skill(self.riya, "Python", assessment_score=90)
        give_skill(self.riya, "SQL", assessment_score=40)

    def test_different_students_get_different_analyses(self):
        register_and_login(self.client, email="arjun@example.com")
        self.arjun = User.objects.get(email="arjun@example.com")
        give_skill(self.arjun, "Python", assessment_score=30)
        give_skill(self.arjun, "SQL", assessment_score=90)

        career = make_career(
            "Full-Stack Developer",
            [("Python", 75, "HIGH"), ("SQL", 70, "MEDIUM")],
        )

        login_user(self.client, self.riya)
        riya = analysis_payload(self.client, career.pk).data
        login_user(self.client, self.arjun)
        arjun = analysis_payload(self.client, career.pk).data

        self.assertEqual(riya["gaps"][0]["skill_name"], "SQL")
        self.assertEqual(arjun["gaps"][0]["skill_name"], "Python")
        self.assertNotEqual(
            riya["readiness_percentage"], arjun["readiness_percentage"]
        )

    def test_same_student_different_careers(self):
        backend = make_career(
            "Backend Developer", [("Python", 80, "HIGH"), ("SQL", 70, "MEDIUM")]
        )
        data_science = make_career(
            "Data Scientist", [("Python", 85, "HIGH"), ("Statistics", 80, "HIGH")]
        )
        res_backend = analysis_payload(self.client, backend.pk).data
        res_ds = analysis_payload(self.client, data_science.pk).data
        self.assertNotEqual(res_backend, res_ds)
        # Missing Statistics is a full gap for the data scientist
        stats_gap = next(g for g in res_ds["gaps"] if g["skill_name"] == "Statistics")
        self.assertEqual(stats_gap["gap_percentage"], 80)


class AccessControlTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.career = make_career(
            "Backend Developer", [("Python", 80, "HIGH")]
        )
        register_and_login(self.client, email="riya@example.com")
        self.riya = User.objects.get(email="riya@example.com")

    def test_anonymous_is_rejected(self):
        self.client.credentials()
        res = analysis_payload(self.client, self.career.pk)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_cannot_read_another_student(self):
        register_and_login(self.client, email="arjun@example.com")
        res = analysis_payload(self.client, self.career.pk, student_id=self.riya.pk)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_can_analyze_any_student(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = analysis_payload(self.client, self.career.pk, student_id=self.riya.pk)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["summary"]["total"], 1)

    def test_professor_without_student_id_gets_400(self):
        register_and_login(self.client, email="prof2@example.com", role="PROFESSOR")
        res = analysis_payload(self.client, self.career.pk)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_analyze_any_student(self):
        admin = User.objects.create_user(
            username="boss",
            email="boss@example.com",
            password=PASSWORD,
            role=User.Role.ADMIN,
        )
        login_user(self.client, admin)
        res = analysis_payload(self.client, self.career.pk, student_id=self.riya.pk)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_catalog_and_detail_visible_to_all_roles(self):
        register_and_login(self.client, email="prof3@example.com", role="PROFESSOR")
        res = self.client.get(CAREERS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        detail = self.client.get(f"{CAREERS_URL}/{self.career.pk}")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["requirements"][0]["target_level"], 80)


class CatalogTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        make_career(
            "Backend Developer", [("Python", 80, "HIGH")]
        )
        make_career(
            "Data Scientist", [("Statistics", 75, "HIGH")]
        )
        register_and_login(self.client)

    def test_list_search(self):
        res = self.client.get(CAREERS_URL, {"search": "Backend"})
        titles = [c["title"] for c in res.data]
        self.assertEqual(titles, ["Backend Developer"])

    def test_list_includes_skill_count(self):
        res = self.client.get(CAREERS_URL)
        backend = next(c for c in res.data if c["title"] == "Backend Developer")
        self.assertEqual(backend["skill_count"], 1)

    def test_inactive_career_hidden(self):
        Career.objects.create(title="Retired Role", is_active=False)
        res = self.client.get(CAREERS_URL)
        self.assertNotIn("Retired Role", [c["title"] for c in res.data])


class AdminCrudTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.admin = User.objects.create_user(
            username="boss",
            email="boss@example.com",
            password=PASSWORD,
            role=User.Role.ADMIN,
        )

    def login(self, role="ADMIN"):
        if role == "ADMIN":
            login_user(self.client, self.admin)
        else:
            register_and_login(self.client, email="prof@example.com", role="PROFESSOR")

    def test_create_career_and_requirements(self):
        self.login()
        res = self.client.post(
            ADMIN_CAREERS_URL,
            {
                "title": "Android Developer",
                "category": "Mobile Development",
                "education": "B.Tech / B.E.",
                "description": "Builds Android apps.",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        career_pk = res.data["id"]

        kotlin = Skill.objects.get(name="Kotlin")
        req = self.client.post(
            f"{ADMIN_CAREERS_URL}/{career_pk}/requirements",
            {"skill": kotlin.pk, "target_level": 75, "importance": "HIGH"},
            format="json",
        )
        self.assertEqual(req.status_code, status.HTTP_201_CREATED)
        self.assertEqual(req.data["target_level"], 75)

        detail = self.client.get(f"{ADMIN_CAREERS_URL}/{career_pk}")
        self.assertEqual(detail.data["requirements"][0]["skill"]["name"], "Kotlin")

    def test_duplicate_requirement_rejected(self):
        self.login()
        career = make_career("Backend Developer", [("Python", 80, "HIGH")])
        python = Skill.objects.get(name="Python")
        res = self.client.post(
            f"{ADMIN_CAREERS_URL}/{career.pk}/requirements",
            {"skill": python.pk, "target_level": 60, "importance": "LOW"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_target_level_range_validated(self):
        self.login()
        career = make_career("Backend Developer")
        python = Skill.objects.get(name="Python")
        res = self.client.post(
            f"{ADMIN_CAREERS_URL}/{career.pk}/requirements",
            {"skill": python.pk, "target_level": 150, "importance": "HIGH"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_and_delete_requirement(self):
        self.login()
        career = make_career("Backend Developer", [("Python", 80, "HIGH")])
        req = career.requirements.get()
        patch = self.client.patch(
            f"{ADMIN_CAREERS_URL}/{career.pk}/requirements/{req.pk}",
            {"target_level": 90},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["target_level"], 90)

        delete = self.client.delete(
            f"{ADMIN_CAREERS_URL}/{career.pk}/requirements/{req.pk}"
        )
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(career.requirements.count(), 0)

    def test_update_and_delete_career(self):
        self.login()
        career = make_career("Backend Developer")
        patch = self.client.patch(
            f"{ADMIN_CAREERS_URL}/{career.pk}",
            {"salary_range": "₹10–30 LPA", "is_active": False},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        career.refresh_from_db()
        self.assertEqual(career.salary_range, "₹10–30 LPA")
        self.assertFalse(career.is_active)

        delete = self.client.delete(f"{ADMIN_CAREERS_URL}/{career.pk}")
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)

    def test_professor_cannot_manage_careers(self):
        self.login(role="PROFESSOR")
        res = self.client.post(
            ADMIN_CAREERS_URL, {"title": "Nope"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_set_matching_fields(self):
        self.login()
        res = self.client.post(
            ADMIN_CAREERS_URL,
            {
                "title": "ML Engineer",
                "category": "Data & AI",
                "domain_keywords": "ml, model, deployment, python",
                "learning_areas": "MLOps, Model Monitoring",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        career = Career.objects.get(title="ML Engineer")
        self.assertEqual(career.domain_keywords_list[0], "ml")
        self.assertEqual(career.learning_areas, "MLOps, Model Monitoring")


class MatchingEngineTests(APITestCase):
    """Unit-style tests of the four-signal matching algorithm."""

    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.profile = StudentProfile.objects.get(user=self.student)

    def backend_career(self):
        return make_career(
            "Backend Developer",
            [("Python", 80, "HIGH"), ("Git", 60, "MEDIUM")],
        )

    def match_for(self, career):
        requirements = list(career.requirements.select_related("skill"))
        scores = {us.skill_id: us.score for us in UserSkill.objects.filter(user=self.student)}
        projects = list(Project.objects.filter(user=self.student))
        return career_match(career, requirements, scores, self.profile, projects)

    def test_all_signals_combine_into_match_percentage(self):
        career = self.backend_career()
        career.domain_keywords = "backend, api, server, software, development"
        career.save()
        give_skill(self.student, "Python", assessment_score=90)
        give_skill(self.student, "Git", assessment_score=70)
        self.profile.interests = "backend systems, apis and servers"
        self.profile.preferred_domain = "Backend"
        self.profile.career_goal = "Software Development Engineer"
        self.profile.save()
        Project.objects.create(
            user=self.student,
            name="API Service",
            technologies="Python, Django REST Framework",
        )

        match = self.match_for(career)
        # Skills 100 (both met) · interests 60 (backend/api/server of 5) ·
        # projects 100 · goal 50 (software/development of 4 terms)
        expected = round(
            100.0 * SKILL_WEIGHT
            + 60.0 * INTEREST_WEIGHT
            + 100.0 * PROJECT_WEIGHT
            + 50.0 * 0.05,
            1,
        )
        self.assertEqual(match["match_percentage"], expected)
        self.assertEqual(match["breakdown"], {"skills": 100.0, "interests": 60.0, "projects": 100.0, "goal": 50.0})
        self.assertEqual(match["matching_skills"], ["Python", "Git"])
        self.assertEqual(match["missing_skills"], [])
        self.assertIn("You meet 2 of 2 required skills", match["explanation"])
        self.assertTrue(match["recommended_next_steps"])

    def test_gaps_are_listed_and_drive_next_steps(self):
        career = self.backend_career()
        give_skill(self.student, "Python", assessment_score=90)
        # Git deliberately missing -> full gap
        match = self.match_for(career)
        self.assertEqual(match["matching_skills"], ["Python"])
        self.assertEqual(match["missing_skills"], ["Git"])
        # Python met (weight 3) + Git missing (weight 2) -> 3/5 = 60
        self.assertEqual(match["breakdown"]["skills"], 60.0)
        self.assertIn("Git", match["recommended_next_steps"][0])

    def test_importance_weighting_boosts_high_requirements(self):
        career = make_career(
            "Weighted Career",
            [("Python", 80, "HIGH"), ("Git", 60, "LOW")],
        )
        give_skill(self.student, "Python", assessment_score=90)
        match = self.match_for(career)
        # Python met (3 weight) + Git missing (1 weight) -> 3/4 = 75, not 50
        self.assertEqual(match["breakdown"]["skills"], 75.0)

    def test_empty_profile_scores_zero_and_advises(self):
        career = self.backend_career()
        match = self.match_for(career)
        self.assertEqual(match["match_percentage"], 0.0)
        self.assertEqual(match["missing_skills"], ["Python", "Git"])
        self.assertIn("Add skills, projects and interests", match["explanation"])

    def test_full_requirement_fit_caps_skill_signal_at_100(self):
        career = make_career("Easy Career", [("Python", 20, "LOW")])
        give_skill(self.student, "Python", assessment_score=95)
        match = self.match_for(career)
        self.assertEqual(match["breakdown"]["skills"], 100.0)
        self.assertIn("You meet every requirement", match["recommended_next_steps"][0])


class CareerMatchApiTests(APITestCase):
    """Endpoint behaviour of GET /careers/matches."""

    MATCHES_URL = "/api/v1/careers/matches"

    def setUp(self):
        ensure_skill_catalog()
        self.backend = make_career(
            "Backend Developer",
            [("Python", 80, "HIGH"), ("Django", 70, "HIGH")],
        )
        self.data_scientist = make_career(
            "Data Scientist",
            [("Python", 85, "HIGH"), ("Statistics", 75, "HIGH")],
        )
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        # Strong backend profile: Python + Django, no statistics
        give_skill(self.student, "Python", assessment_score=90)
        give_skill(self.student, "Django", assessment_score=80)

    def test_matches_are_ranked_highest_first_with_full_payload(self):
        res = self.client.get(self.MATCHES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        matches = res.data["matches"]
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["career"]["title"], "Backend Developer")
        percentages = [m["match_percentage"] for m in matches]
        self.assertEqual(percentages, sorted(percentages, reverse=True))
        first = matches[0]
        for key in [
            "match_percentage",
            "matching_skills",
            "missing_skills",
            "breakdown",
            "explanation",
            "recommended_next_steps",
        ]:
            self.assertIn(key, first)
        self.assertIn("guidance", res.data["disclaimer"])
        self.assertIn("Python", first["matching_skills"])
        self.assertIn("Statistics", matches[1]["missing_skills"])

    def test_career_payload_includes_learning_areas(self):
        self.backend.domain_keywords = "backend, api, server"
        self.backend.learning_areas = "System Design, REST APIs"
        self.backend.save()
        res = self.client.get(self.MATCHES_URL)
        backend = next(
            m for m in res.data["matches"] if m["career"]["title"] == "Backend Developer"
        )
        self.assertEqual(backend["career"]["learning_areas"], "System Design, REST APIs")

    def test_two_students_get_different_rankings(self):
        register_and_login(self.client, email="arjun@example.com")
        arjun = User.objects.get(email="arjun@example.com")
        give_skill(arjun, "Statistics", assessment_score=95)
        give_skill(arjun, "Python", assessment_score=70)

        login_user(self.client, self.student)
        riya = self.client.get(self.MATCHES_URL).data["matches"]
        login_user(self.client, arjun)
        arjun_res = self.client.get(self.MATCHES_URL).data["matches"]

        self.assertEqual(riya[0]["career"]["title"], "Backend Developer")
        self.assertEqual(arjun_res[0]["career"]["title"], "Data Scientist")

    def test_anonymous_is_rejected(self):
        self.client.credentials()
        res = self.client.get(self.MATCHES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_cannot_view_another_student(self):
        register_and_login(self.client, email="arjun@example.com")
        res = self.client.get(self.MATCHES_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_needs_student_id_and_can_read_any(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.get(self.MATCHES_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        res = self.client.get(self.MATCHES_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["matches"][0]["career"]["title"], "Backend Developer")

    def test_admin_can_read_any_student(self):
        admin = User.objects.create_user(
            username="boss",
            email="boss@example.com",
            password=PASSWORD,
            role=User.Role.ADMIN,
        )
        login_user(self.client, admin)
        res = self.client.get(self.MATCHES_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_inactive_careers_excluded(self):
        make_career("Retired Role", [("Python", 80, "HIGH")])
        Career.objects.filter(title="Retired Role").update(is_active=False)
        res = self.client.get(self.MATCHES_URL)
        titles = [m["career"]["title"] for m in res.data["matches"]]
        self.assertNotIn("Retired Role", titles)

