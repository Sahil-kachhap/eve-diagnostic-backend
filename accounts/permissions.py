from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):
    message = "Admin access is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )