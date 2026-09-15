"""API tests for opportunities browse + admin management (Phase 9)."""

import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.students.models import Project, StudentProfile
from apps.users.models import User

from .models import Opportunity, OpportunityRequirement
from .seed_data import ensure_demo_opportunities
from .services import (
    PROFILE_WEIGHT,
    PROJECT_WEIGHT,
    SKILL_WEIGHT,
    opportunity_match,
)

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
OPP_URL = "/api/v1/opportunities"
ADMIN_OPP_URL = "/api/v1/admin/opportunities"

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


def give_skill(user, name, assessment_score=None, proficiency=1):
    skill = Skill.objects.get(name=name)
    return UserSkill.objects.create(
        user=user,
        skill=skill,
        proficiency_level=proficiency,
        assessment_score=assessment_score,
    )


def make_opportunity(
    title="Backend Intern",
    company="Acme Corp",
    opp_type="INTERNSHIP",
    requirements=(),
    status_="ACTIVE",
    deadline_delta=10,
    **extra,
):
    deadline = None
    if deadline_delta is not None:
        deadline = datetime.date.today() + datetime.timedelta(days=deadline_delta)
    opportunity = Opportunity.objects.create(
        title=title,
        company=company,
        opportunity_type=opp_type,
        description=f"Description for {title}",
        location=extra.pop("location", "Bengaluru"),
        is_remote=extra.pop("is_remote", False),
        deadline=deadline,
        compensation=extra.pop("compensation", "₹20k/month"),
        status=status_,
        **extra,
    )
    for name, min_level in requirements:
        skill = Skill.objects.get(name=name)
        OpportunityRequirement.objects.create(
            opportunity=opportunity, skill=skill, min_level=min_level
        )
    return opportunity


class BrowseTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")

    def test_only_active_future_or_open_postings_are_visible(self):
        visible = make_opportunity("Visible Intern", requirements=[("Python", 60)])
        open_ended = make_opportunity(
            "Open Ended Job", company="Now Co", deadline_delta=None
        )
        past = make_opportunity(
            "Expired Posting", company="Old Co", deadline_delta=-5
        )
        draft = make_opportunity(
            "Draft Posting", company="Draft Co", status_="DRAFT"
        )
        closed = make_opportunity(
            "Closed Posting", company="Closed Co", status_="CLOSED"
        )

        res = self.client.get(OPP_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = {item["title"] for item in res.data}
        self.assertIn(visible.title, titles)
        self.assertIn(open_ended.title, titles)
        self.assertNotIn(past.title, titles)
        self.assertNotIn(draft.title, titles)
        self.assertNotIn(closed.title, titles)

    def test_past_deadline_posting_returns_404_on_detail(self):
        past = make_opportunity("Expired Detail", deadline_delta=-1)
        res = self.client.get(f"{OPP_URL}/{past.pk}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_is_rejected(self):
        self.client.credentials()
        res = self.client.get(OPP_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchFilterSortTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        make_opportunity(
            "Python Backend Intern", company="Zoho", opp_type="INTERNSHIP",
            location="Chennai", requirements=[("Python", 70)],
        )
        make_opportunity(
            "Frontend Engineer", company="CRED", opp_type="JOB",
            location="Bengaluru", requirements=[("JavaScript", 75)],
        )
        make_opportunity(
            "Remote ML Intern", company="Fractal", opp_type="INTERNSHIP",
            location="Mumbai", is_remote=True,
            requirements=[("Machine Learning", 65)],
        )

    def test_search_matches_title_company_and_description(self):
        res = self.client.get(OPP_URL, {"search": "zoho"})
        self.assertEqual([o["company"] for o in res.data], ["Zoho"])
        res = self.client.get(OPP_URL, {"search": "Frontend"})
        self.assertEqual(len(res.data), 1)
        res = self.client.get(OPP_URL, {"search": "zzz-none"})
        self.assertEqual(res.data, [])

    def test_type_filter(self):
        res = self.client.get(OPP_URL, {"type": "JOB"})
        self.assertEqual([o["opportunity_type"] for o in res.data], ["JOB"])
        res = self.client.get(OPP_URL, {"type": "HACKATHON"})
        self.assertEqual(res.data, [])

    def test_location_and_remote_filters(self):
        res = self.client.get(OPP_URL, {"location": "chennai"})
        self.assertEqual([o["title"] for o in res.data], ["Python Backend Intern"])
        res = self.client.get(OPP_URL, {"remote": "1"})
        self.assertEqual([o["title"] for o in res.data], ["Remote ML Intern"])

    def test_deadline_sort_soonest_first(self):
        res = self.client.get(OPP_URL, {"sort": "deadline"})
        deadlines = [o["deadline"] for o in res.data if o["deadline"]]
        self.assertEqual(deadlines, sorted(deadlines))

    def test_match_sort_best_first(self):
        give_skill(self.student, "Machine Learning", assessment_score=90)
        res = self.client.get(OPP_URL, {"sort": "match"})
        percentages = [o["match_percentage"] for o in res.data]
        self.assertEqual(percentages, sorted(percentages, reverse=True))
        # ML requirement 65 met at 90 -> 100 skills -> 70% combined (no other
        # profile/project signals in this fixture).
        self.assertEqual(res.data[0]["title"], "Remote ML Intern")
        self.assertEqual(res.data[0]["match_percentage"], 70.0)
        self.assertIn("created_at", res.data[0])


class DetailAndMatchTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")

    def test_detail_includes_full_payload_and_skill_breakdown(self):
        opp = make_opportunity(
            "Backend Intern",
            requirements=[("Python", 80), ("Django", 70)],
            eligibility="B.Tech CSE, CGPA > 7",
            application_link="https://apply.example.com",
        )
        give_skill(self.student, "Python", assessment_score=80)
        give_skill(self.student, "Django", assessment_score=35)

        res = self.client.get(f"{OPP_URL}/{opp.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data
        self.assertEqual(data["title"], "Backend Intern")
        self.assertIn("eligibility", data)
        self.assertIn("application_link", data)
        self.assertIn("description", data)
        self.assertEqual(data["compensation"], "₹20k/month")
        self.assertEqual(data["deadline"], str(datetime.date.today() + datetime.timedelta(days=10)))

        rows = {row["skill"]["name"]: row for row in data["requirements"]}
        self.assertEqual(rows["Python"]["my_level"], 80)
        self.assertTrue(rows["Python"]["met"])
        self.assertEqual(rows["Django"]["my_level"], 35)
        self.assertFalse(rows["Django"]["met"])
        self.assertEqual(rows["Django"]["min_level"], 70)
        self.assertEqual(data["skill_names"], ["Python", "Django"])

    def test_match_percentage_is_a_real_average(self):
        opp = make_opportunity(
            "Backend Intern", requirements=[("Python", 80), ("Django", 70)]
        )
        give_skill(self.student, "Python", assessment_score=80)
        give_skill(self.student, "Django", assessment_score=35)
        res = self.client.get(f"{OPP_URL}/{opp.pk}")
        # Skills 75 (Python 80/80, Django 35/70); empty profile/projects in
        # this fixture -> combined = 75 * 0.7 = 52.5
        self.assertEqual(res.data["match_percentage"], 52.5)
        self.assertEqual(res.data["breakdown"], {"skills": 75.0, "profile": 0.0, "projects": 0.0})
        self.assertEqual(res.data["matching_skills"], ["Python"])
        self.assertEqual(res.data["missing_skills"], ["Django"])
        self.assertEqual(res.data["matched_requirements"], 1)
        self.assertEqual(res.data["total_requirements"], 2)
        self.assertIn("You meet 1 of 2", res.data["explanation"])

    def test_missing_skill_counts_zero(self):
        opp = make_opportunity("Strict Intern", requirements=[("Python", 80)])
        give_skill(self.student, "Python", assessment_score=50)
        res = self.client.get(f"{OPP_URL}/{opp.pk}")
        # skills 62.5 (50/80) * 0.7 -> 43.8
        self.assertEqual(res.data["match_percentage"], 43.8)

    def test_requirement_without_level_met_counts_full(self):
        opp = make_opportunity("Level Free Intern", requirements=[("Python", 0)])
        res = self.client.get(f"{OPP_URL}/{opp.pk}")
        # skills 100 * 0.7 = 70
        self.assertEqual(res.data["match_percentage"], 70.0)
        self.assertIn("You meet 1 of 1", res.data["explanation"])

    def test_no_requirements_matches_from_profile_and_projects(self):
        opp = make_opportunity("No Skills Posting")
        res = self.client.get(f"{OPP_URL}/{opp.pk}")
        # No skills component; empty profile/projects -> 0 (not null)
        self.assertEqual(res.data["match_percentage"], 0.0)
        self.assertIsNone(res.data["breakdown"]["skills"])
        self.assertEqual(res.data["total_requirements"], 0)
        self.assertIn("lists no specific required skills", res.data["explanation"])

    def test_different_students_get_different_matches(self):
        opp = make_opportunity("Selective Intern", requirements=[("Python", 80)])
        give_skill(self.student, "Python", assessment_score=90)

        register_and_login(self.client, email="arjun@example.com")
        arjun = User.objects.get(email="arjun@example.com")
        give_skill(arjun, "Python", assessment_score=30)

        login_user(self.client, self.student)
        riya_match = self.client.get(f"{OPP_URL}/{opp.pk}").data["match_percentage"]
        login_user(self.client, arjun)
        arjun_match = self.client.get(f"{OPP_URL}/{opp.pk}").data["match_percentage"]
        self.assertEqual(riya_match, 70.0)  # 100 skills * 0.7
        self.assertEqual(arjun_match, 26.2)  # 37.5 skills * 0.7


class AccessControlTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.opp = make_opportunity("Target Intern", requirements=[("Python", 60)])

    def test_student_cannot_pass_another_student_id(self):
        register_and_login(self.client, email="arjun@example.com")
        res = self.client.get(OPP_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_analyzes_any_student_with_student_id(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        give_skill(self.student, "Python", assessment_score=60)
        res = self.client.get(OPP_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        by_id = {o["id"]: o for o in res.data}
        # Python 60 required, student at 60 -> skills 100 * 0.7 = 70
        self.assertEqual(by_id[self.opp.pk]["match_percentage"], 70.0)
        self.assertIn("Python", by_id[self.opp.pk]["explanation"])

    def test_professor_browsing_without_student_id_gets_no_match(self):
        register_and_login(self.client, email="prof2@example.com", role="PROFESSOR")
        res = self.client.get(OPP_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNone(res.data[0]["match_percentage"])
        self.assertEqual(res.data[0]["matching_skills"], [])


class AdminCrudTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.admin = User.objects.create_user(
            username="boss",
            email="boss@example.com",
            password=PASSWORD,
            role=User.Role.ADMIN,
        )

    def login_admin(self):
        login_user(self.client, self.admin)

    def test_create_opportunity_and_requirements(self):
        self.login_admin()
        res = self.client.post(
            ADMIN_OPP_URL,
            {
                "title": "Android Intern",
                "company": "Nova Apps",
                "opportunity_type": "INTERNSHIP",
                "description": "Build Android features.",
                "status": "ACTIVE",
                "deadline": str(datetime.date.today() + datetime.timedelta(days=15)),
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pk = res.data["id"]
        kotlin = Skill.objects.get(name="Kotlin")
        req = self.client.post(
            f"{ADMIN_OPP_URL}/{pk}/requirements",
            {"skill": kotlin.pk, "min_level": 75},
            format="json",
        )
        self.assertEqual(req.status_code, status.HTTP_201_CREATED)
        self.assertEqual(req.data["min_level"], 75)
        detail = self.client.get(f"{ADMIN_OPP_URL}/{pk}")
        self.assertEqual(detail.data["requirements"][0]["skill"]["name"], "Kotlin")

    def test_admin_list_shows_all_statuses(self):
        self.login_admin()
        draft = make_opportunity("Draft Posting", company="D", status_="DRAFT")
        active = make_opportunity("Active Posting", company="A")
        res = self.client.get(ADMIN_OPP_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = {o["title"] for o in res.data}
        self.assertIn(draft.title, titles)
        self.assertIn(active.title, titles)

    def test_update_delete_opportunity(self):
        self.login_admin()
        opp = make_opportunity("Editable", company="E")
        patch = self.client.patch(
            f"{ADMIN_OPP_URL}/{opp.pk}",
            {"compensation": "₹30k/month", "status": "CLOSED"},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        opp.refresh_from_db()
        self.assertEqual(opp.compensation, "₹30k/month")
        self.assertEqual(opp.status, "CLOSED")
        delete = self.client.delete(f"{ADMIN_OPP_URL}/{opp.pk}")
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)

    def test_activate_and_deactivate_toggle_student_visibility(self):
        self.login_admin()
        opp = make_opportunity("Togglable", company="T", status_="DRAFT")
        # Draft is invisible to students
        register_and_login(self.client, email="riya@example.com")
        titles = [o["title"] for o in self.client.get(OPP_URL).data]
        self.assertNotIn(opp.title, titles)
        # Admin activates -> visible
        login_user(self.client, self.admin)
        res = self.client.post(f"{ADMIN_OPP_URL}/{opp.pk}/activate")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        login_user(self.client, User.objects.get(email="riya@example.com"))
        titles = [o["title"] for o in self.client.get(OPP_URL).data]
        self.assertIn(opp.title, titles)
        # Admin deactivates -> hidden again
        login_user(self.client, self.admin)
        res = self.client.post(f"{ADMIN_OPP_URL}/{opp.pk}/deactivate")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        login_user(self.client, User.objects.get(email="riya@example.com"))
        titles = [o["title"] for o in self.client.get(OPP_URL).data]
        self.assertNotIn(opp.title, titles)

    def test_duplicate_and_out_of_range_requirements_rejected(self):
        self.login_admin()
        opp = make_opportunity("Req Ops", company="R", requirements=[("Python", 60)])
        python = Skill.objects.get(name="Python")
        dup = self.client.post(
            f"{ADMIN_OPP_URL}/{opp.pk}/requirements",
            {"skill": python.pk, "min_level": 80},
            format="json",
        )
        self.assertEqual(dup.status_code, status.HTTP_400_BAD_REQUEST)
        git = Skill.objects.get(name="Git")
        bad = self.client.post(
            f"{ADMIN_OPP_URL}/{opp.pk}/requirements",
            {"skill": git.pk, "min_level": 150},
            format="json",
        )
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_and_professor_cannot_manage(self):
        register_and_login(self.client, email="riya@example.com")
        res = self.client.post(
            ADMIN_OPP_URL,
            {"title": "Nope", "company": "X", "opportunity_type": "JOB"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.post(f"{ADMIN_OPP_URL}/1/activate")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_requirement_delete(self):
        self.login_admin()
        opp = make_opportunity("Req Del", company="D", requirements=[("Python", 70)])
        req = opp.requirements.get()
        delete = self.client.delete(f"{ADMIN_OPP_URL}/{opp.pk}/requirements/{req.pk}")
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(opp.requirements.count(), 0)


class SmartEngineUnitTests(APITestCase):
    """Unit-style tests of the Phase 10 signal combination."""

    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.profile = StudentProfile.objects.get(user=self.student)
        # Vocabulary of this posting: pandas, analytics, intern, data (+ req skills)
        self.opp = make_opportunity(
            "Panda Analytics Intern",
            company="Data Panda",
            requirements=[("Python", 70), ("Pandas", 70), ("SQL", 70)],
        )

    def requirements(self):
        return list(self.opp.requirements.select_related("skill"))

    def run_match(self):
        scores = {us.skill_id: us.score for us in UserSkill.objects.filter(user=self.student)}
        return opportunity_match(
            self.opp,
            self.requirements(),
            scores,
            self.profile,
            list(Project.objects.filter(user=self.student)),
        )

    def test_all_signals_combine_transparently(self):
        # Skills: Python 80/70 & Pandas 70/70 met, SQL missing -> (1+1+0)/3
        give_skill(self.student, "Python", assessment_score=80)
        give_skill(self.student, "Pandas", assessment_score=70)
        # Profile: interests echo the posting vocabulary (data, analytics, panda)
        self.profile.interests = "data analytics and pandas"
        self.profile.save()
        Project.objects.create(
            user=self.student, name="Sales Dashboard", technologies="Pandas, Python"
        )

        match = self.run_match()
        skill = round((1 + 1 + 0) / 3 * 100, 1)
        # Vocabulary of this posting: panda, analytics, intern, data, internship.
        # The profile text echoes 3 of the 5 (data, analytics, panda) -> 60.
        profile_p = 60.0
        expected = round(
            skill * SKILL_WEIGHT + profile_p * PROFILE_WEIGHT + 100.0 * PROJECT_WEIGHT, 1
        )
        self.assertEqual(match.match_percentage, expected)
        self.assertEqual(match.skills_score, skill)
        self.assertEqual(match.profile_score, profile_p)
        self.assertEqual(match.projects_score, 100.0)
        self.assertEqual(match.matching_skills, ["Pandas", "Python"])
        self.assertEqual(match.missing_skills, ["SQL"])
        self.assertIn("You meet 2 of 3", match.explanation)
        self.assertTrue(any("SQL" in step for step in match.recommended_next_steps))

    def test_no_profile_signals_gives_pure_skill_weight(self):
        give_skill(self.student, "Python", assessment_score=70)
        give_skill(self.student, "Pandas", assessment_score=70)
        match = self.run_match()
        skill = round(2 / 3 * 100, 1)
        self.assertEqual(match.skills_score, skill)
        self.assertEqual(match.profile_score, 0.0)
        self.assertEqual(match.projects_score, 0.0)
        self.assertEqual(match.match_percentage, round(skill * SKILL_WEIGHT, 1))

    def test_missing_skill_drops_score_and_is_listed(self):
        give_skill(self.student, "Python", assessment_score=90)
        give_skill(self.student, "SQL", assessment_score=90)
        match = self.run_match()
        self.assertIn("Pandas", match.missing_skills)
        self.assertEqual(match.matched_requirements, 2)

    def test_no_requirements_uses_profile_and_projects_only(self):
        self.opp = make_opportunity("Data Explorer Fellowship", company="Data Panda")
        self.profile.interests = "data analytics and pandas"
        self.profile.save()
        Project.objects.create(user=self.student, name="EDA", technologies="pandas")
        match = self.run_match()
        self.assertIsNone(match.skills_score)
        self.assertGreater(match.profile_score, 0)
        self.assertGreater(match.projects_score, 0)


class RecommendationsApiTests(APITestCase):
    REC_URL = "/api/v1/opportunities/recommendations"

    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.backend = make_opportunity(
            "Backend Intern", company="Server Co",
            requirements=[("Python", 80), ("Django", 70)],
            deadline_delta=3,
        )
        self.frontend = make_opportunity(
            "Frontend Intern", company="UI Co",
            requirements=[("JavaScript", 80)],
            deadline_delta=12,
        )
        give_skill(self.student, "Python", assessment_score=90)
        give_skill(self.student, "Django", assessment_score=80)

    def test_items_ranked_by_match_with_full_explanation(self):
        res = self.client.get(self.REC_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items = res.data["items"]
        self.assertEqual(len(items), 2)
        percentages = [item["match_percentage"] for item in items]
        self.assertEqual(percentages, sorted(percentages, reverse=True))
        self.assertEqual(items[0]["title"], "Backend Intern")
        for item in items:
            self.assertIn("breakdown", item)
            self.assertIn("explanation", item)
            self.assertTrue(item["explanation"])
            self.assertIn("created_at", item)
            self.assertIn("deadline", item)
        self.assertIn("not a guarantee", res.data["disclaimer"])

    def test_gap_postings_carry_missing_skills_and_actions(self):
        res = self.client.get(self.REC_URL)
        frontend = next(i for i in res.data["items"] if i["title"] == "Frontend Intern")
        self.assertIn("JavaScript", frontend["missing_skills"])
        self.assertEqual(frontend["total_requirements"], 1)
        self.assertTrue(frontend["recommended_next_steps"])

    def test_student_cannot_request_another_student(self):
        register_and_login(self.client, email="arjun@example.com")
        res = self.client.get(self.REC_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_needs_student_id(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.get(self.REC_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        res = self.client.get(self.REC_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["items"][0]["title"], "Backend Intern")

    def test_anonymous_is_rejected(self):
        self.client.credentials()
        res = self.client.get(self.REC_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class SeedTests(APITestCase):
    def test_seed_is_idempotent(self):
        ensure_skill_catalog()
        first = ensure_demo_opportunities()
        second = ensure_demo_opportunities()
        self.assertGreater(first, 0)
        self.assertEqual(second, 0)
        self.assertEqual(Opportunity.objects.count(), first)
