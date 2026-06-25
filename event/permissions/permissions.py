# event/permissions.py
from rest_framework import permissions

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow organizers of an event to edit it.
    Assumes the model has an 'organizer' field.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user