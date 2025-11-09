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
from .models import Person
from .serializers import PersonSerializer, PersonDetailSerializer
from .filters import PersonFilter


@extend_schema_view(
    list=extend_schema(
        summary="List all people",
        description="Retrieve a paginated list of all people with comprehensive filtering, searching, and ordering capabilities. "
                    "Supports filtering by name, email, creation dates, and initiative relationships. "
                    "Use the search parameter to search across name and email.",
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by name (case-insensitive partial match)'
            ),
            OpenApiParameter(
                name='email',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by email (case-insensitive partial match)'
            ),
            OpenApiParameter(
                name='email_exact',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by exact email (case-insensitive)'
            ),
            OpenApiParameter(
                name='has_coordinated_initiatives',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter people who coordinate initiatives'
            ),
            OpenApiParameter(
                name='has_team_initiatives',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter people who are team members in initiatives'
            ),
            OpenApiParameter(
                name='coordinated_count_min',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter people with at least this many coordinated initiatives'
            ),
            OpenApiParameter(
                name='team_count_min',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter people with at least this many team memberships'
            ),
            OpenApiParameter(
                name='created_after',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter people created after this date/time (ISO 8601 format)'
            ),
            OpenApiParameter(
                name='created_before',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter people created before this date/time (ISO 8601 format)'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search across name and email'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order results by field (prefix with - for descending)',
                enum=['name', '-name', 'email', '-email', 'created_at', '-created_at', 'updated_at', '-updated_at']
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
        tags=['people']
    ),
    retrieve=extend_schema(
        summary="Get person details",
        description="Retrieve detailed information about a specific person including coordinated initiatives and team memberships.",
        tags=['people']
    ),
    create=extend_schema(
        summary="Create new person",
        description="Create a new person with name, email, and optional phone number.",
        tags=['people']
    ),
    update=extend_schema(
        summary="Update person (full)",
        description="Perform a full update of a person. All fields must be provided.",
        tags=['people']
    ),
    partial_update=extend_schema(
        summary="Update person (partial)",
        description="Perform a partial update of a person. Only provided fields will be updated.",
        tags=['people']
    ),
    destroy=extend_schema(
        summary="Delete person",
        description="Delete a person. Cannot delete a person who coordinates initiatives.",
        tags=['people']
    ),
)
class PersonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Person entities through REST API.
    
    Provides CRUD operations for Person management with proper
    authentication, filtering, searching, and pagination.
    
    Endpoints:
        GET /api/people/ - List all people with pagination and filtering
        POST /api/people/ - Create new person
        GET /api/people/{id}/ - Retrieve person details
        PUT /api/people/{id}/ - Update person (full update)
        PATCH /api/people/{id}/ - Partial update person
        DELETE /api/people/{id}/ - Delete person
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [PerformantDjangoFilterBackend, OptimizedSearchFilter, EnhancedOrderingFilter]
    filterset_class = PersonFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'email', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Get optimized queryset with prefetched related data.
        
        Returns:
            QuerySet: Optimized Person queryset
        """
        queryset = Person.objects.select_related().prefetch_related(
            'coordinated_initiatives',
            'team_initiatives'
        )
        
        # Add annotation for counts to improve performance
        queryset = queryset.annotate(
            coordinated_count=Count('coordinated_initiatives', distinct=True),
            team_count=Count('team_initiatives', distinct=True)
        )
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer class: PersonDetailSerializer for retrieve, PersonSerializer for others
        """
        if self.action == 'retrieve':
            return PersonDetailSerializer
        return PersonSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new person with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Created person data or validation errors
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
                        'message': 'Failed to create person',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update person with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Updated person data or validation errors
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
                        'message': 'Failed to update person',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete person with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Success response or error details
        """
        try:
            instance = self.get_object()
            
            # Check if person has coordinated initiatives
            if hasattr(instance, 'coordinated_initiatives') and instance.coordinated_initiatives.exists():
                return Response(
                    {
                        'error': {
                            'code': 'DELETION_BLOCKED',
                            'message': 'Cannot delete person who coordinates initiatives',
                            'details': 'This person coordinates one or more initiatives and cannot be deleted.'
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'DELETION_FAILED',
                        'message': 'Failed to delete person',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Get person's initiatives",
        description="Retrieve all initiatives related to this person, including initiatives they coordinate and initiatives where they are a team member.",
        tags=['people'],
        examples=[
            OpenApiExample(
                'Initiatives Response',
                value={
                    'coordinated_initiatives': [
                        {
                            'id': 1,
                            'name': 'Digital Transformation Program',
                            'type': 'program',
                            'type_name': 'Program',
                            'role': 'coordinator'
                        }
                    ],
                    'team_initiatives': [
                        {
                            'id': 5,
                            'name': 'Project Alpha',
                            'type': 'project',
                            'type_name': 'Project',
                            'role': 'team_member'
                        },
                        {
                            'id': 10,
                            'name': 'Sprint 1',
                            'type': 'event',
                            'type_name': 'Event',
                            'role': 'team_member'
                        }
                    ],
                    'total_coordinated': 1,
                    'total_team_member': 2
                },
                response_only=True
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def initiatives(self, request, pk=None):
        """
        Get all initiatives related to this person (coordinated and team member).
        
        Args:
            request: HTTP request object
            pk: Person primary key
            
        Returns:
            Response: List of related initiatives
        """
        person = self.get_object()
        
        # Get coordinated initiatives
        coordinated = []
        if hasattr(person, 'coordinated_initiatives'):
            coordinated = [
                {
                    'id': init.id,
                    'name': init.name,
                    'type': init.type.code if hasattr(init, 'type') and init.type else None,
                    'type_name': init.type.name if hasattr(init, 'type') and init.type else None,
                    'role': 'coordinator'
                }
                for init in person.coordinated_initiatives.all()
            ]
        
        # Get team initiatives
        team_member = []
        if hasattr(person, 'team_initiatives'):
            team_member = [
                {
                    'id': init.id,
                    'name': init.name,
                    'type': init.type.code if hasattr(init, 'type') and init.type else None,
                    'type_name': init.type.name if hasattr(init, 'type') and init.type else None,
                    'role': 'team_member'
                }
                for init in person.team_initiatives.all()
            ]
        
        return Response({
            'coordinated_initiatives': coordinated,
            'team_initiatives': team_member,
            'total_coordinated': len(coordinated),
            'total_team_member': len(team_member)
        })
    
    @extend_schema(
        summary="Search people",
        description="Advanced search endpoint for people. Searches across person name and email. "
                    "Provide a search query using the 'q' parameter.",
        tags=['people'],
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
                            'name': 'John Doe',
                            'email': 'john.doe@example.com'
                        },
                        {
                            'id': 2,
                            'name': 'Jane Doe',
                            'email': 'jane.doe@example.com'
                        }
                    ],
                    'count': 2,
                    'query': 'doe'
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
        Advanced search endpoint for people.
        
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
            models.Q(email__icontains=query)
        )
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'query': query
        })