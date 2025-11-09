from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet

# Configure router with Group ViewSet
router = DefaultRouter()
router.register(r'organizationalgroups', GroupViewSet, basename='organizationalgroups')

urlpatterns = [
    path('', include(router.urls)),
]
