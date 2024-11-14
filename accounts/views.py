from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Q
from .models import User, Role
from .decorators import role_required, permission_required, audit_log
from .forms import (
    LoginForm, UserCreationForm, UserChangeForm, 
    RoleForm, PasswordChangeForm
)
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    """Handle user login with security measures"""
    if request.user.is_authenticated:
        return redirect(request.user.get_default_route())

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = form.get_user()
                if user is not None:
                    login(request, user)
                    logger.info(f'User logged in: {user.username}')
                    
                    # Update last login info
                    user.last_login = timezone.now()
                    user.last_login_ip = request.META.get('REMOTE_ADDR')
                    user.save(update_fields=['last_login', 'last_login_ip'])
                    
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect(user.get_default_route())
                else:
                    messages.error(request, 'Invalid username or password.')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """Handle user logout"""
    username = request.user.username
    logout(request)
    logger.info(f'User logged out: {username}')
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
@role_required(['ADMIN', 'MANAGER'])
@audit_log('accessed_dashboard')
def dashboard(request):
    """Main dashboard view with role-specific data"""
    context = {
        'total_sales': get_dashboard_stats('sales', request.user),
        'total_inventory': get_dashboard_stats('inventory', request.user),
        'recent_activities': get_recent_activities(request.user),
        'alerts': get_user_alerts(request.user),
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
@role_required(['ADMIN'])
@audit_log('user_management')
def user_list(request):
    """List all users with filtering and search"""
    users = User.objects.select_related('role').all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Handle filters
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role__name=role_filter)

    context = {
        'users': users,
        'roles': Role.objects.all(),
        'search_query': search_query,
        'role_filter': role_filter,
    }
    return render(request, 'accounts/user_list.html', context)

@login_required
@role_required(['ADMIN'])
@audit_log('user_creation')
@transaction.atomic
def user_create(request):
    """Create new user with role assignment"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.must_change_password = True
                user.save()
                
                logger.info(f'New user created: {user.username} by {request.user.username}')
                messages.success(request, 'User created successfully.')
                return redirect('accounts:user_list')
            except Exception as e:
                logger.error(f'Error creating user: {str(e)}')
                messages.error(request, 'Error creating user. Please try again.')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Create'})

@login_required
@role_required(['ADMIN'])
@audit_log('user_edit')
@transaction.atomic
def user_edit(request, pk):
    """Edit existing user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f'User updated: {user.username} by {request.user.username}')
                messages.success(request, 'User updated successfully.')
                return redirect('accounts:user_list')
            except Exception as e:
                logger.error(f'Error updating user: {str(e)}')
                messages.error(request, 'Error updating user. Please try again.')
    else:
        form = UserChangeForm(instance=user)

    return render(request, 'accounts/user_form.html', {
        'form': form, 
        'action': 'Edit',
        'user': user
    })

@login_required
@permission_required('accounts.change_password')
@audit_log('password_change')
def change_password(request):
    """Handle password changes with security policies"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.must_change_password = False
                user.password_changed_at = timezone.now()
                user.save(update_fields=['must_change_password', 'password_changed_at'])
                
                # Update session to prevent logout
                update_session_auth_hash(request, user)
                
                logger.info(f'Password changed for user: {user.username}')
                messages.success(request, 'Your password was changed successfully.')
                return redirect(user.get_default_route())
            except Exception as e:
                logger.error(f'Error changing password: {str(e)}')
                messages.error(request, 'Error changing password. Please try again.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})

# Helper functions
def get_dashboard_stats(stat_type, user):
    """Get role-specific dashboard statistics"""
    # Implementation depends on your specific needs
    pass

def get_recent_activities(user):
    """Get recent system activities relevant to the user's role"""
    # Implementation depends on your specific needs
    pass

def get_user_alerts(user):
    """Get role-specific alerts and notifications"""
    # Implementation depends on your specific needs
    pass 