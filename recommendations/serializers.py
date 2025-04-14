from rest_framework import serializers
from .models import Recommendation
from books.serializers import BookSerializer
from users.serializers import UserSerializer

class RecommendationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    recommended_books_details = BookSerializer(source='recommended_books', many=True, read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'user_details', 'recommended_books', 'recommended_books_details', 'date_recommended']
        read_only_fields = ['date_recommended']