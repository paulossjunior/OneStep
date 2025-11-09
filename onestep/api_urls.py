"""
API URL configuration for OneStep project.

This module provides centralized API routing with versioning support
and automatic documentation generation.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import ViewSets
from apps.people.views import PersonViewSet
from apps.initiatives.views import InitiativeViewSet
from apps.organizational_group.views import OrganizationalGroupViewSet, CampusViewSet


# API Root view
@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint providing information about available endpoints.
    
    Returns:
        Response: API information and available endpoints
    """
    return Response({
        'message': 'Welcome to OneStep API',
        'version': 'v1',
        'endpoints': {
            'people': request.build_absolute_uri('/api/v1/people/'),
            'initiatives': request.build_absolute_uri('/api/v1/initiatives/'),
            'groups': request.build_absolute_uri('/api/v1/groups/'),
            'campuses': request.build_absolute_uri('/api/v1/campuses/'),
            'auth': {
                'token': request.build_absolute_uri('/api/v1/auth/token/'),
                'token_refresh': request.build_absolute_uri('/api/v1/auth/token/refresh/'),
                'token_verify': request.build_absolute_uri('/api/v1/auth/token/verify/'),
            }
        },
        'authentication': 'JWT, Session, or Basic authentication supported',
        'pagination': 'Page-based pagination with 20 items per page',
        'filtering': 'DjangoFilter, Search, and Ordering supported',
        'features': {
            'search': 'Use ?search=query to search across multiple fields',
            'ordering': 'Use ?ordering=field_name to sort results',
            'filtering': 'Use field-specific query parameters for filtering',
            'pagination': 'Use ?page=N and ?page_size=N for pagination control'
        }
    })


# Configure DRF router for automatic URL generation
router = DefaultRouter()
router.register(r'people', PersonViewSet, basename='person')
router.register(r'initiatives', InitiativeViewSet, basename='initiative')
router.register(r'organizationalgroup', OrganizationalGroupViewSet, basename='organizationalgroup')
router.register(r'campuses', CampusViewSet, basename='campus')

# API v1 URL patterns
v1_patterns = [
    # API root
    path('', api_root, name='api-root'),
    
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Router URLs (includes all ViewSet endpoints)
    path('', include(router.urls)),
]

# Main API URL patterns with versioning
urlpatterns = [
    # API v1
    path('v1/', include((v1_patterns, 'api'), namespace='v1')),
    
    # Default to v1 for backward compatibility
    path('', include((v1_patterns, 'api'), namespace='default')),
]