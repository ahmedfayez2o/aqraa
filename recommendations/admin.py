from django.contrib import admin
from .models import UserActivity, Recommendation, RecommendationItem, ModelData

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'view_count', 'last_viewed', 'is_favorite', 'interaction_score')
    list_filter = ('is_favorite',)
    search_fields = ('user__username', 'book__title')

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'date_generated', 'is_active', 'source_book')
    list_filter = ('recommendation_type', 'is_active')
    search_fields = ('user__username',)

@admin.register(RecommendationItem)
class RecommendationItemAdmin(admin.ModelAdmin):
    list_display = ('recommendation', 'book', 'relevance_score', 'position')
    list_filter = ('recommendation__recommendation_type',)
    search_fields = ('recommendation__user__username', 'book__title')
    ordering = ('recommendation', 'position')

@admin.register(ModelData)
class ModelDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
