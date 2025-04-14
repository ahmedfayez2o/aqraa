from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Review
from .serializers import ReviewSerializer

# Create your views here.

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        
        # Filter by book
        book_id = self.request.query_params.get('book', None)
        if book_id:
            queryset = queryset.filter(book=book_id)
            
        # Filter by user
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user=user_id)
            
        # Filter by rating
        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(rating=rating)
            
        # Order by date
        return queryset.order_by('-date_reviewed')

    def perform_create(self, serializer):
        # Check if user has already reviewed this book
        existing_review = Review.objects.filter(
            user=self.request.user,
            book=serializer.validated_data['book']
        ).first()
        
        if existing_review:
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this book."}
            )
            
        serializer.save(
            user=self.request.user,
            date_reviewed=timezone.now()
        )

    def perform_update(self, serializer):
        # Only allow updating rating and comment
        serializer.save(date_reviewed=timezone.now())

    @action(detail=False)
    def my_reviews(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def recent(self, request):
        reviews = Review.objects.all().order_by('-date_reviewed')[:10]
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def top_rated(self, request):
        reviews = Review.objects.filter(rating=5)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
