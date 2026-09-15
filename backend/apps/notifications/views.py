"""Notification views — list, unread count, mark read, mark all read."""

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStudent

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    """GET /notifications — list current user's notifications."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)
        unread_only = request.query_params.get("unread")
        if unread_only in ("true", "1", "True"):
            qs = qs.filter(read_at__isnull=True)
        limit = request.query_params.get("limit")
        if limit:
            try:
                qs = qs[: int(limit)]
            except (ValueError, TypeError):
                pass
        serializer = NotificationSerializer(qs[:50], many=True)
        return Response(serializer.data)


class UnreadCountView(APIView):
    """GET /notifications/unread-count — count of unread notifications."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, read_at__isnull=True
        ).count()
        return Response({"unread_count": count})


class MarkReadView(APIView):
    """POST /notifications/<id>/read — mark one notification as read."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if notif.read_at is None:
            notif.read_at = timezone.now()
            notif.save(update_fields=["read_at"])
        return Response({"detail": "Marked as read."})


class MarkAllReadView(APIView):
    """POST /notifications/read-all — mark all unread notifications as read."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        now = timezone.now()
        updated = Notification.objects.filter(
            user=request.user, read_at__isnull=True
        ).update(read_at=now)
        return Response({"detail": f"Marked {updated} notifications as read."})
