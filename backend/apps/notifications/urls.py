"""Notification endpoints.

Routes under /api/v1/:
    GET  notifications                    my notifications (newest first)
    GET  notifications/unread-count       count of unread
    POST notifications/<id>/read          mark one as read
    POST notifications/read-all           mark all as read
"""

from django.urls import path

from . import views

urlpatterns = [
    path("notifications", views.NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/unread-count",
        views.UnreadCountView.as_view(),
        name="notification-unread-count",
    ),
    path(
        "notifications/<int:pk>/read",
        views.MarkReadView.as_view(),
        name="notification-mark-read",
    ),
    path(
        "notifications/read-all",
        views.MarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),
]
