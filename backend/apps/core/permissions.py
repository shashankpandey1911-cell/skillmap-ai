"""Role-based permission classes shared across all apps.

Combine with object-level ownership checks inside views, e.g.:

    class IsOwner(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return obj.user == request.user
"""

from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_student)


class IsProfessor(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_professor)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_user)


class IsProfessorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_professor or request.user.is_admin_user)
        )