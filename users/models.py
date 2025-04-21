from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    profile_picture = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username
