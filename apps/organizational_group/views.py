from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Prefetch, Count, Q
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.core.pagination import StandardResultsSetPagination
from .models import OrganizationalGroup, OrganizationalGroupLeadership
from .serializers import (
    OrganizationalGroupSerializer,
    OrganizationalGroupDetailSerializer,
    OrganizationalGroupCreateUpdateSerializer,
    OrganizationalGroupLeadershipSerializer
)


class OrganizationalGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing OrganizationalGroup entities through REST API.
    
    Provides CRUD operations for OrganizationalGroup management with proper
    authentication, filtering, searching, and pagination.
    
    Endpoints:
        GET /api/organizationalgroups/ - List all groups with pagination and filtering
        POST /api/organizationalgroups/ - Create new group
        GET /api/organizationalgroups/{id}/ - Retrieve group details
        PUT /api/organizationalgroups/{id}/ - Update group (full update)
        PATCH /api/organizationalgroups/{id}/ - Partial update group
        DELETE /api/organizationalgroups/{id}/ - Delete group
        GET /api/organizationalgroups/{id}/current_leaders/ - Get current leaders
        POST /api/organizationalgroups/{id}/add_leader/ - Add a leader
        POST /api/organizationalgroups/{id}/remove_leader/ - Remove a leader
        GET /api/organizationalgroups/{id}/leadership_history/ - Get leadership history
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'campus', 'knowledge_area']
    search_fields = ['name', 'short_name']
    ordering_fields = ['name', 'short_name', 'type', 'campus', 'created_at', 'updated_at']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        Get optimized queryset with prefetched related data.
        
        Uses select_related and prefetch_related for performance optimization
        to minimize database queries.
        
        Returns:
            QuerySet: Optimized OrganizationalGroup queryset
        """
        queryset = OrganizationalGroup.objects.select_related().prefetch_related(
            'members',
            'initiatives',
            Prefetch(
                'organizationalgroupleadership_set',
                queryset=OrganizationalGroupLeadership.objects.filter(is_active=True).select_related('person'),
                to_attr='current_leaders_list'
            )
        )
        
        # Add annotations for counts to improve performance
        queryset = queryset.annotate(
            annotated_leader_count=Count('leaders', distinct=True, filter=models.Q(organizationalgroupleadership__is_active=True)),
            annotated_member_count=Count('members', distinct=True),
            annotated_initiative_count=Count('initiatives', distinct=True)
        )
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer class: Different serializers for different actions
        """
        if self.action == 'retrieve':
            return OrganizationalGroupDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OrganizationalGroupCreateUpdateSerializer
        return OrganizationalGroupSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new group with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Created group data or validation errors
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'CREATION_FAILED',
                        'message': 'Failed to create group',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update group with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Updated group data or validation errors
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'UPDATE_FAILED',
                        'message': 'Failed to update group',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete group with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Success response or error details
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'DELETION_FAILED',
                        'message': 'Failed to delete group',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def current_leaders(self, request, pk=None):
        """
        Get current leaders for this group.
        
        Returns a list of current active leaders with their leadership details
        including person information, start date, and leadership status.
        
        Args:
            request: HTTP request object
            pk: Group primary key
            
        Returns:
            Response: List of current leaders with details
        """
        group = self.get_object()
        
        # Get active leadership relationships
        active_leaderships = OrganizationalGroupLeadership.objects.filter(
            group=group,
            is_active=True
        ).select_related('person').order_by('-start_date')
        
        serializer = OrganizationalGroupLeadershipSerializer(
            active_leaderships,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'group_id': group.id,
            'group_name': group.name,
            'current_leaders': serializer.data,
            'leader_count': active_leaderships.count()
        })
    
    @action(detail=True, methods=['post'])
    def add_leader(self, request, pk=None):
        """
        Add a leader to this group.
        
        Expects a request body with:
        - person_id (required): ID of the person to add as leader
        - start_date (optional): Leadership start date (defaults to today)
        
        Args:
            request: HTTP request object
            pk: Group primary key
            
        Returns:
            Response: Success response or error details
        """
        group = self.get_object()
        person_id = request.data.get('person_id')
        start_date = request.data.get('start_date')
        
        if not person_id:
            return Response(
                {
                    'error': {
                        'code': 'MISSING_PERSON_ID',
                        'message': 'person_id is required'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.people.models import Person
            from datetime import datetime
            
            person = Person.objects.get(id=person_id)
            
            # Parse start_date if provided
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Add leader using model method
            leadership = group.add_leader(person, start_date=start_date)
            
            # Serialize the created leadership
            serializer = OrganizationalGroupLeadershipSerializer(
                leadership,
                context={'request': request}
            )
            
            return Response({
                'message': f'{person.name} added as leader',
                'leadership': serializer.data,
                'leader_count': group.leader_count()
            }, status=status.HTTP_201_CREATED)
            
        except Person.DoesNotExist:
            return Response(
                {
                    'error': {
                        'code': 'PERSON_NOT_FOUND',
                        'message': 'Person not found'
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'ADD_LEADER_FAILED',
                        'message': 'Failed to add leader',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def remove_leader(self, request, pk=None):
        """
        Remove a leader from this group.
        
        Expects a request body with:
        - person_id (required): ID of the person to remove as leader
        - end_date (optional): Leadership end date (defaults to today)
        
        Args:
            request: HTTP request object
            pk: Group primary key
            
        Returns:
            Response: Success response or error details
        """
        group = self.get_object()
        person_id = request.data.get('person_id')
        end_date = request.data.get('end_date')
        
        if not person_id:
            return Response(
                {
                    'error': {
                        'code': 'MISSING_PERSON_ID',
                        'message': 'person_id is required'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.people.models import Person
            from datetime import datetime
            
            person = Person.objects.get(id=person_id)
            
            # Parse end_date if provided
            if end_date:
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Remove leader using model method
            group.remove_leader(person, end_date=end_date)
            
            return Response({
                'message': f'{person.name} removed as leader',
                'leader_count': group.leader_count()
            })
            
        except Person.DoesNotExist:
            return Response(
                {
                    'error': {
                        'code': 'PERSON_NOT_FOUND',
                        'message': 'Person not found'
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'REMOVE_LEADER_FAILED',
                        'message': 'Failed to remove leader',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def leadership_history(self, request, pk=None):
        """
        Get complete leadership history for this group.
        
        Returns all leadership relationships (current and historical) ordered
        by start date, including person details and leadership period information.
        
        Args:
            request: HTTP request object
            pk: Group primary key
            
        Returns:
            Response: Complete leadership history
        """
        group = self.get_object()
        
        # Get all leadership relationships ordered by start_date
        all_leaderships = OrganizationalGroupLeadership.objects.filter(
            group=group
        ).select_related('person').order_by('-start_date')
        
        serializer = OrganizationalGroupLeadershipSerializer(
            all_leaderships,
            many=True,
            context={'request': request}
        )
        
        # Separate current and historical leaders
        current = [l for l in serializer.data if l['is_active']]
        historical = [l for l in serializer.data if not l['is_active']]
        
        return Response({
            'group_id': group.id,
            'group_name': group.name,
            'current_leaders': current,
            'historical_leaders': historical,
            'total_current': len(current),
            'total_historical': len(historical),
            'total_all_time': all_leaderships.count()
        })
