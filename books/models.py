from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('AR', 'Arabic'),
        ('FR', 'French'),
        ('ES', 'Spanish'),
        ('DE', 'German')
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, related_name='books')
    isbn = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    summary = models.TextField(blank=True)
    cover_image = models.URLField(blank=True)
    publication_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='EN')
    publisher = models.CharField(max_length=255, blank=True)
    page_count = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    edition = models.CharField(max_length=50, blank=True)
    is_featured = models.BooleanField(default=False)
    keywords = models.JSONField(default=list, blank=True)
    average_rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_ratings = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'books'
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['isbn']),
            models.Index(fields=['genre']),
            models.Index(fields=['language']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.title

    def update_rating(self, new_rating):
        """Update book's average rating when a new review is added"""
        if self.total_ratings == 0:
            self.average_rating = float(new_rating)
        else:
            total = self.average_rating * self.total_ratings
            self.average_rating = (total + float(new_rating)) / (self.total_ratings + 1)
        self.total_ratings += 1
        self.save()
