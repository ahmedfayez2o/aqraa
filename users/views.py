from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import CustomUser
from .serializers import UserSerializer
from books.models import Book
from reviews.models import Review
from orders.models import Order

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_permissions(self):
        if self.action in ['create', 'verify_email']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    def perform_create(self, serializer):
        # Hash password before saving
        password = serializer.validated_data.get('password')
        if password:
            hashed_password = make_password(password)
            serializer.save(password=hashed_password)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password with validation"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to change this password."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(
            user, 
            data={'password': request.data.get('new_password'),
                  'confirm_password': request.data.get('confirm_password'),
                  'current_password': request.data.get('current_password')},
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password updated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_profile(self, request, pk=None):
        """Update user profile information"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to update this profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def reading_history(self, request, pk=None):
        """Get user's reading history including borrowed and purchased books"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to view this history."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        orders = Order.objects.filter(user=user)
        from orders.serializers import OrderSerializer
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def review_history(self, request, pk=None):
        """Get user's review history"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to view these reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reviews = Review.objects.filter(user=user)
        from reviews.serializers import ReviewSerializer
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_preferences(self, request, pk=None):
        """Update user notification preferences"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to update these preferences."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        preferences = request.data.get('notification_preferences', {})
        serializer = self.get_serializer(
            user, 
            data={'notification_preferences': preferences},
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_genres(self, request, pk=None):
        """Update user's favorite genres"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to update these preferences."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        genres = request.data.get('favorite_genres', [])
        serializer = self.get_serializer(
            user,
            data={'favorite_genres': genres},
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """Verify user's email address"""
        # This is a placeholder for email verification logic
        # In a real implementation, this would verify a token sent to the user's email
        email = request.data.get('email')
        token = request.data.get('token')
        
        # Add your email verification logic here
        # For now, just return a placeholder response
        return Response({
            "detail": "Email verification endpoint. Implementation needed."
        })
