from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Order
from .serializers import OrderSerializer

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            date_ordered=timezone.now()
        )

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        order = self.get_object()
        if order.is_purchased:
            return Response(
                {"detail": "Cannot borrow a purchased book."},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.is_borrowed = True
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        order = self.get_object()
        if order.is_borrowed:
            return Response(
                {"detail": "Cannot purchase a borrowed book. Please return it first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.is_purchased = True
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        order = self.get_object()
        if not order.is_borrowed:
            return Response(
                {"detail": "This book is not borrowed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.is_borrowed = False
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False)
    def borrowed(self, request):
        borrowed_orders = self.get_queryset().filter(is_borrowed=True)
        serializer = self.get_serializer(borrowed_orders, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def purchased(self, request):
        purchased_orders = self.get_queryset().filter(is_purchased=True)
        serializer = self.get_serializer(purchased_orders, many=True)
        return Response(serializer.data)
