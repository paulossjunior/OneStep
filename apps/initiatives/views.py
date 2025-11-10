from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Count, Prefetch
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from apps.core.filters import PerformantDjangoFilterBackend, OptimizedSearchFilter, EnhancedOrderingFilter
from apps.core.pagination import StandardResultsSetPagination
from .models import Initiative, InitiativeType
from .serializers import (
    InitiativeSerializer, 
    InitiativeDetailSerializer, 
    InitiativeCreateUpdateSerializer,
    InitiativeTypeSerializer
)
from .filters import InitiativeFilter


@extend_schema_view(
    list=extend_schema(
        summary="List all initiatives",
        description="Retrieve a paginated list of all initiatives with comprehensive filtering, searching, and ordering capabilities. "
                    "Supports filtering by type, coordinator, dates, hierarchy level, team members, and status. "
                    "Use the search parameter to search across name, description, and coordinator name.",
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by name (case-insensitive partial match)'
            ),
            OpenApiParameter(
                name='type_code',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by initiative type code',
                enum=['program', 'project', 'event']
            ),
            OpenApiParameter(
                name='coordinator',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by coordinator person ID'
            ),
            OpenApiParameter(
                name='parent',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by parent initiative ID'
            ),
            OpenApiParameter(
                name='is_root',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter root initiatives (no parent)'
            ),
            OpenApiParameter(
                name='has_children',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter initiatives that have child initiatives'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter active initiatives (currently running)'
            ),
            OpenApiParameter(
                name='is_upcoming',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter upcoming initiatives (not yet started)'
            ),
            OpenApiParameter(
                name='is_completed',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter completed initiatives (already ended)'
            ),
            OpenApiParameter(
                name='team_member',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter initiatives where person is a team member'
            ),
            OpenApiParameter(
                name='start_date_after',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter initiatives starting after this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='start_date_before',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter initiatives starting before this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search across name, description, and coordinator name'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order results by field (prefix with - for descending)',
                enum=['name', '-name', 'type', '-type', 'start_date', '-start_date', 'end_date', '-end_date', 'created_at', '-created_at']
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number for pagination'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of results per page'
            ),
        ],
        tags=['initiatives']
    ),
    retrieve=extend_schema(
        summary="Get initiative details",
        description="Retrieve detailed information about a specific initiative including coordinator, team members, parent, and children.",
        tags=['initiatives']
    ),
    create=extend_schema(
        summary="Create new initiative",
        description="Create a new initiative with name, description, type, dates, coordinator, and optional parent. "
                    "Team members can be added after creation using the add_team_member endpoint.",
        tags=['initiatives']
    ),
    update=extend_schema(
        summary="Update initiative (full)",
        description="Perform a full update of an initiative. All fields must be provided.",
        tags=['initiatives']
    ),
    partial_update=extend_schema(
        summary="Update initiative (partial)",
        description="Perform a partial update of an initiative. Only provided fields will be updated.",
        tags=['initiatives']
    ),
    destroy=extend_schema(
        summary="Delete initiative",
        description="Delete an initiative. If the initiative has children, a warning will be returned requiring confirmation. "
                    "Use the force_delete endpoint to confirm deletion of initiative with children.",
        tags=['initiatives']
    ),
)
class InitiativeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Initiative entities through REST API.
    
    Provides CRUD operations for Initiative management with proper
    authentication, filtering, searching, and pagination.
    
    Endpoints:
        GET /api/initiatives/ - List all initiatives with pagination and filtering
        POST /api/initiatives/ - Create new initiative
        GET /api/initiatives/{id}/ - Retrieve initiative details
        PUT /api/initiatives/{id}/ - Update initiative (full update)
        PATCH /api/initiatives/{id}/ - Partial update initiative
        DELETE /api/initiatives/{id}/ - Delete initiative
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [PerformantDjangoFilterBackend, OptimizedSearchFilter, EnhancedOrderingFilter]
    filterset_class = InitiativeFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ['name', 'description', 'coordinator__name']
    ordering_fields = ['name', 'type', 'start_date', 'end_date', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Get optimized queryset with prefetched related data.
        
        Returns:
            QuerySet: Optimized Initiative queryset
        """
        queryset = Initiative.objects.select_related(
            'coordinator',
            'parent',
            'demanding_partner'
        ).prefetch_related(
            'team_members',
            'children'
        )
        
        # Add annotation for counts to improve performance
        queryset = queryset.annotate(
            annotated_team_count=Count('team_members', distinct=True),
            annotated_children_count=Count('children', distinct=True)
        )
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer class: Different serializers for different actions
        """
        if self.action == 'retrieve':
            return InitiativeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InitiativeCreateUpdateSerializer
        return InitiativeSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new initiative with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Created initiative data or validation errors
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
                        'message': 'Failed to create initiative',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update initiative with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Updated initiative data or validation errors
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'UPDATE_FAILED',
                        'message': 'Failed to update initiative',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete initiative with proper error handling and cascade warnings.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Success response or error details
        """
        try:
            instance = self.get_object()
            
            # Check if initiative has children (will be cascade deleted)
            children_count = instance.children.count()
            if children_count > 0:
                # Return warning about cascade deletion
                return Response(
                    {
                        'warning': {
                            'code': 'CASCADE_DELETION',
                            'message': f'This initiative has {children_count} child initiative(s) that will also be deleted.',
                            'children_count': children_count,
                            'confirm_required': True
                        }
                    },
                    status=status.HTTP_200_OK
                )
            
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'DELETION_FAILED',
                        'message': 'Failed to delete initiative',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Force delete initiative with children",
        description="Force delete an initiative and all its child initiatives (confirmed cascade deletion). "
                    "Use this endpoint after receiving a cascade deletion warning from the regular delete endpoint.",
        tags=['initiatives'],
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    'message': 'Initiative deleted successfully. 3 child initiative(s) were also deleted.',
                    'deleted_children_count': 3
                },
                response_only=True,
                status_codes=['204']
            ),
            OpenApiExample(
                'Error Response',
                value={
                    'error': {
                        'code': 'FORCE_DELETION_FAILED',
                        'message': 'Failed to force delete initiative',
                        'details': 'Error details'
                    }
                },
                response_only=True,
                status_codes=['400']
            )
        ]
    )
    @action(detail=True, methods=['delete'])
    def force_delete(self, request, pk=None):
        """
        Force delete initiative with all children (confirmed cascade deletion).
        
        Args:
            request: HTTP request object
            pk: Initiative primary key
            
        Returns:
            Response: Success response or error details
        """
        try:
            instance = self.get_object()
            children_count = instance.children.count()
            
            self.perform_destroy(instance)
            
            return Response({
                'message': f'Initiative deleted successfully. {children_count} child initiative(s) were also deleted.',
                'deleted_children_count': children_count
            }, status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'FORCE_DELETION_FAILED',
                        'message': 'Failed to force delete initiative',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Get initiative hierarchy",
        description="Retrieve the complete hierarchy tree for an initiative including all ancestors (parents) and descendants (children). "
                    "Returns the current initiative, its position in the hierarchy, and counts of ancestors and descendants.",
        tags=['initiatives'],
        examples=[
            OpenApiExample(
                'Hierarchy Response',
                value={
                    'current': {
                        'id': 5,
                        'name': 'Project Alpha',
                        'type': 'project',
                        'type_name': 'Project',
                        'level': 1
                    },
                    'ancestors': [
                        {
                            'id': 1,
                            'name': 'Strategic Program',
                            'type': 'program',
                            'type_name': 'Program',
                            'level': 0
                        }
                    ],
                    'descendants': [
                        {
                            'id': 10,
                            'name': 'Sprint 1',
                            'type': 'event',
                            'type_name': 'Event',
                            'level': 2,
                            'children': []
                        }
                    ],
                    'total_ancestors': 1,
                    'total_descendants': 1
                },
                response_only=True
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """
        Get the full hierarchy tree for this initiative (ancestors and descendants).
        
        Args:
            request: HTTP request object
            pk: Initiative primary key
            
        Returns:
            Response: Hierarchy tree data
        """
        initiative = self.get_object()
        
        # Get ancestors
        ancestors = []
        current = initiative.parent
        while current:
            ancestors.insert(0, {
                'id': current.id,
                'name': current.name,
                'type': current.type.code if current.type else None,
                'type_name': current.type.name if current.type else None,
                'level': current.get_hierarchy_level()
            })
            current = current.parent
        
        # Get descendants recursively
        def get_descendants(init):
            children = []
            for child in init.children.all():
                child_data = {
                    'id': child.id,
                    'name': child.name,
                    'type': child.type.code if child.type else None,
                    'type_name': child.type.name if child.type else None,
                    'level': child.get_hierarchy_level(),
                    'children': get_descendants(child)
                }
                children.append(child_data)
            return children
        
        descendants = get_descendants(initiative)
        
        return Response({
            'current': {
                'id': initiative.id,
                'name': initiative.name,
                'type': initiative.type.code if initiative.type else None,
                'type_name': initiative.type.name if initiative.type else None,
                'level': initiative.get_hierarchy_level()
            },
            'ancestors': ancestors,
            'descendants': descendants,
            'total_ancestors': len(ancestors),
            'total_descendants': len(initiative.get_all_children())
        })
    
    @extend_schema(
        summary="Add team member to initiative",
        description="Add a person as a team member to this initiative. Provide the person_id in the request body.",
        tags=['initiatives'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'person_id': {
                        'type': 'integer',
                        'description': 'ID of the person to add as team member'
                    }
                },
                'required': ['person_id'],
                'example': {
                    'person_id': 42
                }
            }
        },
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    'message': 'John Doe added as team member',
                    'team_count': 5
                },
                response_only=True,
                status_codes=['200']
            ),
            OpenApiExample(
                'Missing Person ID',
                value={
                    'error': {
                        'code': 'MISSING_PERSON_ID',
                        'message': 'person_id is required'
                    }
                },
                response_only=True,
                status_codes=['400']
            ),
            OpenApiExample(
                'Person Not Found',
                value={
                    'error': {
                        'code': 'PERSON_NOT_FOUND',
                        'message': 'Person not found'
                    }
                },
                response_only=True,
                status_codes=['404']
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def add_team_member(self, request, pk=None):
        """
        Add a team member to this initiative.
        
        Args:
            request: HTTP request object
            pk: Initiative primary key
            
        Returns:
            Response: Success response or error details
        """
        initiative = self.get_object()
        person_id = request.data.get('person_id')
        
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
            person = Person.objects.get(id=person_id)
            initiative.team_members.add(person)
            
            return Response({
                'message': f'{person.name} added as team member',
                'team_count': initiative.team_members.count()
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
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'ADD_TEAM_MEMBER_FAILED',
                        'message': 'Failed to add team member',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Remove team member from initiative",
        description="Remove a person from the team members of this initiative. Provide the person_id in the request body.",
        tags=['initiatives'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'person_id': {
                        'type': 'integer',
                        'description': 'ID of the person to remove from team'
                    }
                },
                'required': ['person_id'],
                'example': {
                    'person_id': 42
                }
            }
        },
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    'message': 'John Doe removed from team',
                    'team_count': 4
                },
                response_only=True,
                status_codes=['200']
            ),
            OpenApiExample(
                'Missing Person ID',
                value={
                    'error': {
                        'code': 'MISSING_PERSON_ID',
                        'message': 'person_id is required'
                    }
                },
                response_only=True,
                status_codes=['400']
            ),
            OpenApiExample(
                'Person Not Found',
                value={
                    'error': {
                        'code': 'PERSON_NOT_FOUND',
                        'message': 'Person not found'
                    }
                },
                response_only=True,
                status_codes=['404']
            )
        ]
    )
    @action(detail=True, methods=['delete'])
    def remove_team_member(self, request, pk=None):
        """
        Remove a team member from this initiative.
        
        Args:
            request: HTTP request object
            pk: Initiative primary key
            
        Returns:
            Response: Success response or error details
        """
        initiative = self.get_object()
        person_id = request.data.get('person_id')
        
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
            person = Person.objects.get(id=person_id)
            initiative.team_members.remove(person)
            
            return Response({
                'message': f'{person.name} removed from team',
                'team_count': initiative.team_members.count()
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
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'REMOVE_TEAM_MEMBER_FAILED',
                        'message': 'Failed to remove team member',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Get available initiative types",
        description="Retrieve a list of all active initiative types (program, project, event) that can be used when creating initiatives.",
        tags=['initiatives'],
        examples=[
            OpenApiExample(
                'Types Response',
                value={
                    'types': [
                        {
                            'id': 1,
                            'code': 'program',
                            'name': 'Program',
                            'description': 'High-level strategic initiative',
                            'is_active': True
                        },
                        {
                            'id': 2,
                            'code': 'project',
                            'name': 'Project',
                            'description': 'Specific deliverable-focused work',
                            'is_active': True
                        },
                        {
                            'id': 3,
                            'code': 'event',
                            'name': 'Event',
                            'description': 'Time-bound activity',
                            'is_active': True
                        }
                    ]
                },
                response_only=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def types(self, request):
        """
        Get available initiative types.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: List of available initiative types
        """
        types = InitiativeType.objects.filter(is_active=True).order_by('name')
        serializer = InitiativeTypeSerializer(types, many=True)
        return Response({
            'types': serializer.data
        })
    
    @extend_schema(
        summary="Search initiatives",
        description="Advanced search endpoint for initiatives. Searches across initiative name, description, and coordinator name. "
                    "Provide a search query using the 'q' parameter.",
        tags=['initiatives'],
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query string',
                required=True
            ),
        ],
        examples=[
            OpenApiExample(
                'Search Results',
                value={
                    'results': [
                        {
                            'id': 1,
                            'name': 'Digital Transformation Program',
                            'description': 'Company-wide digital transformation',
                            'type': 'program'
                        }
                    ],
                    'count': 1,
                    'query': 'digital'
                },
                response_only=True
            ),
            OpenApiExample(
                'Empty Query',
                value={
                    'results': [],
                    'message': 'Please provide a search query using the "q" parameter'
                },
                response_only=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search endpoint for initiatives.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Search results
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({
                'results': [],
                'message': 'Please provide a search query using the "q" parameter'
            })
        
        # Search across multiple fields
        queryset = self.get_queryset().filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(coordinator__first_name__icontains=query) |
            models.Q(coordinator__last_name__icontains=query)
        )
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'query': query
        })