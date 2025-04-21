from django.db import models
from django.conf import settings
import json

class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)
    interaction_score = models.FloatField(default=0)  # Calculated based on user interactions

    class Meta:
        db_table = 'user_activities'
        unique_together = ('user', 'book')
        verbose_name_plural = 'User activities'

    def __str__(self):
        return f"{self.user.username}'s activity on {self.book.title}"

class Recommendation(models.Model):
    RECOMMENDATION_TYPES = [
        ('PERSONALIZED', 'Personalized'),
        ('TRENDING', 'Trending'),
        ('SIMILAR', 'Similar Books'),
        ('GENRE', 'Genre Based'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommended_books = models.ManyToManyField('books.Book', through='RecommendationItem')
    date_generated = models.DateTimeField(auto_now_add=True)
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    is_active = models.BooleanField(default=True)
    source_book = models.ForeignKey(
        'books.Book',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='source_recommendations'
    )

    class Meta:
        db_table = 'recommendations'
        ordering = ['-date_generated']

    def __str__(self):
        return f"Recommendations for {self.user.username}"

class RecommendationItem(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    relevance_score = models.FloatField()  # How relevant this recommendation is
    position = models.IntegerField()  # Position in the recommendation list
    reason = models.TextField(blank=True)  # Why this book was recommended

    class Meta:
        db_table = 'recommendation_items'
        ordering = ['position']
        unique_together = ('recommendation', 'book')

    def __str__(self):
        return f"Item {self.position} in {self.recommendation}"

class ModelData(models.Model):
    """Store ML model data in the database instead of pickle files"""
    name = models.CharField(max_length=100, unique=True)
    version = models.IntegerField(default=1)
    data = models.JSONField()  # Store model data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'model_data'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} v{self.version}"

    @classmethod
    def save_model_data(cls, name, data_dict):
        """Save model data to database"""
        # Convert numpy arrays to lists
        processed_data = {}
        for key, value in data_dict.items():
            if hasattr(value, 'tolist'):
                processed_data[key] = value.tolist()
            elif hasattr(value, 'to_dict'):
                processed_data[key] = value.to_dict()
            else:
                processed_data[key] = value

        # Create new version
        version = 1
        latest = cls.objects.filter(name=name).order_by('-version').first()
        if latest:
            version = latest.version + 1

        return cls.objects.create(
            name=name,
            version=version,
            data=processed_data
        )

    @classmethod
    def get_latest_model_data(cls, name):
        """Get the latest version of model data"""
        return cls.objects.filter(name=name).order_by('-version').first()
