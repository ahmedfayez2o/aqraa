from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .serializers import UserSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Hash password before saving
        password = serializer.validated_data.get('password')
        if password:
            hashed_password = make_password(password)
            serializer.save(password=hashed_password)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to change this password."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_password = request.data.get('new_password')
        if not new_password:
            return Response(
                {"detail": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.password = make_password(new_password)
        user.save()
        return Response({"detail": "Password updated successfully."})
