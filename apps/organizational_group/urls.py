from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, CampusViewSet

# Configure router with Group and Campus ViewSets
router = DefaultRouter()
router.register(r'organizationalgroups', GroupViewSet, basename='organizationalgroups')
router.register(r'campuses', CampusViewSet, basename='campus')

urlpatterns = [
    path('', include(router.urls)),
]
