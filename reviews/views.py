from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer
from recommendations.ml_model import SentimentAnalyzer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comment']
    ordering_fields = ['date_reviewed', 'rating']
    _sentiment_analyzer = None

    @property
    def sentiment_analyzer(self):
        if self._sentiment_analyzer is None:
            self._sentiment_analyzer = SentimentAnalyzer()
        return self._sentiment_analyzer

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
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(date_reviewed__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_reviewed__lte=end_date)
            
        # Filter by sentiment
        sentiment = self.request.query_params.get('sentiment', None)
        if sentiment:
            # This is a more expensive operation as we need to analyze each review
            filtered_reviews = []
            for review in queryset:
                sent_score = self.sentiment_analyzer.analyze_sentiment(review.comment)
                if sentiment == 'positive' and sent_score >= 0.05:
                    filtered_reviews.append(review.id)
                elif sentiment == 'negative' and sent_score <= -0.05:
                    filtered_reviews.append(review.id)
                elif sentiment == 'neutral' and -0.05 < sent_score < 0.05:
                    filtered_reviews.append(review.id)
            queryset = queryset.filter(id__in=filtered_reviews)
            
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
        """Get all reviews by the current user"""
        reviews = Review.objects.filter(user=request.user)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def recent(self, request):
        """Get recent reviews with optional limit parameter"""
        limit = int(request.query_params.get('limit', 10))
        reviews = Review.objects.all().order_by('-date_reviewed')[:limit]
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def top_rated(self, request):
        """Get top-rated reviews"""
        min_rating = int(request.query_params.get('min_rating', 4))
        reviews = (Review.objects.filter(rating__gte=min_rating)
                  .order_by('-rating', '-date_reviewed'))
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def sentiment(self, request, pk=None):
        """Get sentiment analysis for a specific review"""
        review = self.get_object()
        if not review.comment:
            return Response({
                "sentiment": 0.0,
                "message": "No comment to analyze",
                "interpretation": "neutral"
            })
            
        sentiment = self.sentiment_analyzer.analyze_sentiment(review.comment)
        return Response({
            "sentiment": sentiment,
            "interpretation": "positive" if sentiment >= 0.05 
                            else "negative" if sentiment <= -0.05 
                            else "neutral",
            "review_id": review.id,
            "book_title": review.book.title
        })

    @action(detail=False, methods=['get'])
    def book_sentiments(self, request):
        """Get sentiment analysis for all reviews of a book"""
        book_id = request.query_params.get('book', None)
        if not book_id:
            return Response(
                {"detail": "Book ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        reviews = Review.objects.filter(book_id=book_id)
        if not reviews:
            return Response({
                "detail": "No reviews found for this book",
                "sentiment_stats": {
                    "average": 0,
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0
                }
            })
            
        sentiments = []
        stats = {"positive": 0, "neutral": 0, "negative": 0}
        
        for review in reviews:
            if review.comment:
                sentiment = self.sentiment_analyzer.analyze_sentiment(review.comment)
                sentiments.append(sentiment)
                if sentiment >= 0.05:
                    stats["positive"] += 1
                elif sentiment <= -0.05:
                    stats["negative"] += 1
                else:
                    stats["neutral"] += 1
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        return Response({
            "book_id": book_id,
            "total_reviews": len(reviews),
            "reviews_with_comments": len(sentiments),
            "average_sentiment": round(avg_sentiment, 2),
            "sentiment_stats": stats,
            "interpretation": "positive" if avg_sentiment >= 0.05 
                            else "negative" if avg_sentiment <= -0.05 
                            else "neutral"
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get review statistics"""
        book_id = request.query_params.get('book', None)
        user_id = request.query_params.get('user', None)
        
        queryset = Review.objects
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        stats = queryset.aggregate(
            total_reviews=models.Count('id'),
            average_rating=models.Avg('rating'),
            rating_1=models.Count('id', filter=models.Q(rating=1)),
            rating_2=models.Count('id', filter=models.Q(rating=2)),
            rating_3=models.Count('id', filter=models.Q(rating=3)),
            rating_4=models.Count('id', filter=models.Q(rating=4)),
            rating_5=models.Count('id', filter=models.Q(rating=5))
        )
        
        return Response({
            "total_reviews": stats['total_reviews'],
            "average_rating": round(stats['average_rating'], 2) if stats['average_rating'] else 0,
            "rating_distribution": {
                "1": stats['rating_1'],
                "2": stats['rating_2'],
                "3": stats['rating_3'],
                "4": stats['rating_4'],
                "5": stats['rating_5']
            }
        })
