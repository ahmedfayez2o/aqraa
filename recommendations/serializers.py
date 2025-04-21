from rest_framework import serializers
from .models import Recommendation, RecommendationItem, UserActivity
from books.serializers import BookSerializer
from users.serializers import UserSerializer

class UserActivitySerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'book', 'book_details', 'view_count', 
                 'last_viewed', 'is_favorite', 'interaction_score']
        read_only_fields = ['view_count', 'last_viewed', 'interaction_score']

class RecommendationItemSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    
    class Meta:
        model = RecommendationItem
        fields = ['id', 'book', 'book_details', 'relevance_score', 
                 'position', 'reason']

class RecommendationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    items = RecommendationItemSerializer(
        source='recommendationitem_set',
        many=True,
        read_only=True
    )
    source_book_details = BookSerializer(source='source_book', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'user_details', 'items', 
                 'date_generated', 'recommendation_type', 
                 'is_active', 'source_book', 'source_book_details']
        read_only_fields = ['date_generated']

    def create(self, validated_data):
        items_data = self.context.get('items', [])
        recommendation = Recommendation.objects.create(**validated_data)
        
        for idx, item_data in enumerate(items_data):
            RecommendationItem.objects.create(
                recommendation=recommendation,
                position=idx,
                **item_data
            )
            
        return recommendation