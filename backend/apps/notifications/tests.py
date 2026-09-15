"""Tests for notification endpoints and services."""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Notification
from .services import (
    notify_application_status,
    notify_assessment_result,
    notify_learning_recommendation,
    notify_opportunity_match,
    notify_professor_guidance,
    notify_skill_gap,
)

User = get_user_model()


class NotificationTestBase(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="notifstudent",
            email="notifstudent@test.com",
            password="Student@12345",
            role="STUDENT",
        )
        self.client.force_authenticate(user=self.student)


class NotificationListTests(NotificationTestBase):
    def test_empty_list(self):
        resp = self.client.get("/api/v1/notifications")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_list_with_notifications(self):
        Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Test",
            body="Body",
        )
        resp = self.client.get("/api/v1/notifications")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["title"], "Test")
        self.assertFalse(resp.data[0]["is_read"])

    def test_filter_unread(self):
        Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Unread",
        )
        notif = Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Read",
            read_at=timezone.now(),
        )
        resp = self.client.get("/api/v1/notifications?unread=true")
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["title"], "Unread")

    def test_limit(self):
        for i in range(5):
            Notification.objects.create(
                user=self.student,
                notification_type=Notification.Type.SYSTEM,
                title=f"Notification {i}",
            )
        resp = self.client.get("/api/v1/notifications?limit=2")
        self.assertEqual(len(resp.data), 2)


class UnreadCountTests(NotificationTestBase):
    def test_zero_unread(self):
        resp = self.client.get("/api/v1/notifications/unread-count")
        self.assertEqual(resp.data["unread_count"], 0)

    def test_count_unread(self):
        Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Unread 1",
        )
        Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Unread 2",
        )
        Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Read",
            read_at=timezone.now(),
        )
        resp = self.client.get("/api/v1/notifications/unread-count")
        self.assertEqual(resp.data["unread_count"], 2)


class MarkReadTests(NotificationTestBase):
    def test_mark_one_read(self):
        notif = Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Mark me",
        )
        resp = self.client.post(f"/api/v1/notifications/{notif.id}/read")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertIsNotNone(notif.read_at)

    def test_mark_already_read(self):
        notif = Notification.objects.create(
            user=self.student,
            notification_type=Notification.Type.SYSTEM,
            title="Already read",
            read_at=timezone.now(),
        )
        resp = self.client.post(f"/api/v1/notifications/{notif.id}/read")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_mark_other_user_notification(self):
        other = User.objects.create_user(
            username="other", email="other@test.com", password="Test@12345"
        )
        notif = Notification.objects.create(
            user=other, notification_type=Notification.Type.SYSTEM, title="Other"
        )
        resp = self.client.post(f"/api/v1/notifications/{notif.id}/read")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class MarkAllReadTests(NotificationTestBase):
    def test_mark_all_read(self):
        for i in range(3):
            Notification.objects.create(
                user=self.student,
                notification_type=Notification.Type.SYSTEM,
                title=f"Test {i}",
            )
        resp = self.client.post("/api/v1/notifications/read-all")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["detail"], "Marked 3 notifications as read.")
        self.assertEqual(
            Notification.objects.filter(user=self.student, read_at__isnull=True).count(),
            0,
        )


class ServiceTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="svcstudent",
            email="svc@test.com",
            password="Student@12345",
            role="STUDENT",
        )

    def test_notify_opportunity_match(self):
        from apps.opportunities.models import Opportunity

        opp = Opportunity.objects.create(
            title="Test Job", company="Corp", opportunity_type="JOB"
        )
        notify_opportunity_match(self.student, opp, 85.0)
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.notification_type, Notification.Type.OPPORTUNITY_MATCH)
        self.assertIn("85%", n.body)

    def test_notify_assessment_result(self):
        notify_assessment_result(self.student, "Python Quiz", 90.0)
        n = Notification.objects.first()
        self.assertEqual(n.notification_type, Notification.Type.ASSESSMENT_RESULT)
        self.assertIn("90.0%", n.body)

    def test_notify_skill_gap(self):
        notify_skill_gap(self.student, "DSA", 40.0, "Backend Developer")
        n = Notification.objects.first()
        self.assertEqual(n.notification_type, Notification.Type.SKILL_GAP)
        self.assertIn("40%", n.body)

    def test_notify_professor_guidance(self):
        notify_professor_guidance(self.student, "Dr. Smith", "Review DSA")
        n = Notification.objects.first()
        self.assertEqual(n.notification_type, Notification.Type.PROFESSOR_GUIDANCE)
        self.assertIn("Dr. Smith", n.title)

    def test_notify_learning_recommendation(self):
        notify_learning_recommendation(self.student, "Python Course", "Python")
        n = Notification.objects.first()
        self.assertEqual(n.notification_type, Notification.Type.LEARNING_RECOMMEND)

    def test_deduplication(self):
        from apps.opportunities.models import Opportunity

        opp = Opportunity.objects.create(
            title="Dedup Job", company="Corp", opportunity_type="JOB"
        )
        notify_opportunity_match(self.student, opp, 80.0)
        notify_opportunity_match(self.student, opp, 80.0)
        self.assertEqual(Notification.objects.count(), 1)
