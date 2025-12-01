import django_filters
from django.db import models
from .models import Initiative, InitiativeType


class InitiativeFilter(django_filters.FilterSet):
    """
    Filter class for Initiative model to enable advanced filtering in API.
    
    Provides filtering capabilities for Initiative list endpoints with
    various filter options and search functionality.
    """
    
    # Text search filters
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Filter by name (case-insensitive partial match)'
    )
    
    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        help_text='Filter by description (case-insensitive partial match)'
    )
    
    # Choice filters
    type = django_filters.ModelChoiceFilter(
        queryset=InitiativeType.objects.filter(is_active=True),
        help_text='Filter by initiative type'
    )
    
    type_code = django_filters.CharFilter(
        field_name='type__code',
        help_text='Filter by initiative type code (program, project, event)'
    )
    
    type_codes = django_filters.MultipleChoiceFilter(
        field_name='type__code',
        choices=[
            ('program', 'Program'),
            ('project', 'Project'),
            ('event', 'Event'),
        ],
        help_text='Filter by multiple initiative type codes'
    )
    
    # Foreign key filters
    coordinator = django_filters.NumberFilter(
        field_name='coordinator__id',
        help_text='Filter by coordinator person ID'
    )
    
    coordinator_name = django_filters.CharFilter(
        field_name='coordinator__name',
        lookup_expr='icontains',
        help_text='Filter by coordinator name (case-insensitive partial match)'
    )
    
    parent = django_filters.NumberFilter(
        field_name='parent__id',
        help_text='Filter by parent initiative ID'
    )
    
    demanding_partner = django_filters.NumberFilter(
        field_name='demanding_partner__id',
        help_text='Filter by demanding partner organization ID'
    )
    
    demanding_partner_name = django_filters.CharFilter(
        field_name='demanding_partner__name',
        lookup_expr='icontains',
        help_text='Filter by demanding partner name (case-insensitive partial match)'
    )
    
    has_demanding_partner = django_filters.BooleanFilter(
        method='filter_has_demanding_partner',
        help_text='Filter initiatives that have a demanding partner'
    )
    
    # Hierarchical filters
    is_root = django_filters.BooleanFilter(
        method='filter_is_root',
        help_text='Filter root initiatives (no parent)'
    )
    
    has_children = django_filters.BooleanFilter(
        method='filter_has_children',
        help_text='Filter initiatives that have child initiatives'
    )
    
    hierarchy_level = django_filters.NumberFilter(
        method='filter_hierarchy_level',
        help_text='Filter by hierarchy level (0 = root)'
    )
    
    # Date range filters
    start_date_after = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        help_text='Filter initiatives starting after this date'
    )
    
    start_date_before = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        help_text='Filter initiatives starting before this date'
    )
    
    end_date_after = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte',
        help_text='Filter initiatives ending after this date'
    )
    
    end_date_before = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        help_text='Filter initiatives ending before this date'
    )
    
    # Status filters
    is_active = django_filters.BooleanFilter(
        method='filter_is_active',
        help_text='Filter active initiatives (start_date <= today <= end_date or no end_date)'
    )
    
    is_upcoming = django_filters.BooleanFilter(
        method='filter_is_upcoming',
        help_text='Filter upcoming initiatives (start_date > today)'
    )
    
    is_completed = django_filters.BooleanFilter(
        method='filter_is_completed',
        help_text='Filter completed initiatives (end_date < today)'
    )
    
    # Team filters
    team_member = django_filters.NumberFilter(
        field_name='team_members__id',
        help_text='Filter initiatives where person is a team member'
    )
    
    team_size_min = django_filters.NumberFilter(
        method='filter_team_size_min',
        help_text='Filter initiatives with minimum team size'
    )
    
    team_size_max = django_filters.NumberFilter(
        method='filter_team_size_max',
        help_text='Filter initiatives with maximum team size'
    )
    
    # Creation date filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter initiatives created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter initiatives created before this date/time'
    )
    
    class Meta:
        model = Initiative
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'type': ['exact'],
            'start_date': ['exact', 'gte', 'lte'],
            'end_date': ['exact', 'gte', 'lte', 'isnull'],
            'coordinator': ['exact'],
            'parent': ['exact', 'isnull'],
            'demanding_partner': ['exact', 'isnull'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_is_root(self, queryset, name, value):
        """
        Filter root initiatives (no parent).
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Boolean value
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is True:
            return queryset.filter(parent__isnull=True)
        elif value is False:
            return queryset.filter(parent__isnull=False)
        return queryset
    
    def filter_has_children(self, queryset, name, value):
        """
        Filter initiatives that have child initiatives.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Boolean value
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is True:
            return queryset.filter(children__isnull=False).distinct()
        elif value is False:
            return queryset.filter(children__isnull=True).distinct()
        return queryset
    
    def filter_hierarchy_level(self, queryset, name, value):
        """
        Filter by hierarchy level.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Hierarchy level
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is not None:
            # This is a simplified approach - for exact level filtering
            # we would need a more complex query or database function
            if value == 0:
                return queryset.filter(parent__isnull=True)
            elif value == 1:
                return queryset.filter(parent__isnull=False, parent__parent__isnull=True)
            elif value == 2:
                return queryset.filter(
                    parent__isnull=False, 
                    parent__parent__isnull=False,
                    parent__parent__parent__isnull=True
                )
            # For higher levels, we'd need a more sophisticated approach
        return queryset
    
    def filter_is_active(self, queryset, name, value):
        """
        Filter active initiatives.
        
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
            return queryset.filter(
                start_date__lte=today
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
            )
        elif value is False:
            return queryset.filter(
                models.Q(start_date__gt=today) | models.Q(end_date__lt=today)
            )
        return queryset
    
    def filter_is_upcoming(self, queryset, name, value):
        """
        Filter upcoming initiatives.
        
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
            return queryset.filter(start_date__gt=today)
        elif value is False:
            return queryset.filter(start_date__lte=today)
        return queryset
    
    def filter_is_completed(self, queryset, name, value):
        """
        Filter completed initiatives.
        
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
            return queryset.filter(end_date__lt=today)
        elif value is False:
            return queryset.filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
            )
        return queryset
    
    def filter_team_size_min(self, queryset, name, value):
        """
        Filter initiatives with minimum team size.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Minimum team size
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is not None:
            return queryset.annotate(
                team_size=models.Count('team_members', distinct=True)
            ).filter(team_size__gte=value)
        return queryset
    
    def filter_team_size_max(self, queryset, name, value):
        """
        Filter initiatives with maximum team size.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Maximum team size
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is not None:
            return queryset.annotate(
                team_size=models.Count('team_members', distinct=True)
            ).filter(team_size__lte=value)
        return queryset
    
    def filter_has_demanding_partner(self, queryset, name, value):
        """
        Filter initiatives that have a demanding partner.
        
        Args:
            queryset: Base queryset
            name: Filter field name
            value: Boolean value
            
        Returns:
            QuerySet: Filtered queryset
        """
        if value is True:
            return queryset.filter(demanding_partner__isnull=False)
        elif value is False:
            return queryset.filter(demanding_partner__isnull=True)
        return queryset