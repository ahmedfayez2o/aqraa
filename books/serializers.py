from rest_framework import serializers
from .models import Book, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent']

class BookSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Book
        fields = '__all__'