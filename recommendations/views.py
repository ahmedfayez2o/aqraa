from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Recommendation
from .serializers import RecommendationSerializer
from books.models import Book
from reviews.models import Review

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        # Get user's previous reviews
        user_reviews = Review.objects.filter(user=request.user)
        liked_genres = set()
        
        # Collect genres from highly rated books
        for review in user_reviews:
            if review.rating >= 4:
                liked_genres.add(review.book.genre)
        
        # Find books in similar genres that user hasn't reviewed
        reviewed_books = {review.book for review in user_reviews}
        recommended_books = Book.objects.filter(genre__in=liked_genres).exclude(id__in=[book.id for book in reviewed_books])[:5]
        
        # Create or update recommendation
        recommendation = Recommendation.objects.get_or_create(user=request.user)[0]
        recommendation.recommended_books = list(recommended_books)
        recommendation.date_recommended = timezone.now()
        recommendation.save()
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)
