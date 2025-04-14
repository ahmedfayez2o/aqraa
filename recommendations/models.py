from mongoengine import Document, ReferenceField, ListField, DateTimeField
from books.models import Book
from users.models import CustomUser

class Recommendation(Document):
    user = ReferenceField(CustomUser, required=True)
    recommended_books = ListField(ReferenceField(Book))
    date_recommended = DateTimeField()

    meta = {'collection': 'recommendations'}

    def __str__(self):
        return f"Recommendations for {self.user.username}"
