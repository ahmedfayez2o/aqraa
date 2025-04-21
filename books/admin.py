from django.contrib import admin
from .models import Book, Category

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'price', 'stock', 'average_rating', 'language', 'is_featured', 'publication_date')
    list_filter = ('genre', 'language', 'is_featured', 'categories', 'publication_date')
    search_fields = ('title', 'author', 'isbn', 'publisher', 'summary')
    filter_horizontal = ('categories',)
    readonly_fields = ('average_rating', 'total_ratings')
    list_editable = ('price', 'stock', 'is_featured')
    list_per_page = 20
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'summary', 'cover_image')
        }),
        ('Categories and Genre', {
            'fields': ('genre', 'categories', 'keywords')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'publisher', 'language', 'page_count', 'edition')
        }),
        ('Stock and Pricing', {
            'fields': ('price', 'stock')
        }),
        ('Ratings and Features', {
            'fields': ('average_rating', 'total_ratings', 'is_featured')
        }),
    )
    ordering = ('title',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name', 'description')
    list_filter = ('parent',)
    ordering = ('name',)
    raw_id_fields = ('parent',)
