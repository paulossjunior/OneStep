"""
ViewSets for the scholarships app REST API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Count, Sum, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from apps.core.pagination import StandardResultsSetPagination
from .models import ScholarshipType, Scholarship
from .serializers import (
    ScholarshipTypeSerializer,
    ScholarshipSerializer,
    ScholarshipDetailSerializer,
    ScholarshipCreateUpdateSerializer
)
from .filters import ScholarshipTypeFilter, ScholarshipFilter


@extend_schema_view(
    list=extend_schema(
        summary="List scholarship types",
        description="Retrieve a paginated list of all scholarship types with filtering and search capabilities.",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search by name, code, or description'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Order by: name, code, is_active, created_at, updated_at'
            ),
        ],
        tags=['Scholarship Types']
    ),
    create=extend_schema(
        summary="Create scholarship type",
        description="Create a new scholarship type with name, code, and description.",
        tags=['Scholarship Types']
    ),
    retrieve=extend_schema(
        summary="Get scholarship type details",
        description="Retrieve detailed information about a specific scholarship type including scholarship count.",
        tags=['Scholarship Types']
    ),
    update=extend_schema(
        summary="Update scholarship type",
        description="Update all fields of a scholarship type.",
        tags=['Scholarship Types']
    ),
    partial_update=extend_schema(
        summary="Partially update scholarship type",
        description="Update specific fields of a scholarship type.",
        tags=['Scholarship Types']
    ),
    destroy=extend_schema(
        summary="Delete scholarship type",
        description="Delete a scholarship type. Cannot delete if scholarships are associated with this type.",
        tags=['Scholarship Types']
    ),
)
class ScholarshipTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ScholarshipType entities through REST API.
    
    Provides CRUD operations for ScholarshipType management with proper
    authentication, filtering, searching, and pagination.
    
    Endpoints:
        GET /api/scholarship-types/ - List all scholarship types
        POST /api/scholarship-types/ - Create new scholarship type
        GET /api/scholarship-types/{id}/ - Retrieve scholarship type details
        PUT /api/scholarship-types/{id}/ - Update scholarship type (full)
        PATCH /api/scholarship-types/{id}/ - Partial update scholarship type
        DELETE /api/scholarship-types/{id}/ - Delete scholarship type
    
    Requirements: 6.1
    """
    
    queryset = ScholarshipType.objects.all()
    serializer_class = ScholarshipTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ScholarshipTypeFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'is_active', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Get optimized queryset with annotations.
        
        Returns:
            QuerySet: Optimized ScholarshipType queryset
        """
        queryset = ScholarshipType.objects.all()
        
        # Add annotation for scholarship count
        queryset = queryset.annotate(
            _scholarship_count=Count('scholarships', distinct=True)
        )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a new scholarship type with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Created scholarship type data or validation errors
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
                        'message': 'Failed to create scholarship type',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update scholarship type with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Updated scholarship type data or validation errors
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'UPDATE_FAILED',
                        'message': 'Failed to update scholarship type',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete scholarship type with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Success response or error details
        """
        try:
            instance = self.get_object()
            
            # Check if type has associated scholarships
            if instance.scholarships.exists():
                return Response(
                    {
                        'error': {
                            'code': 'DELETION_BLOCKED',
                            'message': 'Cannot delete scholarship type with associated scholarships',
                            'details': f'This scholarship type has {instance.scholarships.count()} associated scholarships.'
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
                        'message': 'Failed to delete scholarship type',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    list=extend_schema(
        summary="List scholarships",
        description="Retrieve a paginated list of all scholarships with comprehensive filtering, search, and ordering capabilities.",
        parameters=[
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.INT,
                description='Filter by scholarship type ID'
            ),
            OpenApiParameter(
                name='campus',
                type=OpenApiTypes.INT,
                description='Filter by campus ID'
            ),
            OpenApiParameter(
                name='supervisor',
                type=OpenApiTypes.INT,
                description='Filter by supervisor (Person) ID'
            ),
            OpenApiParameter(
                name='student',
                type=OpenApiTypes.INT,
                description='Filter by student (Person) ID'
            ),
            OpenApiParameter(
                name='sponsor',
                type=OpenApiTypes.INT,
                description='Filter by sponsor (Organization) ID'
            ),
            OpenApiParameter(
                name='initiative',
                type=OpenApiTypes.INT,
                description='Filter by initiative ID'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                description='Filter by active status (currently ongoing scholarships)'
            ),
            OpenApiParameter(
                name='start_date_after',
                type=OpenApiTypes.DATE,
                description='Filter scholarships starting after this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='start_date_before',
                type=OpenApiTypes.DATE,
                description='Filter scholarships starting before this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='end_date_after',
                type=OpenApiTypes.DATE,
                description='Filter scholarships ending after this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='end_date_before',
                type=OpenApiTypes.DATE,
                description='Filter scholarships ending before this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='value_min',
                type=OpenApiTypes.DECIMAL,
                description='Filter scholarships with minimum monthly value'
            ),
            OpenApiParameter(
                name='value_max',
                type=OpenApiTypes.DECIMAL,
                description='Filter scholarships with maximum monthly value'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search by title, student name, supervisor name, or sponsor name'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Order by: start_date, end_date, value, student__name, supervisor__name, created_at, updated_at (prefix with - for descending)'
            ),
        ],
        tags=['Scholarships']
    ),
    create=extend_schema(
        summary="Create scholarship",
        description="Create a new scholarship with all required information including type, dates, people, and funding details.",
        request=ScholarshipCreateUpdateSerializer,
        responses={201: ScholarshipSerializer},
        examples=[
            OpenApiExample(
                'Create Scholarship Example',
                value={
                    'title': 'Research Scholarship - Machine Learning',
                    'type': 1,
                    'campus': 1,
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31',
                    'supervisor': 5,
                    'student': 10,
                    'value': '1500.00',
                    'sponsor': 2,
                    'initiative': 3
                },
                request_only=True
            )
        ],
        tags=['Scholarships']
    ),
    retrieve=extend_schema(
        summary="Get scholarship details",
        description="Retrieve detailed information about a specific scholarship including all related entities and computed properties.",
        responses={200: ScholarshipDetailSerializer},
        tags=['Scholarships']
    ),
    update=extend_schema(
        summary="Update scholarship",
        description="Update all fields of a scholarship with validation for dates, values, and relationships.",
        request=ScholarshipCreateUpdateSerializer,
        responses={200: ScholarshipSerializer},
        tags=['Scholarships']
    ),
    partial_update=extend_schema(
        summary="Partially update scholarship",
        description="Update specific fields of a scholarship with validation.",
        request=ScholarshipCreateUpdateSerializer,
        responses={200: ScholarshipSerializer},
        tags=['Scholarships']
    ),
    destroy=extend_schema(
        summary="Delete scholarship",
        description="Delete a scholarship record.",
        tags=['Scholarships']
    ),
)
class ScholarshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Scholarship entities through REST API.
    
    Provides CRUD operations for Scholarship management with proper
    authentication, filtering, searching, and pagination.
    
    Endpoints:
        GET /api/scholarships/ - List all scholarships
        POST /api/scholarships/ - Create new scholarship
        GET /api/scholarships/{id}/ - Retrieve scholarship details
        PUT /api/scholarships/{id}/ - Update scholarship (full)
        PATCH /api/scholarships/{id}/ - Partial update scholarship
        DELETE /api/scholarships/{id}/ - Delete scholarship
    
    Requirements: 6.1, 6.5
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ScholarshipFilter
    pagination_class = StandardResultsSetPagination
    search_fields = [
        'title',
        'student__name',
        'supervisor__name',
        'sponsor__name'
    ]
    ordering_fields = [
        'start_date',
        'end_date',
        'value',
        'student__name',
        'supervisor__name',
        'created_at',
        'updated_at'
    ]
    ordering = ['-start_date']
    
    def get_queryset(self):
        """
        Get optimized queryset with prefetched related data.
        
        Returns:
            QuerySet: Optimized Scholarship queryset
        """
        queryset = Scholarship.objects.select_related(
            'type',
            'campus',
            'supervisor',
            'student',
            'sponsor',
            'initiative'
        )
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer class: Different serializers for different actions
        """
        if self.action == 'retrieve':
            return ScholarshipDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ScholarshipCreateUpdateSerializer
        return ScholarshipSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new scholarship with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Created scholarship data or validation errors
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            # Return detailed representation
            instance = serializer.instance
            output_serializer = ScholarshipSerializer(instance)
            headers = self.get_success_headers(output_serializer.data)
            
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'CREATION_FAILED',
                        'message': 'Failed to create scholarship',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update scholarship with proper error handling.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Updated scholarship data or validation errors
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # Return detailed representation
            output_serializer = ScholarshipSerializer(instance)
            return Response(output_serializer.data)
        except Exception as e:
            return Response(
                {
                    'error': {
                        'code': 'UPDATE_FAILED',
                        'message': 'Failed to update scholarship',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete scholarship with proper error handling.
        
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
                        'message': 'Failed to delete scholarship',
                        'details': str(e)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Get scholarship statistics",
        description="""
        Retrieve aggregated statistics about scholarships including:
        - Total scholarship count
        - Active scholarship count
        - Total monthly value across all scholarships
        - Distribution by scholarship type
        - Distribution by campus
        - Top 10 supervisors by scholarship count
        - Top 10 sponsors by scholarship count
        
        All filters applied to the list endpoint also apply to statistics.
        """,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_count': {'type': 'integer', 'description': 'Total number of scholarships'},
                    'active_count': {'type': 'integer', 'description': 'Number of currently active scholarships'},
                    'total_monthly_value': {'type': 'string', 'description': 'Sum of all scholarship monthly values'},
                    'by_type': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type__name': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    },
                    'by_campus': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'campus__name': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    },
                    'top_supervisors': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'supervisor__name': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    },
                    'top_sponsors': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'sponsor__name': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        },
        tags=['Scholarships']
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get scholarship statistics.
        
        Returns aggregated statistics about scholarships including:
        - Total count
        - Active count
        - Total value
        - Count by type
        - Count by campus
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Statistics data
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        # Get base queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Total count
        total_count = queryset.count()
        
        # Active count
        active_count = queryset.filter(
            start_date__lte=today
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        ).count()
        
        # Total value (sum of all scholarship values)
        total_value = queryset.aggregate(
            total=Sum('value')
        )['total'] or 0
        
        # Count by type
        by_type = list(queryset.values(
            'type__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count'))
        
        # Count by campus
        by_campus = list(queryset.values(
            'campus__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count'))
        
        # Count by supervisor
        by_supervisor = list(queryset.values(
            'supervisor__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10])  # Top 10
        
        # Count by sponsor
        by_sponsor = list(queryset.values(
            'sponsor__name'
        ).annotate(
            count=Count('id')
        ).filter(
            sponsor__isnull=False
        ).order_by('-count')[:10])  # Top 10
        
        return Response({
            'total_count': total_count,
            'active_count': active_count,
            'total_monthly_value': str(total_value),
            'by_type': by_type,
            'by_campus': by_campus,
            'top_supervisors': by_supervisor,
            'top_sponsors': by_sponsor
        })
