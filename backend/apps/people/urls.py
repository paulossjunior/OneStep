from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonViewSet

# Configure router with Person ViewSet
router = DefaultRouter()
router.register(r'people', PersonViewSet, basename='person')

urlpatterns = [
    path('', include(router.urls)),
]