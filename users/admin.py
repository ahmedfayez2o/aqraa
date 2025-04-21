from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_verified', 'last_active')
    list_filter = ('is_staff', 'is_verified', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('profile_picture', 'bio', 'phone_number', 'birth_date')}),
        ('Preferences', {'fields': ('favorite_genres', 'notification_preferences')}),
        ('Status', {'fields': ('is_verified', 'last_active')}),
    )
