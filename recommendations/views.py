from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import Now
from .models import Recommendation, RecommendationItem, UserActivity, ModelData
from .serializers import (RecommendationSerializer, RecommendationItemSerializer,
                        UserActivitySerializer)
from books.models import Book
from reviews.models import Review
from orders.models import Order
from .ml_model import BookRecommender
import os

class UserActivityViewSet(viewsets.ModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        activity = self.get_object()
        activity.is_favorite = not activity.is_favorite
        activity.save()
        return Response({'status': 'favorite toggled'})

    @action(detail=True, methods=['post'])
    def record_view(self, request, pk=None):
        activity = self.get_object()
        activity.view_count += 1
        activity.last_viewed = timezone.now()
        activity.save()
        return Response({'status': 'view recorded'})

class RecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    _recommender = None

    @property
    def recommender(self):
        if self._recommender is None:
            self._recommender = BookRecommender()
            self._recommender.load_model()  # Now loads from database instead of file
        return self._recommender

    def get_queryset(self):
        return Recommendation.objects.filter(
            user=self.request.user,
            is_active=True
        )

    def create_recommendation(self, books, recommendation_type, source_book=None):
        # Deactivate previous recommendations of the same type
        Recommendation.objects.filter(
            user=self.request.user,
            recommendation_type=recommendation_type,
            is_active=True
        ).update(is_active=False)

        # Create new recommendation
        recommendation = Recommendation.objects.create(
            user=self.request.user,
            recommendation_type=recommendation_type,
            source_book=source_book
        )

        # Create recommendation items
        items = []
        for idx, (book, score, reason) in enumerate(books):
            items.append(RecommendationItem(
                recommendation=recommendation,
                book=book,
                relevance_score=score,
                position=idx,
                reason=reason
            ))
        RecommendationItem.objects.bulk_create(items)

        return recommendation

    def calculate_user_preferences(self):
        """Calculate user preferences based on their activity"""
        user = self.request.user
        
        # Get user activities
        activities = UserActivity.objects.filter(user=user)
        reviews = Review.objects.filter(user=user)
        orders = Order.objects.filter(user=user)
        
        preferences = {}
        
        # Process activities
        for activity in activities:
            genre = activity.book.genre
            score = (activity.view_count * 0.1 +
                    (2 if activity.is_favorite else 0))
            preferences[genre] = preferences.get(genre, 0) + score
            
        # Process reviews
        for review in reviews:
            genre = review.book.genre
            score = review.rating * 0.5
            preferences[genre] = preferences.get(genre, 0) + score
            
        # Process orders
        for order in orders:
            genre = order.book.genre
            score = 3 if order.is_purchased else 2
            preferences[genre] = preferences.get(genre, 0) + score
            
        return preferences

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate personalized recommendations"""
        preferences = self.calculate_user_preferences()
        
        # Get user's recent activity
        last_activity = UserActivity.objects.filter(
            user=request.user
        ).order_by('-last_viewed').first()
        
        if last_activity:
            # Generate recommendations based on last viewed book
            recommended_ids = self.recommender.get_recommendations(
                str(last_activity.book.id),
                user_id=request.user.id  # Add user_id for collaborative filtering
            )
            recommended_books = []
            
            for book_id in recommended_ids:
                book = Book.objects.get(id=book_id)
                score = preferences.get(book.genre, 0)
                reason = f"Because you viewed {last_activity.book.title}"
                recommended_books.append((book, score, reason))
                
            # Sort by user preferences
            recommended_books.sort(key=lambda x: x[1], reverse=True)
            
            recommendation = self.create_recommendation(
                recommended_books,
                'PERSONALIZED',
                last_activity.book
            )
        else:
            # If no activity, use genre-based recommendations
            top_genres = sorted(
                preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            recommended_books = []
            for genre, score in top_genres:
                books = Book.objects.filter(genre=genre)[:3]
                for book in books:
                    reason = f"Based on your interest in {genre} books"
                    recommended_books.append((book, score, reason))
                    
            recommendation = self.create_recommendation(
                recommended_books,
                'GENRE'
            )
            
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

    @action(detail=False)
    def trending(self, request):
        """Get trending books based on recent activity"""
        # Calculate trending score based on recent views and ratings
        trending_period = timezone.now() - timezone.timedelta(days=30)
        
        trending_books = Book.objects.annotate(
            recent_views=Count(
                'useractivity',
                filter=F('useractivity__last_viewed__gte=trending_period')
            ),
            recent_ratings=Count(
                'review',
                filter=F('review__date_reviewed__gte=trending_period')
            ),
            avg_rating=Avg('review__rating'),
            trending_score=ExpressionWrapper(
                F('recent_views') * 0.4 +
                F('recent_ratings') * 0.3 +
                (F('avg_rating') or 0) * 0.3,
                output_field=fields.FloatField()
            )
        ).order_by('-trending_score')[:10]
        
        recommended_books = [
            (book, book.trending_score, "Trending in the last 30 days")
            for book in trending_books
        ]
        
        recommendation = self.create_recommendation(
            recommended_books,
            'TRENDING'
        )
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

    @action(detail=False)
    def similar_to_favorites(self, request):
        """Get recommendations based on user's favorite books"""
        favorites = UserActivity.objects.filter(
            user=request.user,
            is_favorite=True
        )
        
        if not favorites:
            return Response(
                {"detail": "No favorite books found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        recommended_books = []
        seen_books = set()
        
        for favorite in favorites[:3]:
            similar_ids = self.recommender.get_recommendations(
                str(favorite.book.id),
                num_recommendations=3,
                user_id=request.user.id  # Add user_id for collaborative filtering
            )
            
            for book_id in similar_ids:
                book = Book.objects.get(id=book_id)
                if book.id not in seen_books:
                    seen_books.add(book.id)
                    score = 1.0 - (len(recommended_books) * 0.1)
                    reason = f"Similar to your favorite: {favorite.book.title}"
                    recommended_books.append((book, score, reason))
                
        recommendation = self.create_recommendation(
            recommended_books,
            'SIMILAR',
            favorites.first().book
        )
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

    @action(detail=False)
    def refresh_model(self, request):
        """Retrain and update the recommendation model"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can refresh the model"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            self.recommender.train_model()
            return Response({
                "detail": "Model refreshed successfully",
                "model_info": {
                    "latest_version": ModelData.objects.filter(
                        name=BookRecommender.MODEL_NAME
                    ).count()
                }
            })
        except Exception as e:
            return Response(
                {"detail": f"Error refreshing model: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False)
    def refresh_all(self, request):
        """Refresh all recommendation types for the user"""
        # Generate personalized recommendations
        self.generate(request)
        
        # Generate trending recommendations
        self.trending(request)
        
        # Generate similar-to-favorites recommendations
        self.similar_to_favorites(request)
        
        # Return all active recommendations
        recommendations = self.get_queryset()
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
