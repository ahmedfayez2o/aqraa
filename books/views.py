from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True)
    def books(self, request, pk=None):
        """Get all books in this category"""
        category = self.get_object()
        books = category.books.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn', 'publisher', 'keywords']
    ordering_fields = ['title', 'author', 'price', 'publication_date', 'average_rating']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Optionally restricts the returned books by filtering against
        query parameters in the URL.
        """
        queryset = Book.objects.all()
        
        # Basic filters
        genre = self.request.query_params.get('genre', None)
        category = self.request.query_params.get('category', None)
        language = self.request.query_params.get('language', None)
        
        # Price range filters
        price_min = self.request.query_params.get('price_min', None)
        price_max = self.request.query_params.get('price_max', None)
        
        # Rating filters
        rating_min = self.request.query_params.get('rating_min', None)
        
        # Date filters
        pub_year = self.request.query_params.get('year', None)
        pub_after = self.request.query_params.get('published_after', None)
        pub_before = self.request.query_params.get('published_before', None)

        # Stock availability
        in_stock = self.request.query_params.get('in_stock', None)
        
        # Apply filters
        if genre:
            queryset = queryset.filter(genre=genre)
        if category:
            queryset = queryset.filter(categories__id=category)
        if language:
            queryset = queryset.filter(language=language.upper())
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))
        if rating_min:
            queryset = queryset.filter(average_rating__gte=float(rating_min))
        if pub_year:
            queryset = queryset.filter(publication_date__year=int(pub_year))
        if pub_after:
            queryset = queryset.filter(publication_date__gte=pub_after)
        if pub_before:
            queryset = queryset.filter(publication_date__lte=pub_before)
        if in_stock:
            queryset = queryset.filter(stock__gt=0)
            
        return queryset

    @action(detail=False)
    def genres(self, request):
        """List all unique genres"""
        genres = Book.objects.values_list('genre', flat=True).distinct()
        return Response(sorted(genres))

    @action(detail=False)
    def featured(self, request):
        """Get featured books"""
        featured_books = Book.objects.filter(is_featured=True)
        serializer = self.get_serializer(featured_books, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def search(self, request):
        """Advanced search endpoint"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "Search query is required"}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Split the query into keywords
        keywords = query.split()
        
        # Build complex Q objects for searching multiple fields
        q_objects = Q()
        for keyword in keywords:
            q_objects |= (
                Q(title__icontains=keyword) |
                Q(author__icontains=keyword) |
                Q(summary__icontains=keyword) |
                Q(keywords__contains=[keyword.lower()]) |
                Q(publisher__icontains=keyword)
            )
            
        books = Book.objects.filter(q_objects).distinct()
        
        # Apply additional filters from get_queryset
        books = self.filter_queryset(books)
        
        # Get page from the default pagination class
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def similar(self, request, pk=None):
        """Get similar books based on genre and categories"""
        book = self.get_object()
        similar_books = Book.objects.filter(
            Q(genre=book.genre) |
            Q(categories__in=book.categories.all())
        ).exclude(id=book.id).distinct()[:5]
        
        serializer = self.get_serializer(similar_books, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def latest(self, request):
        """Get latest books"""
        latest_books = Book.objects.order_by('-publication_date')[:10]
        serializer = self.get_serializer(latest_books, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def top_rated(self, request):
        """Get top-rated books"""
        min_ratings = int(request.query_params.get('min_ratings', 3))
        top_books = Book.objects.filter(
            total_ratings__gte=min_ratings
        ).order_by('-average_rating')[:10]
        
        serializer = self.get_serializer(top_books, many=True)
        return Response(serializer.data)
