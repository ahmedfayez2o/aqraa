from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    summary = models.TextField(blank=True)
    cover_image = models.URLField(blank=True)

    class Meta:
        db_table = 'books'

    def __str__(self):
        return self.title
