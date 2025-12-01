"""
Core application views.

This module contains views for the core application, including
the landing page view that serves as the entry point for the application.
"""

from django.views.generic import TemplateView
from django.conf import settings


class IndexView(TemplateView):
    """
    Landing page view for OneStep application.
    
    Provides information about the application, links to admin
    and API, and displays available endpoints.
    
    Attributes:
        template_name (str): Path to the template file
    
    Methods:
        get_context_data: Provides context data for template rendering
    """
    template_name = 'core/index.html'
    
    def get_context_data(self, **kwargs):
        """
        Prepare context data for the landing page template.
        
        Returns context containing application information, API endpoints,
        authentication methods, and API features.
        
        Args:
            **kwargs: Additional keyword arguments from parent class
            
        Returns:
            dict: Context dictionary with application data
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'app_name': 'OneStep',
            'app_description': 'Organizational Initiative Management System',
            'api_version': 'v1',
            'admin_url': settings.ADMIN_URL,
            'api_endpoints': [
                {
                    'name': 'People',
                    'url': '/api/v1/people/',
                    'description': 'Manage people and team members'
                },
                {
                    'name': 'Initiatives',
                    'url': '/api/v1/initiatives/',
                    'description': 'Manage programs, projects, and events'
                },
            ],
            'auth_methods': ['JWT Token', 'Session Authentication', 'Basic Authentication'],
            'api_features': [
                'Search across multiple fields',
                'Field-based filtering',
                'Ordering and sorting',
                'Page-based pagination'
            ]
        })
        return context


from rest_framework import views, permissions, response
from .serializers import UserSerializer

class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return response.Response(serializer.data)
