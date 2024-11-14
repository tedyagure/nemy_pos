from rest_framework import serializers
from .models import User, Customer

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    Handles user registration and profile management
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'credit_limit']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create user with encrypted password
        user = User.objects.create_user(**validated_data)
        return user

class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model
    Handles customer management including their pricing preferences
    """
    class Meta:
        model = Customer
        fields = '__all__' 