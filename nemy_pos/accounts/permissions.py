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
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner or admin
        return (obj.created_by == request.user or 
                request.user.user_type in ['ADMIN', 'SYSTEM_ADMIN']) 