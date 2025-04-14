from mongoengine import Document, ReferenceField, DateTimeField, BooleanField
from users.models import CustomUser
from books.models import Book

class Order(Document):
    user = ReferenceField(CustomUser, required=True)
    book = ReferenceField(Book, required=True)
    date_ordered = DateTimeField()
    is_borrowed = BooleanField(default=False)
    is_purchased = BooleanField(default=False)

    meta = {'collection': 'orders'}

    def __str__(self):
        return f"Order for {self.book.title} by {self.user.username}"
