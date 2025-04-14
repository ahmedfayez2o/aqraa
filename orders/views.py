from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order
from rest_framework.decorators import action

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    
    def get_serializer_class(self):
        # TODO: Create and import OrderSerializer
        from .serializers import OrderSerializer
        return OrderSerializer
    
    def get_queryset(self):
        # Filter orders by user if not staff
        user = self.request.user
        if not user.is_staff:
            return Order.objects.filter(user=user)
        return Order.objects.all()

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        order = self.get_object()
        order.is_borrowed = True
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        order = self.get_object()
        order.is_purchased = True
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
