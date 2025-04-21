from django.shortcuts import render
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from .models import Order
from .serializers import OrderSerializer
from books.models import Book

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        if book.stock <= 0:
            raise serializers.ValidationError({"detail": "Book is out of stock"})
        
        serializer.save(
            user=self.request.user,
            date_ordered=timezone.now(),
            status='PENDING'
        )

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'PENDING':
            return Response(
                {"detail": f"Cannot borrow book in {order.status} status"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if order.book.stock <= 0:
            return Response(
                {"detail": "Book is out of stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update book stock
        book = order.book
        book.stock -= 1
        book.save()
        
        # Update order
        order.status = 'BORROWED'
        order.is_borrowed = True
        order.borrow_date = timezone.now()
        order.return_due_date = timezone.now() + timedelta(days=14)  # 2 weeks borrowing period
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        order = self.get_object()
        
        if order.status not in ['PENDING', 'BORROWED']:
            return Response(
                {"detail": f"Cannot purchase book in {order.status} status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status == 'PENDING' and order.book.stock <= 0:
            return Response(
                {"detail": "Book is out of stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update book stock if not already borrowed
        if order.status == 'PENDING':
            book = order.book
            book.stock -= 1
            book.save()

        # Update order
        order.status = 'PURCHASED'
        order.is_purchased = True
        order.purchase_date = timezone.now()
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        order = self.get_object()
        
        if not order.is_borrowed or order.status != 'BORROWED':
            return Response(
                {"detail": "This book is not borrowed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update book stock
        book = order.book
        book.stock += 1
        book.save()
        
        # Update order
        order.status = 'RETURNED'
        order.is_borrowed = False
        order.return_date = timezone.now()
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.status not in ['PENDING']:
            return Response(
                {"detail": f"Cannot cancel order in {order.status} status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'CANCELLED'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False)
    def borrowed(self, request):
        borrowed_orders = self.get_queryset().filter(status='BORROWED')
        serializer = self.get_serializer(borrowed_orders, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def purchased(self, request):
        purchased_orders = self.get_queryset().filter(status='PURCHASED')
        serializer = self.get_serializer(purchased_orders, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def overdue(self, request):
        """List all overdue borrowed books"""
        overdue_orders = self.get_queryset().filter(
            status='BORROWED',
            return_due_date__lt=timezone.now()
        )
        serializer = self.get_serializer(overdue_orders, many=True)
        return Response(serializer.data)
