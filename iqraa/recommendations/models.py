from djongo import models
from books.models import Book
from users.models import CustomUser

class Recommendation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recommended_books = models.ManyToManyField(Book)
    date_recommended = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendations for {self.user.username}"
