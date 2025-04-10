from djongo import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    summary = models.TextField()
    cover_image = models.URLField()

    def __str__(self):
        return self.title
