from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InitiativeViewSet

# Configure router with Initiative ViewSet
router = DefaultRouter()
router.register(r'initiatives', InitiativeViewSet, basename='initiative')

urlpatterns = [
    path('', include(router.urls)),
]