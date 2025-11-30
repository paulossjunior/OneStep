import django_filters
from django.db import models
from .models import Person


class PersonFilter(django_filters.FilterSet):
    """
    Filter class for Person model to enable advanced filtering in API.
    
    Provides filtering capabilities for Person list endpoints with
    various filter options and search functionality.
    """
    
    # Text search filters
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Filter by name (case-insensitive partial match)'
    )
    
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        help_text='Filter by email (case-insensitive partial match)'
    )
    
    # Exact match filters
    email_exact = django_filters.CharFilter(
        field_name='email',
        lookup_expr='iexact',
        help_text='Filter by exact email (case-insensitive)'
    )
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter people created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter people created before this date/time'
    )
    
    # Boolean filters for related data
    has_coordinated_initiatives = django_filters.BooleanFilter(
        method='filter_has_coordinated_initiatives',
        help_text='Filter people who coordinate initiatives (true/false)'
    )
    
    has_team_initiatives = django_filters.BooleanFilter(
        method='filter_has_team_initiatives',
        help_text='Filter people who are team members in initiatives (true/false)'
    )
    
    # Number range filters
    coordinated_count_min = django_filters.NumberFilter(
        method='filter_coordinated_count_min',
        help_text='Filter people with at least this many coordinated initiatives'
    )
    
    team_count_min = django_filters.NumberFilter(
        method='filter_team_count_min',
        help_text='Filter people with at least this many team memberships'
    )
    
    class Meta:
        model = Person
        fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_has_coordinated_initiatives(self, queryset, name, value):
        """
        Filter people based on whether they coordinate initiatives.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Boolean value
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is True:
            return queryset.filter(coordinated_initiatives__isnull=False).distinct()
        elif value is False:
            return queryset.filter(coordinated_initiatives__isnull=True).distinct()
        return queryset
    
    def filter_has_team_initiatives(self, queryset, name, value):
        """
        Filter people based on whether they are team members in initiatives.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Boolean value
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is True:
            return queryset.filter(team_initiatives__isnull=False).distinct()
        elif value is False:
            return queryset.filter(team_initiatives__isnull=True).distinct()
        return queryset
    
    def filter_coordinated_count_min(self, queryset, name, value):
        """
        Filter people with minimum number of coordinated initiatives.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Minimum count
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is not None:
            return queryset.annotate(
                coord_count=models.Count('coordinated_initiatives', distinct=True)
            ).filter(coord_count__gte=value)
        return queryset
    
    def filter_team_count_min(self, queryset, name, value):
        """
        Filter people with minimum number of team memberships.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Minimum count
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is not None:
            return queryset.annotate(
                team_count=models.Count('team_initiatives', distinct=True)
            ).filter(team_count__gte=value)
        return queryset