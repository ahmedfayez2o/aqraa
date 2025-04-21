from django.db import models
from django.conf import settings

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    is_borrowed = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"Order for {self.book.title} by {self.user.username}"

    class Meta:
        db_table = 'orders'
