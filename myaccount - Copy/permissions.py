from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model



class UserWatchList(BasePermission):
	def has_object_permission(self, request, view, obj):
		return bool(
				request.user.is_authenticated and
				request.user.is_superuser or
				request.user.is_authenticated and
				request.user.id == obj.user.id
			)

class Is_Authenticated(BasePermission):
	def has_permission(self, request, view):
		return bool(
				request.user.is_authenticated
			)

class IsUser(BasePermission):
	def has_object_permission(self, request, view, User):
		return bool(
				request.user.is_authenticated and
				request.user.is_superuser or
				request.user.is_authenticated and
				request.user.id == User.id
			)

class IsVerified(BasePermission):
    def has_permission(self, request, view):
        return bool(
                request.user.is_authenticated and
                request.user.is_verified
        )
        