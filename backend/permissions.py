from rest_framework import permissions

# See: http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/#object-level-permissions


class AdminPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.whatever()
