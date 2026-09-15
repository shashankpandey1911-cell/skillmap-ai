"""API tests for authentication and role-based access control."""

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"
LOGOUT_URL = "/api/v1/auth/logout"
REFRESH_URL = "/api/v1/auth/refresh"
FORGOT_URL = "/api/v1/auth/forgot-password"
RESET_URL = "/api/v1/auth/reset-password"
PROF_SUMMARY_URL = "/api/v1/professors/dashboard-summary"
ADMIN_SUMMARY_URL = "/api/v1/admin/dashboard-summary"

STUDENT_PASSWORD = "Tr0ub4dor&3"
PROFESSOR_PASSWORD = "Pr0fess0r#1"
ADMIN_PASSWORD = "Adm1n#2026"


def student_payload(**overrides):
    payload = {
        "full_name": "Riya Sharma",
        "email": "riya@example.com",
        "password": STUDENT_PASSWORD,
        "role": "STUDENT",
        "college": "NIT Trichy",
        "course": "B.Tech CSE",
        "year": 3,
    }
    payload.update(overrides)
    return payload


class RegisterTests(APITestCase):
    def test_register_student_creates_user_profile_and_tokens(self):
        res = self.client.post(REGISTER_URL, student_payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

        user = User.objects.get(email="riya@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.first_name, "Riya")
        self.assertEqual(user.last_name, "Sharma")
        self.assertEqual(user.username, "riya")  # derived from email
        self.assertTrue(hasattr(user, "student_profile"))
        self.assertEqual(user.student_profile.college, "NIT Trichy")
        self.assertEqual(user.student_profile.year, 3)

    def test_register_hashes_password(self):
        res = self.client.post(REGISTER_URL, student_payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="riya@example.com")
        self.assertNotEqual(user.password, STUDENT_PASSWORD)
        self.assertTrue(user.password.startswith("pbkdf2"))
        self.assertTrue(user.check_password(STUDENT_PASSWORD))

    def test_register_duplicate_email_rejected(self):
        self.client.post(REGISTER_URL, student_payload(), format="json")
        res = self.client.post(REGISTER_URL, student_payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_weak_password_rejected(self):
        res = self.client.post(
            REGISTER_URL,
            student_payload(password="short", email="weak@example.com"),
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", res.data)

    def test_register_admin_role_is_not_self_serve(self):
        res = self.client.post(
            REGISTER_URL,
            student_payload(role="ADMIN"),
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", res.data)

    def test_register_student_requires_college_course_year(self):
        res = self.client.post(
            REGISTER_URL,
            student_payload(college="", course="", year=None),
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("college", "course", "year"):
            self.assertIn(field, res.data)

    def test_register_professor_does_not_need_college(self):
        res = self.client.post(
            REGISTER_URL,
            {
                "full_name": "Anita Desai",
                "email": "anita@example.com",
                "password": PROFESSOR_PASSWORD,
                "role": "PROFESSOR",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="anita@example.com")
        self.assertEqual(user.role, User.Role.PROFESSOR)
        self.assertFalse(hasattr(user, "student_profile"))


class LoginTests(APITestCase):
    def setUp(self):
        self.client.post(REGISTER_URL, student_payload(), format="json")

    def test_login_with_email_returns_tokens_and_user(self):
        res = self.client.post(
            LOGIN_URL,
            {"email": "riya@example.com", "password": STUDENT_PASSWORD},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["email"], "riya@example.com")
        self.assertEqual(res.data["user"]["role"], "STUDENT")

    def test_login_with_username_also_works(self):
        res = self.client.post(
            LOGIN_URL,
            {"email": "riya", "password": STUDENT_PASSWORD},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_wrong_password_rejected(self):
        res = self.client.post(
            LOGIN_URL,
            {"email": "riya@example.com", "password": "WrongPass!123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_user_rejected(self):
        res = self.client.post(
            LOGIN_URL,
            {"email": "nobody@example.com", "password": STUDENT_PASSWORD},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user_rejected(self):
        user = User.objects.get(email="riya@example.com")
        user.is_active = False
        user.save()
        res = self.client.post(
            LOGIN_URL,
            {"email": "riya@example.com", "password": STUDENT_PASSWORD},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class SessionTests(APITestCase):
    def _register_and_login(self):
        self.client.post(REGISTER_URL, student_payload(), format="json")
        return self.client.post(
            LOGIN_URL,
            {"email": "riya@example.com", "password": STUDENT_PASSWORD},
            format="json",
        ).data

    def test_me_requires_authentication(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        tokens = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "riya@example.com")

    def test_logout_blacklists_refresh_token(self):
        tokens = self._register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        res = self.client.post(LOGOUT_URL, {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # The same refresh token must no longer work after logout.
        res = self.client.post(REFRESH_URL, {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class RoleRestrictionTests(APITestCase):
    def _tokens_for(self, payload):
        self.client.post(REGISTER_URL, payload, format="json")
        res = self.client.post(
            LOGIN_URL,
            {"email": payload["email"], "password": payload["password"]},
            format="json",
        )
        return res.data

    def _professor_payload(self):
        return {
            "full_name": "Anita Desai",
            "email": "anita@example.com",
            "password": PROFESSOR_PASSWORD,
            "role": "PROFESSOR",
        }

    def _admin_user(self):
        return User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password=ADMIN_PASSWORD,
            role=User.Role.ADMIN,
        )

    def _authed_get(self, url, tokens):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        return self.client.get(url)

    def test_unauthenticated_cannot_reach_protected_endpoints(self):
        for url in (PROF_SUMMARY_URL, ADMIN_SUMMARY_URL):
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_cannot_access_professor_dashboard(self):
        tokens = self._tokens_for(student_payload())
        res = self._authed_get(PROF_SUMMARY_URL, tokens)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_access_admin_dashboard(self):
        tokens = self._tokens_for(student_payload())
        res = self._authed_get(ADMIN_SUMMARY_URL, tokens)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_cannot_access_admin_dashboard(self):
        tokens = self._tokens_for(self._professor_payload())
        res = self._authed_get(ADMIN_SUMMARY_URL, tokens)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_can_access_professor_dashboard(self):
        tokens = self._tokens_for(self._professor_payload())
        res = self._authed_get(PROF_SUMMARY_URL, tokens)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_students"], 0)

    def test_admin_can_access_admin_dashboard(self):
        self._admin_user()
        res = self.client.post(
            LOGIN_URL,
            {"email": "admin1@example.com", "password": ADMIN_PASSWORD},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self._authed_get(ADMIN_SUMMARY_URL, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["admins"], 1)


class PasswordResetTests(APITestCase):
    def test_forgot_password_sends_reset_email(self):
        self.client.post(REGISTER_URL, student_payload(), format="json")
        res = self.client.post(FORGOT_URL, {"email": "riya@example.com"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/reset-password", mail.outbox[0].body)

    def test_forgot_password_does_not_leak_account_existence(self):
        res = self.client.post(FORGOT_URL, {"email": "ghost@example.com"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password_with_valid_token(self):
        self.client.post(REGISTER_URL, student_payload(), format="json")
        user = User.objects.get(email="riya@example.com")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        new_password = "N3wPassword#42"
        res = self.client.post(
            RESET_URL,
            {"uidb64": uid, "token": token, "password": new_password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertFalse(user.check_password(STUDENT_PASSWORD))
        self.assertTrue(user.check_password(new_password))

    def test_reset_password_with_invalid_token(self):
        self.client.post(REGISTER_URL, student_payload(), format="json")
        user = User.objects.get(email="riya@example.com")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        res = self.client.post(
            RESET_URL,
            {"uidb64": uid, "token": "bad-token", "password": "N3wPassword#42"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)