from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        # fields = ['id', 'title', 'author', 'description', 'price', 'stock', 'image_url', 'category']
        # extra_kwargs = {              # 'image_url': {'required': False},  # Make image_url optional  