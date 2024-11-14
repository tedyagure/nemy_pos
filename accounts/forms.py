from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm, PasswordChangeForm as BasePasswordChangeForm
)
from django.core.exceptions import ValidationError
from .models import User, Role
import re

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Additional security checks can be added here
            pass

        return cleaned_data

class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'user_type', 'role', 'phone')
        
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            # Custom password validation
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            if not re.search(r'[A-Z]', password):
                raise ValidationError('Password must contain at least one uppercase letter.')
            if not re.search(r'[a-z]', password):
                raise ValidationError('Password must contain at least one lowercase letter.')
            if not re.search(r'[0-9]', password):
                raise ValidationError('Password must contain at least one number.')
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError('Password must contain at least one special character.')
        return password

class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'user_type', 'role', 'phone', 'is_active')

class PasswordChangeForm(BasePasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            # Reuse password validation from UserCreationForm
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            # ... other validation rules
        return password

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'permissions', 'default_route', 'is_active') 