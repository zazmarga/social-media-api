from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUserAllOwnIsAuthenticatedReadOnly(BasePermission):
    """
    The request is authenticated own profile, posts etc. is a read/write request, or
    the request is authenticated all others user is a read-only request.
    """

    def has_permission(self, request, view):
        # Разрешить доступ только аутентифицированным пользователям
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешить чтение для всех аутентифицированных пользователей
        if request.method in SAFE_METHODS:
            return True
        # Разрешить запись только для владельца объекта
        return obj.user == request.user
