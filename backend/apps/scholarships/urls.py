"""
URL patterns for the scholarships app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScholarshipTypeViewSet, ScholarshipViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'scholarship-types', ScholarshipTypeViewSet, basename='scholarshiptype')
router.register(r'scholarships', ScholarshipViewSet, basename='scholarship')

urlpatterns = [
    path('', include(router.urls)),
]
