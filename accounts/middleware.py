from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.conf import settings
import logging
from .models import User

logger = logging.getLogger(__name__)

class RoleBasedAccessMiddleware:
    """
    Middleware to handle role-based access control and security
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Cache the public URLs at startup
        self.public_urls = getattr(settings, 'PUBLIC_URLS', [
            'login', 'logout', 'password_reset', 'password_reset_done',
            'password_reset_confirm', 'password_reset_complete'
        ])

    def __call__(self, request):
        try:
            if not self._is_public_url(request):
                self._handle_authentication(request)
                self._handle_authorization(request)
                self._handle_password_policy(request)
                self._log_access(request)

            response = self.get_response(request)
            return response

        except Exception as e:
            logger.error(f'Middleware error: {str(e)}')
            messages.error(request, 'An unexpected error occurred.')
            return redirect('accounts:login')

    def _is_public_url(self, request):
        """Check if the current URL is public"""
        current_url = resolve(request.path_info).url_name
        return current_url in self.public_urls

    def _handle_authentication(self, request):
        """Handle authentication checks"""
        if not request.user.is_authenticated:
            logger.warning(f'Unauthenticated access attempt to {request.path}')
            messages.warning(request, 'Please log in to access this page.')
            raise PermissionDenied

    def _handle_authorization(self, request):
        """Handle role-based authorization"""
        if not request.user.is_authenticated:
            return

        current_url = resolve(request.path_info).url_name
        allowed_urls = self._get_allowed_urls(request.user)

        if current_url not in allowed_urls:
            logger.warning(
                f'Unauthorized access attempt by {request.user.username} to {request.path}'
            )
            raise PermissionDenied

    def _handle_password_policy(self, request):
        """Handle password policy enforcement"""
        if not request.user.is_authenticated:
            return

        password_urls = ['password_change', 'logout']
        current_url = resolve(request.path_info).url_name

        if request.user.must_change_password and current_url not in password_urls:
            messages.warning(request, 'Please change your password to continue.')
            return redirect('accounts:password_change')

    def _get_allowed_urls(self, user):
        """Get allowed URLs based on user type and role"""
        base_urls = {
            User.UserType.ADMIN: {
                'dashboard', 'profile', 'password_change',
                'users_list', 'user_create', 'user_edit', 'user_delete',
                'roles_list', 'role_create', 'role_edit', 'role_delete',
                'settings', 'audit_logs'
            },
            User.UserType.MANAGER: {
                'dashboard', 'profile', 'password_change',
                'inventory_list', 'inventory_create', 'inventory_edit',
                'sales_list', 'sales_create', 'sales_report',
                'customer_list', 'customer_create', 'customer_edit'
            },
            User.UserType.CASHIER: {
                'profile', 'password_change',
                'pos', 'sales_create', 'sales_list',
                'customer_list', 'customer_create'
            },
            User.UserType.STOCK_CLERK: {
                'profile', 'password_change',
                'inventory_list', 'inventory_edit',
                'stock_adjustment', 'stock_count'
            }
        }

        # Get base URLs for user type
        allowed_urls = base_urls.get(user.user_type, set())

        # Add role-specific URLs
        if user.role:
            role_permissions = user.role.permissions.values_list('codename', flat=True)
            allowed_urls.update(self._get_urls_from_permissions(role_permissions))

        return allowed_urls

    def _get_urls_from_permissions(self, permissions):
        """Convert permissions to their corresponding URLs"""
        permission_url_mapping = {
            'can_view_dashboard': ['dashboard', 'dashboard_charts'],
            'can_manage_inventory': [
                'inventory_list', 'inventory_create', 'inventory_edit',
                'inventory_delete', 'category_list', 'category_create'
            ],
            'can_manage_sales': [
                'pos', 'sales_list', 'sales_create', 'sales_void',
                'sales_report', 'receipt_view', 'receipt_print'
            ],
            # Add more mappings as needed
        }

        urls = set()
        for perm in permissions:
            urls.update(permission_url_mapping.get(perm, []))
        return urls

    def _log_access(self, request):
        """Log access attempts for audit purposes"""
        if request.user.is_authenticated:
            logger.info(
                f'Access: {request.user.username} accessed {request.path} '
                f'from {request.META.get("REMOTE_ADDR")}'
            ) 