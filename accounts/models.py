from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Role(models.Model):
    """
    Custom role model for fine-grained permissions
    """
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )
    default_route = models.CharField(max_length=100, help_text=_('Default URL route for this role'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    Custom user model with enhanced features
    """
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        MANAGER = 'MANAGER', _('Manager')
        CASHIER = 'CASHIER', _('Cashier')
        STOCK_CLERK = 'STOCK_CLERK', _('Stock Clerk')

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        related_name='users'
    )
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CASHIER
    )
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    must_change_password = models.BooleanField(default=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = [
            ('can_view_dashboard', 'Can view dashboard'),
            ('can_manage_inventory', 'Can manage inventory'),
            ('can_manage_sales', 'Can manage sales'),
            ('can_manage_users', 'Can manage users'),
            ('can_view_reports', 'Can view reports'),
        ]

    def clean(self):
        super().clean()
        if self.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            raise ValidationError(_('Account locked due to too many failed login attempts'))

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        
        if creating:
            self.assign_role_permissions()
            logger.info(f'User created: {self.username} with role {self.role}')

    def assign_role_permissions(self):
        """
        Assigns permissions based on user type and role
        """
        try:
            if self.role:
                self.user_permissions.set(self.role.permissions.all())
            
            # Assign default permissions based on user type
            default_permissions = self.get_default_permissions()
            self.user_permissions.add(*default_permissions)
            
            logger.info(f'Permissions assigned for user: {self.username}')
        except Exception as e:
            logger.error(f'Error assigning permissions to user {self.username}: {str(e)}')
            raise

    def get_default_permissions(self):
        """
        Returns default permissions based on user type
        """
        permission_mapping = {
            self.UserType.ADMIN: Permission.objects.all(),
            self.UserType.MANAGER: Permission.objects.filter(
                codename__in=['can_view_dashboard', 'can_manage_inventory', 
                             'can_manage_sales', 'can_view_reports']
            ),
            self.UserType.CASHIER: Permission.objects.filter(
                codename__in=['can_manage_sales']
            ),
            self.UserType.STOCK_CLERK: Permission.objects.filter(
                codename__in=['can_manage_inventory']
            ),
        }
        return permission_mapping.get(self.user_type, Permission.objects.none())

    def get_default_route(self):
        """
        Returns the default route for the user based on their role
        """
        if self.role:
            return self.role.default_route
            
        route_mapping = {
            self.UserType.ADMIN: 'accounts:dashboard',
            self.UserType.MANAGER: 'accounts:dashboard',
            self.UserType.CASHIER: 'sales:pos',
            self.UserType.STOCK_CLERK: 'inventory:list',
        }
        return route_mapping.get(self.user_type, 'accounts:login')

    def lock_account(self):
        """
        Locks the user account
        """
        self.is_active = False
        self.save(update_fields=['is_active'])
        logger.warning(f'Account locked for user: {self.username}')

    def reset_failed_login_attempts(self):
        """
        Resets the failed login attempts counter
        """
        if self.failed_login_attempts > 0:
            self.failed_login_attempts = 0
            self.save(update_fields=['failed_login_attempts']) 