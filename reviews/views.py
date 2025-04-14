from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Review
from django.utils import timezone

# Create your views here.

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    
    def get_serializer_class(self):
        # TODO: Create and import ReviewSerializer
        from .serializers import ReviewSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        # Allow filtering reviews by book
        book_id = self.request.query_params.get('book', None)
        if book_id:
            return Review.objects.filter(book=book_id)
        return Review.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            date_reviewed=timezone.now()
        )
