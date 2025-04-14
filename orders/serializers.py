from rest_framework import serializers
from .models import Order
from books.serializers import BookSerializer

class OrderSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'book', 'book_details', 'date_ordered', 'is_borrowed', 'is_purchased']
        read_only_fields = ['date_ordered']