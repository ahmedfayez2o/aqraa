from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Recommendation
from .serializers import RecommendationSerializer
from books.models import Book
from reviews.models import Review
from mongoengine.aggregation import Avg
from .ml_model import BookRecommender
import os

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    _recommender = None

    @property
    def recommender(self):
        if self._recommender is None:
            self._recommender = BookRecommender()
            model_path = 'recommendations/ml_models/book_recommender.pkl'
            if os.path.exists(model_path):
                self._recommender.load_model(model_path)
            else:
                # Create ml_models directory if it doesn't exist
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                self._recommender.train_model()
                self._recommender.save_model(model_path)
        return self._recommender

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        # Get user's previous reviews
        user_reviews = Review.objects.filter(user=request.user)
        
        if not user_reviews:
            # If no reviews, return top-rated books
            return self.top_rated_books(request)
        
        # Get the most recently reviewed book
        latest_review = user_reviews.order_by('-date_reviewed').first()
        
        # Get recommendations based on the last reviewed book
        recommended_ids = self.recommender.get_recommendations(str(latest_review.book.id))
        recommended_books = [Book.objects.get(id=book_id) for book_id in recommended_ids]
        
        # Create or update recommendation
        recommendation = Recommendation.objects.get_or_create(user=request.user)[0]
        recommendation.recommended_books = recommended_books
        recommendation.date_recommended = timezone.now()
        recommendation.save()
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def retrain_model(self, request):
        """Endpoint to retrain the recommendation model"""
        try:
            self._recommender = BookRecommender()
            self._recommender.train_model()
            self._recommender.save_model()
            return Response({"message": "Model retrained successfully"})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def top_rated_books(self, request):
        # Get all reviews and calculate average rating for each book
        pipeline = [
            {"$group": {
                "_id": "$book",
                "avg_rating": {"$avg": "$rating"},
                "review_count": {"$sum": 1}
            }},
            {"$match": {
                "review_count": {"$gte": 3}  # Minimum 3 reviews required
            }},
            {"$sort": {"avg_rating": -1}},
            {"$limit": 10}
        ]
        
        # Execute aggregation pipeline
        top_books_data = Review.objects.aggregate(pipeline)
        
        # Get the book objects
        top_books = []
        from books.serializers import BookSerializer
        
        for book_data in top_books_data:
            book = Book.objects.get(id=book_data['_id'])
            book_dict = BookSerializer(book).data
            book_dict['average_rating'] = round(book_data['avg_rating'], 2)
            book_dict['review_count'] = book_data['review_count']
            top_books.append(book_dict)
        
        return Response(top_books)
