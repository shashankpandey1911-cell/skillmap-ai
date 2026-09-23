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


class IsVerifiedStudent(permissions.BasePermission):
    """Student who has confirmed their email address.

    Defense-in-depth: unverified users are already blocked at login, but this
    also rejects requests carrying a token minted before the gate existed.
    """

    message = "Please verify your email address to access student features."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_student
            and user.is_email_verified
        )


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
