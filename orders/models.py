from djongo import models
from users.models import CustomUser
from books.models import Book

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    is_borrowed = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
