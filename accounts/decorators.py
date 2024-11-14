from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def role_required(allowed_roles, require_all=False):
    """
    Decorator to check if user has required roles
    
    Args:
        allowed_roles (list): List of required roles
        require_all (bool): If True, user must have all roles. If False, any role is sufficient
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('accounts:login')

            user_roles = {request.user.user_type}
            if request.user.role:
                user_roles.add(request.user.role.name)

            if require_all:
                has_permission = all(role in user_roles for role in allowed_roles)
            else:
                has_permission = any(role in user_roles for role in allowed_roles)

            if not has_permission:
                logger.warning(
                    f'Access denied: {request.user.username} attempted to access '
                    f'{request.path} without required roles'
                )
                raise PermissionDenied('You do not have permission to access this page.')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def permission_required(permissions, require_all=True):
    """
    Decorator to check if user has required permissions
    
    Args:
        permissions (list): List of required permissions
        require_all (bool): If True, user must have all permissions. If False, any permission is sufficient
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('accounts:login')

            if require_all:
                has_permission = all(request.user.has_perm(perm) for perm in permissions)
            else:
                has_permission = any(request.user.has_perm(perm) for perm in permissions)

            if not has_permission:
                logger.warning(
                    f'Permission denied: {request.user.username} attempted to access '
                    f'{request.path} without required permissions'
                )
                raise PermissionDenied('You do not have permission to access this page.')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def audit_log(action_type):
    """
    Decorator to log user actions for audit purposes
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            if request.user.is_authenticated:
                logger.info(
                    f'Audit: {action_type} by {request.user.username} '
                    f'on {request.path} from {request.META.get("REMOTE_ADDR")}'
                )
            
            return response
        return _wrapped_view
    return decorator 