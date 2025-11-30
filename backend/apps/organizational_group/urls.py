from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KnowledgeAreaViewSet, OrganizationalGroupViewSet, CampusViewSet

# Configure router with KnowledgeArea, OrganizationalGroup and Campus ViewSets
router = DefaultRouter()
router.register(r'knowledge-areas', KnowledgeAreaViewSet, basename='knowledge-area')
router.register(r'organizationalgroups', OrganizationalGroupViewSet, basename='organizationalgroups')
router.register(r'campuses', CampusViewSet, basename='campus')

urlpatterns = [
    path('', include(router.urls)),
]
