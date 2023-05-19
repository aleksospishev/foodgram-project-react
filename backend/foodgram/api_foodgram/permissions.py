from rest_framework import permissions


class AuthorOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class AuthorAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permissions(self, request, obj, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_superuser)


class UserMeOrUserProfile(permissions.BasePermission):
    def has_permission(self, request, view):
        user_me = bool(
            request.user
            and request.user.is_authenticated
            and request.path_info == '/api/users/me/'
        )
        user_profile = bool(
            request.path_info != '/api/users/me/'
        )
        return bool(user_me or user_profile)


class SubscribeUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
