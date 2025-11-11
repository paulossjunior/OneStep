"""
Filter classes for the scholarships app.
"""
import django_filters
from django.db import models
from .models import ScholarshipType, Scholarship


class ScholarshipTypeFilter(django_filters.FilterSet):
    """
    Filter class for ScholarshipType model.
    
    Provides filtering capabilities for ScholarshipType list endpoints.
    """
    
    # Text search filters
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Filter by name (case-insensitive partial match)'
    )
    
    code = django_filters.CharFilter(
        field_name='code',
        lookup_expr='icontains',
        help_text='Filter by code (case-insensitive partial match)'
    )
    
    # Boolean filters
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        help_text='Filter by active status (true/false)'
    )
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter types created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter types created before this date/time'
    )
    
    class Meta:
        model = ScholarshipType
        fields = {
            'name': ['exact', 'icontains'],
            'code': ['exact', 'icontains'],
            'is_active': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
        }


class ScholarshipFilter(django_filters.FilterSet):
    """
    Filter class for Scholarship model.
    
    Provides comprehensive filtering capabilities for Scholarship list endpoints
    including filtering by type, campus, people, dates, and values.
    
    Requirements: 6.5
    """
    
    # Text search filters
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text='Filter by title (case-insensitive partial match)'
    )
    
    # Foreign key filters
    type = django_filters.NumberFilter(
        field_name='type',
        help_text='Filter by scholarship type ID'
    )
    
    campus = django_filters.NumberFilter(
        field_name='campus',
        help_text='Filter by campus ID'
    )
    
    supervisor = django_filters.NumberFilter(
        field_name='supervisor',
        help_text='Filter by supervisor person ID'
    )
    
    student = django_filters.NumberFilter(
        field_name='student',
        help_text='Filter by student person ID'
    )
    
    sponsor = django_filters.NumberFilter(
        field_name='sponsor',
        help_text='Filter by sponsor organization ID'
    )
    
    initiative = django_filters.NumberFilter(
        field_name='initiative',
        help_text='Filter by initiative ID'
    )
    
    # Date range filters
    start_date_after = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        help_text='Filter scholarships starting on or after this date'
    )
    
    start_date_before = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        help_text='Filter scholarships starting on or before this date'
    )
    
    end_date_after = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte',
        help_text='Filter scholarships ending on or after this date'
    )
    
    end_date_before = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        help_text='Filter scholarships ending on or before this date'
    )
    
    # Value range filters
    value_min = django_filters.NumberFilter(
        field_name='value',
        lookup_expr='gte',
        help_text='Filter scholarships with value greater than or equal to this amount'
    )
    
    value_max = django_filters.NumberFilter(
        field_name='value',
        lookup_expr='lte',
        help_text='Filter scholarships with value less than or equal to this amount'
    )
    
    # Boolean filter for active scholarships
    is_active = django_filters.BooleanFilter(
        method='filter_is_active',
        help_text='Filter active scholarships (true/false)'
    )
    
    # Date range filters for created/updated
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter scholarships created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter scholarships created before this date/time'
    )
    
    class Meta:
        model = Scholarship
        fields = {
            'title': ['exact', 'icontains'],
            'type': ['exact'],
            'campus': ['exact'],
            'supervisor': ['exact'],
            'student': ['exact'],
            'sponsor': ['exact'],
            'initiative': ['exact'],
            'start_date': ['exact', 'gte', 'lte'],
            'end_date': ['exact', 'gte', 'lte'],
            'value': ['exact', 'gte', 'lte'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_is_active(self, queryset, name, value):
        """
        Filter scholarships based on whether they are currently active.
        
        A scholarship is active if:
        - start_date <= today
        - end_date is null OR end_date >= today
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Boolean value
            
        Returns:
            QuerySet: Filtered queryset
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        if value is True:
            # Active scholarships
            return queryset.filter(
                start_date__lte=today
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
            )
        elif value is False:
            # Inactive scholarships (not started or already ended)
            return queryset.filter(
                models.Q(start_date__gt=today) |  # Not started yet
                models.Q(end_date__lt=today)  # Already ended
            )
        return queryset
