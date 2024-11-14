from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Customer
from .serializers import UserSerializer, CustomerSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .forms import UserForm, CustomerForm

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations
    Handles CRUD operations for users with proper permissions
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def technicians(self, request):
        """Get list of technicians only"""
        technicians = User.objects.filter(user_type='TECHNICIAN')
        serializer = self.get_serializer(technicians, many=True)
        return Response(serializer.data)

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer operations
    Includes special pricing and credit management
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def credit_status(self, request, pk=None):
        """Get customer's credit status and history"""
        customer = self.get_object()
        # Add credit status logic here
        return Response({
            'credit_limit': customer.credit_limit,
            'credit_allowed': customer.credit_allowed,
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Custom login view
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({
            'error': 'Please provide both username and password'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({
            'error': 'Invalid Credentials'
        }, status=status.HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.pk,
        'user_type': user.user_type
    })

@api_view(['POST'])
def logout(request):
    """
    Logout view
    """
    if request.user.is_authenticated:
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out.'})
    else:
        return Response({'error': 'Not logged in'}, 
                       status=status.HTTP_400_BAD_REQUEST)

def user_list(request):
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'accounts/user_detail.html', {'user': user})

def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'accounts/user_form.html', {'form': form})

def user_update(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'accounts/user_form.html', {'form': form, 'user': user})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'accounts/customer_list.html', {'customers': customers})

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'accounts/customer_detail.html', {'customer': customer})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'accounts/customer_form.html', {'form': form})

def customer_update(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'accounts/customer_form.html', {'form': form, 'customer': customer})
