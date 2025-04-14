from rest_framework import serializers
from .models import Review
from books.serializers import BookSerializer
from users.serializers import UserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_details', 'book', 'book_details', 'rating', 'comment', 'date_reviewed']
        read_only_fields = ['date_reviewed']