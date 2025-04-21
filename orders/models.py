from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('BORROWED', 'Borrowed'),
        ('PURCHASED', 'Purchased'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_borrowed = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)
    borrow_date = models.DateTimeField(null=True, blank=True)
    return_due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    purchase_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order for {self.book.title} by {self.user.username}"

    class Meta:
        db_table = 'orders'
        ordering = ['-date_ordered']
