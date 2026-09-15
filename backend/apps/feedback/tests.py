"""API tests for the career feedback loop (Phase 12)."""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.applications.models import Application
from apps.careers.models import Career, CareerSkillRequirement
from apps.learning.models import LearningResource
from apps.opportunities.models import Opportunity, OpportunityRequirement
from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.users.models import User

from .models import ApplicationFeedback

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
FEEDBACK_URL = "/api/v1/feedback"
ADMIN_APPLICATIONS_URL = "/api/v1/admin/applications"
ROADMAP_URL = "/api/v1/learning/roadmap"
DASHBOARD_URL = "/api/v1/students/dashboard-summary"

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
        user=user, skill=skill, proficiency_level=proficiency,
        assessment_score=assessment_score,
    )


def make_opportunity(requirements=()):
    opp = Opportunity.objects.create(
        title="Backend Intern",
        company="Acme Corp",
        opportunity_type="INTERNSHIP",
        description="Build APIs.",
        status=Opportunity.Status.ACTIVE,
    )
    for name, min_level in requirements:
        OpportunityRequirement.objects.create(
            opportunity=opp, skill=Skill.objects.get(name=name), min_level=min_level
        )
    return opp


def make_resource(skill_name, title, rtype="COURSE", level="BEGINNER"):
    return LearningResource.objects.create(
        title=title, skill=Skill.objects.get(name=skill_name),
        type=rtype, level=level, url="https://example.com/" + title.replace(" ", "-"),
    )


def make_career(title="Backend Developer", requirements=()):
    career = Career.objects.create(title=title, category="Software Development")
    for name, target, importance in requirements:
        CareerSkillRequirement.objects.create(
            career=career,
            skill=Skill.objects.get(name=name),
            target_level=target,
            importance=importance,
        )
    return career


class FeedbackGenerationTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.opp = make_opportunity(
            [("Python", 70), ("Data Structures & Algorithms", 70)]
        )
        self.app = Application.objects.create(
            student=self.student, opportunity=self.opp, status=Application.Status.APPLIED
        )
        self.admin = User.objects.create_user(
            username="boss", email="boss@example.com",
            password=PASSWORD, role=User.Role.ADMIN,
        )

    def reject(self):
        login_user(self.client, self.admin)
        return self.client.patch(
            f"{ADMIN_APPLICATIONS_URL}/{self.app.pk}",
            {"status": "REJECTED"}, format="json",
        )

    def test_rejection_generates_feedback_with_real_gaps(self):
        give_skill(self.student, "Python", assessment_score=80)  # meets 70 -> no gap
        make_resource("Data Structures & Algorithms", "DSA Crash Course")
        res = self.reject()
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        feedback = ApplicationFeedback.objects.get(application=self.app)
        self.assertEqual(feedback.kind, "REJECTED")
        self.assertEqual(feedback.status, "PENDING")
        # Only the unmet requirement becomes a gap; Python (80 >= 70) does not.
        self.assertEqual(feedback.gaps.count(), 1)
        gap = feedback.gaps.get()
        self.assertEqual(gap.skill.name, "Data Structures & Algorithms")
        self.assertEqual(float(gap.current_level), 0.0)
        self.assertEqual(gap.required_level, 70)
        self.assertEqual(gap.gap_class, "HIGH")
        self.assertIn("Data Structures & Algorithms", feedback.summary)
        self.assertIn("Acme Corp", feedback.summary)

    def test_selection_records_an_achievement(self):
        login_user(self.client, self.admin)
        self.client.patch(
            f"{ADMIN_APPLICATIONS_URL}/{self.app.pk}",
            {"status": "SELECTED"}, format="json",
        )
        feedback = ApplicationFeedback.objects.get(application=self.app)
        self.assertEqual(feedback.kind, "SELECTED")
        self.assertEqual(feedback.gaps.count(), 0)
        self.assertIn("Congratulations", feedback.summary)

    def test_generation_is_idempotent_and_repairs(self):
        self.reject()
        self.reject()  # same status again -> view skips, but service stays safe
        self.assertEqual(ApplicationFeedback.objects.filter(application=self.app).count(), 1)

    def test_no_automatic_profile_or_skill_changes(self):
        give_skill(self.student, "Python", assessment_score=50)
        skills_before = list(
            UserSkill.objects.filter(user=self.student).values_list("skill_id", "assessment_score")
        )
        self.reject()
        skills_after = list(
            UserSkill.objects.filter(user=self.student).values_list("skill_id", "assessment_score")
        )
        self.assertEqual(skills_before, skills_after)
        # No new UserSkill rows for the gap skills either.
        self.assertFalse(
            UserSkill.objects.filter(
                user=self.student, skill__name="Data Structures & Algorithms"
            ).exists()
        )

    def test_recommendations_come_from_the_live_catalog(self):
        make_resource("Data Structures & Algorithms", "DSA Crash Course", "COURSE")
        make_resource("Data Structures & Algorithms", "LeetCode Practice", "PRACTICE")
        self.reject()
        login_user(self.client, self.student)  # back to the student's session
        res = self.client.get(f"{FEEDBACK_URL}")
        gap = res.data[0]["gaps"][0]
        kinds = [r["kind"] for r in gap["recommendations"]]
        self.assertIn("COURSE", kinds)
        self.assertIn("PRACTICE", kinds)
        linked = [r for r in gap["recommendations"] if r["resource_id"]]
        self.assertTrue(linked)
        self.assertTrue(all(r["url"] for r in linked))


class StudentFeedbackTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.opp = make_opportunity([("Python", 70)])
        self.app = Application.objects.create(
            student=self.student, opportunity=self.opp, status=Application.Status.REJECTED
        )
        from apps.feedback.services import generate_application_feedback

        generate_application_feedback(self.app)
        self.feedback = ApplicationFeedback.objects.get(application=self.app)

    def test_list_is_own_only_with_filters(self):
        register_and_login(self.client, email="arjun@example.com")
        arjun = User.objects.get(email="arjun@example.com")
        opp2 = make_opportunity()
        app2 = Application.objects.create(
            student=arjun, opportunity=opp2, status=Application.Status.SELECTED
        )
        from apps.feedback.services import generate_application_feedback

        generate_application_feedback(app2)

        login_user(self.client, self.student)
        res = self.client.get(FEEDBACK_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.feedback.pk)
        self.assertIn("opportunity", res.data[0])
        self.assertEqual(res.data[0]["opportunity"]["title"], "Backend Intern")

        res = self.client.get(FEEDBACK_URL, {"kind": "SELECTED"})
        self.assertEqual(res.data, [])
        res = self.client.get(FEEDBACK_URL, {"kind": "bogus"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detail_is_owner_only(self):
        res = self.client.get(f"{FEEDBACK_URL}/{self.feedback.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        register_and_login(self.client, email="arjun@example.com")
        res = self.client.get(f"{FEEDBACK_URL}/{self.feedback.pk}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_edits_notes_only(self):
        res = self.client.patch(
            f"{FEEDBACK_URL}/{self.feedback.pk}",
            {"notes": "Focus on Python projects this month."}, format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.notes, "Focus on Python projects this month.")

        res = self.client.patch(
            f"{FEEDBACK_URL}/{self.feedback.pk}", {"status": "ACCEPTED"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_and_dismiss(self):
        res = self.client.post(f"{FEEDBACK_URL}/{self.feedback.pk}/accept")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, "ACCEPTED")

        res = self.client.post(f"{FEEDBACK_URL}/{self.feedback.pk}/dismiss")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, "DISMISSED")

    def test_selection_feedback_cannot_be_accepted(self):
        opp2 = make_opportunity()
        app2 = Application.objects.create(
            student=self.student, opportunity=opp2, status=Application.Status.SELECTED
        )
        from apps.feedback.services import generate_application_feedback

        generate_application_feedback(app2)
        selected = ApplicationFeedback.objects.get(application=app2)
        res = self.client.post(f"{FEEDBACK_URL}/{selected.pk}/accept")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_student_cannot_act_on_feedback(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.post(f"{FEEDBACK_URL}/{self.feedback.pk}/accept")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class FeedbackRoadmapTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.opp = make_opportunity([("Data Structures & Algorithms", 70)])
        self.app = Application.objects.create(
            student=self.student, opportunity=self.opp, status=Application.Status.REJECTED
        )
        from apps.feedback.services import generate_application_feedback

        generate_application_feedback(self.app)
        self.feedback = ApplicationFeedback.objects.get(application=self.app)
        make_resource("Data Structures & Algorithms", "DSA Crash Course", "COURSE")
        make_resource("Data Structures & Algorithms", "LeetCode Practice", "PRACTICE")
        make_resource("Python", "Python 101", "COURSE")
        self.career = make_career("Backend Developer", [("Python", 80, "HIGH")])

    def roadmap(self):
        return self.client.get(ROADMAP_URL, {"career_id": self.career.pk})

    def test_accepted_feedback_joins_the_roadmap(self):
        res = self.roadmap()
        self.assertNotIn("feedback_roadmap", res.data)

        self.client.post(f"{FEEDBACK_URL}/{self.feedback.pk}/accept")
        res = self.roadmap()
        feedback_skills = res.data.get("feedback_roadmap", [])
        self.assertEqual(len(feedback_skills), 1)
        entry = feedback_skills[0]
        self.assertEqual(entry["skill"]["name"], "Data Structures & Algorithms")
        self.assertEqual(entry["source"]["company"], "Acme Corp")
        # Resource + practice steps carry the real catalog items.
        steps = {s["key"]: s for s in entry["steps"]}
        self.assertEqual(
            [i["title"] for i in steps["resource"]["items"]], ["DSA Crash Course"]
        )
        self.assertEqual(
            [i["title"] for i in steps["practice"]["items"]], ["LeetCode Practice"]
        )
        # Progress is merged across career + feedback items.
        self.assertEqual(res.data["progress"]["total_resources"], 3)

    def test_dismissed_feedback_stays_out_of_the_roadmap(self):
        self.client.post(f"{FEEDBACK_URL}/{self.feedback.pk}/dismiss")
        res = self.roadmap()
        self.assertNotIn("feedback_roadmap", res.data)

    def test_closed_gap_drops_out_of_the_roadmap(self):
        self.client.post(f"{FEEDBACK_URL}/{self.feedback.pk}/accept")
        # Student improves DSA past the posting's bar -> nothing left to learn.
        give_skill(self.student, "Data Structures & Algorithms", assessment_score=80)
        res = self.roadmap()
        self.assertNotIn("feedback_roadmap", res.data)


class FeedbackAccessAndDashboardTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.opp = make_opportunity([("Python", 70)])
        self.app = Application.objects.create(
            student=self.student, opportunity=self.opp, status=Application.Status.REJECTED
        )
        from apps.feedback.services import generate_application_feedback

        generate_application_feedback(self.app)

    def test_professor_reads_via_student_id(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.get(FEEDBACK_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        res = self.client.get(FEEDBACK_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_student_cannot_use_the_staff_list(self):
        res = self.client.get(FEEDBACK_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # still just their own

    def test_dashboard_counts_and_recent_achievements(self):
        Application.objects.create(
            student=self.student, opportunity=make_opportunity(),
            status=Application.Status.APPLIED,
        )
        opp2 = make_opportunity([("Python", 70)])
        app2 = Application.objects.create(
            student=self.student, opportunity=opp2, status=Application.Status.SELECTED
        )
        from apps.feedback.services import generate_application_feedback

        generate_application_feedback(app2)

        res = self.client.get(DASHBOARD_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # 1 rejected (setUp) + 1 applied + 1 selected.
        self.assertEqual(res.data["applications_count"], 3)
        self.assertEqual(res.data["achievements_count"], 1)
        self.assertEqual(res.data["feedback_pending_count"], 1)
        self.assertEqual(len(res.data["recent_achievements"]), 1)
        self.assertEqual(res.data["recent_achievements"][0]["company"], "Acme Corp")