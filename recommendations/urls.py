from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet, UserActivityViewSet

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'user-activities', UserActivityViewSet, basename='user-activity')

urlpatterns = [
    path('', include(router.urls)),
]