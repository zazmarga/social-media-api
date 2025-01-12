from rest_framework.permissions import BasePermission, SAFE_METHODS

from content.models import Profile, Relation


class IsUserAllOwnIsAuthenticatedReadOnly(BasePermission):
    """
    Allow access only to authenticated users
    Allow reading for all authenticated users
    Allow writing access only for the owner
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if isinstance(obj, Profile):
            return obj.user == request.user
        if isinstance(obj, Relation):
            return (
                obj.follower.user == request.user or obj.following.user == request.user
            )
        return False
