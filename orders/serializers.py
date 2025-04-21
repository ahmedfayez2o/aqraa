from rest_framework import serializers
from .models import Order
from books.serializers import BookSerializer
from users.serializers import UserSerializer
from django.utils import timezone

class OrderSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_details', 'book', 'book_details', 
                 'date_ordered', 'status', 'status_display', 'is_borrowed', 
                 'is_purchased', 'borrow_date', 'return_due_date', 
                 'return_date', 'purchase_date']
        read_only_fields = ['date_ordered', 'status', 'borrow_date', 
                           'return_date', 'purchase_date']

    def validate(self, data):
        if self.instance:
            # Validation for updates
            if self.instance.is_purchased and data.get('is_borrowed', False):
                raise serializers.ValidationError("Cannot borrow a purchased book")
            if self.instance.status == 'CANCELLED':
                raise serializers.ValidationError("Cannot modify a cancelled order")
        
        return data