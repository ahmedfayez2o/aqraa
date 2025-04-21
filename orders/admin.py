from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'status', 'date_ordered', 'is_borrowed', 'is_purchased', 'return_due_date')
    list_filter = ('status', 'is_borrowed', 'is_purchased', 'date_ordered')
    search_fields = ('user__username', 'user__email', 'book__title', 'book__isbn')
    readonly_fields = ('date_ordered',)
    raw_id_fields = ('user', 'book')
    date_hierarchy = 'date_ordered'
    list_per_page = 20
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Purchase Details', {
            'fields': ('is_purchased', 'purchase_date')
        }),
        ('Borrowing Details', {
            'fields': ('is_borrowed', 'borrow_date', 'return_due_date', 'return_date')
        })
    )
