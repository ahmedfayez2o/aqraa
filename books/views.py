from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'genre']
    ordering_fields = ['title', 'author', 'price']

    def get_queryset(self):
        queryset = Book.objects.all()
        genre = self.request.query_params.get('genre', None)
        price_min = self.request.query_params.get('price_min', None)
        price_max = self.request.query_params.get('price_max', None)

        if genre:
            queryset = queryset.filter(genre=genre)
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))
            
        return queryset

    @action(detail=False, methods=['get'])
    def genres(self, request):
        genres = Book.objects.distinct('genre')
        return Response(genres)
