from mongoengine import Document, ReferenceField, IntField, StringField, DateTimeField
from users.models import CustomUser
from books.models import Book

class Review(Document):
    user = ReferenceField(CustomUser, required=True)
    book = ReferenceField(Book, required=True)
    rating = IntField(min_value=1, max_value=5, required=True)
    comment = StringField()
    date_reviewed = DateTimeField()

    meta = {'collection': 'reviews'}

    def __str__(self):
        return f"Review for {self.book.title} by {self.user.username}"
