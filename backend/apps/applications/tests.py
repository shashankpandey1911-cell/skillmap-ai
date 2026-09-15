"""API tests for application tracking (Phase 11)."""

import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from apps.opportunities.models import Opportunity, OpportunityRequirement
from apps.skills.seed_data import ensure_skill_catalog
from apps.users.models import User

from .models import Application

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/students/me/applications"
STAFF_LIST_URL = "/api/v1/applications"
ADMIN_URL = "/api/v1/admin/applications"
OPP_URL = "/api/v1/opportunities"

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


def make_opportunity(
    title="Backend Intern",
    company="Acme Corp",
    status_="ACTIVE",
    deadline_delta=10,
):
    return Opportunity.objects.create(
        title=title,
        company=company,
        opportunity_type="INTERNSHIP",
        description=f"Description for {title}",
        deadline=(
            datetime.date.today() + datetime.timedelta(days=deadline_delta)
            if deadline_delta is not None
            else None
        ),
        status=status_,
    )


def make_application(student, opportunity, status_=Application.Status.APPLIED):
    return Application.objects.create(student=student, opportunity=opportunity, status=status_)


class ApplyFlowTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")

    def test_student_can_apply(self):
        opp = make_opportunity()
        res = self.client.post(ME_URL, {"opportunity": opp.pk}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "APPLIED")
        self.assertEqual(res.data["opportunity"]["title"], "Backend Intern")
        self.assertIn("deadline", res.data["opportunity"])
        self.assertIsNotNone(res.data["applied_at"])

    def test_cannot_apply_twice(self):
        opp = make_opportunity()
        self.client.post(ME_URL, {"opportunity": opp.pk}, format="json")
        res = self.client.post(ME_URL, {"opportunity": opp.pk}, format="json")
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    def test_cannot_apply_to_inactive_or_expired(self):
        draft = make_opportunity("Draft Posting", status_="DRAFT")
        closed = make_opportunity("Closed Posting", status_="CLOSED")
        expired = make_opportunity("Expired Posting", deadline_delta=-2)
        for opp in (draft, closed, expired):
            res = self.client.post(ME_URL, {"opportunity": opp.pk}, format="json")
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_students_cannot_apply(self):
        self.client.credentials()
        res = self.client.post(
            ME_URL, {"opportunity": make_opportunity().pk}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.post(
            ME_URL, {"opportunity": make_opportunity().pk}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StudentListNotesTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.opp_a = make_opportunity("Python Intern", company="Nova")
        self.opp_b = make_opportunity("Data Intern", company="Nova")
        self.app = make_application(self.student, self.opp_a)

    def test_list_is_scoped_to_own_applications(self):
        register_and_login(self.client, email="arjun@example.com")
        arjun = User.objects.get(email="arjun@example.com")
        make_application(arjun, self.opp_b, status_=Application.Status.SELECTED)

        login_user(self.client, self.student)
        res = self.client.get(ME_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["opportunity"]["title"], "Python Intern")

        login_user(self.client, arjun)
        res = self.client.get(ME_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["status"], "SELECTED")

    def test_status_and_search_filters(self):
        make_application(self.student, self.opp_b, status_=Application.Status.SHORTLISTED)
        res = self.client.get(ME_URL, {"status": "SHORTLISTED"})
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["opportunity"]["title"], "Data Intern")
        res = self.client.get(ME_URL, {"status": "NOT_A_STATUS"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        res = self.client.get(ME_URL, {"search": "nova"})
        self.assertEqual(len(res.data), 2)
        res = self.client.get(ME_URL, {"search": "python"})
        self.assertEqual(len(res.data), 1)

    def test_owner_can_add_notes_but_not_touch_status(self):
        res = self.client.patch(
            f"{ME_URL}/{self.app.pk}", {"notes": "Waiting for a call back."},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.app.refresh_from_db()
        self.assertEqual(self.app.notes, "Waiting for a call back.")

        res = self.client.patch(
            f"{ME_URL}/{self.app.pk}", {"status": "SELECTED"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detail_is_owner_only(self):
        register_and_login(self.client, email="arjun@example.com")
        res = self.client.get(f"{ME_URL}/{self.app.pk}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class StaffAccessTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.app = make_application(self.student, make_opportunity())

    def test_professor_lists_any_student_but_needs_student_id(self):
        register_and_login(self.client, email="prof@example.com", role="PROFESSOR")
        res = self.client.get(STAFF_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        res = self.client.get(STAFF_LIST_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_student_cannot_use_the_staff_list(self):
        res = self.client.get(STAFF_LIST_URL, {"student_id": self.student.pk})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlowTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.app = make_application(
            self.student, make_opportunity(), status_=Application.Status.APPLIED
        )
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
            register_and_login(self.client, email="prof2@example.com", role="PROFESSOR")

    def test_admin_sees_all_applications_with_student_info(self):
        register_and_login(self.client, email="arjun@example.com")
        arjun = User.objects.get(email="arjun@example.com")
        make_application(arjun, make_opportunity("Other Intern"))
        login_user(self.client, self.admin)

        res = self.client.get(ADMIN_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertIn("student", res.data[0])
        self.assertEqual(res.data[0]["student"]["email"], "arjun@example.com")

    def test_admin_status_filter(self):
        login_user(self.client, self.admin)
        res = self.client.get(ADMIN_URL, {"status": "SELECTED"})
        self.assertEqual(res.data, [])

    def test_admin_drives_status_and_interview_date(self):
        login_user(self.client, self.admin)
        res = self.client.patch(
            f"{ADMIN_URL}/{self.app.pk}",
            {
                "status": "INTERVIEW",
                "interview_date": str(
                    datetime.date.today() + datetime.timedelta(days=7)
                ),
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.app.refresh_from_db()
        self.assertEqual(self.app.status, "INTERVIEW")
        self.assertIsNotNone(self.app.interview_date)

        res = self.client.patch(
            f"{ADMIN_URL}/{self.app.pk}", {"status": "SELECTED"}, format="json"
        )
        self.app.refresh_from_db()
        self.assertEqual(self.app.status, "SELECTED")

    def test_admin_cannot_edit_arbitrary_fields(self):
        login_user(self.client, self.admin)
        res = self.client.patch(
            f"{ADMIN_URL}/{self.app.pk}",
            {"student": self.student.pk, "status": "SELECTED"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_professor_and_student_cannot_drive_status(self):
        res = self.client.patch(
            f"{ADMIN_URL}/{self.app.pk}", {"status": "SELECTED"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        login_user(self.client, self.admin)
        # professor
        self.login(role="PROFESSOR")
        res = self.client.patch(
            f"{ADMIN_URL}/{self.app.pk}", {"status": "SELECTED"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class MyApplicationFlagTests(APITestCase):
    """The opportunity detail payload tells the UI whether the student has
    already applied."""

    def setUp(self):
        ensure_skill_catalog()
        register_and_login(self.client)
        self.student = User.objects.get(email="riya@example.com")
        self.opp = make_opportunity()

    def test_detail_has_my_application_only_after_applying(self):
        res = self.client.get(f"{OPP_URL}/{self.opp.pk}")
        self.assertIsNone(res.data["my_application"])
        self.client.post(ME_URL, {"opportunity": self.opp.pk}, format="json")
        res = self.client.get(f"{OPP_URL}/{self.opp.pk}")
        self.assertIsNotNone(res.data["my_application"])
        self.assertEqual(res.data["my_application"]["status"], "APPLIED")
