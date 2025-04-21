from django.db import models
from django.conf import settings

class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommended_books = models.ManyToManyField('books.Book')
    date_recommended = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendations for {self.user.username}"

    class Meta:
        db_table = 'recommendations'
