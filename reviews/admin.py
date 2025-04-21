from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'rating', 'date_reviewed')
    list_filter = ('rating', 'date_reviewed')
    search_fields = ('user__username', 'book__title', 'comment')
    raw_id_fields = ('user', 'book')
    readonly_fields = ('date_reviewed',)
    date_hierarchy = 'date_reviewed'
    list_per_page = 20
    
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'book', 'rating')
        }),
        ('Content', {
            'fields': ('comment', 'date_reviewed')
        })
    )
