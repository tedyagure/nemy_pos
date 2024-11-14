from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'ADMIN'

class IsTechnician(permissions.BasePermission):
    """
    Custom permission for technicians
    """
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'TECHNICIAN'

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.created_by == request.user or 
                request.user.user_type in ['ADMIN', 'SYSTEM_ADMIN']) 