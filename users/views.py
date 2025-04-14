from django.shortcuts import render
from rest_framework import viewsets
from .models import CustomUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    
    def get_serializer_class(self):
        # TODO: Create and import UserSerializer
        from .serializers import UserSerializer
        return UserSerializer
