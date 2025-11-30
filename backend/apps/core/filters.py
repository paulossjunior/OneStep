"""
Custom filtering classes for OneStep API.

Provides enhanced filtering capabilities with performance optimizations
and consistent filtering patterns across all endpoints.
"""

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models


class OptimizedSearchFilter(SearchFilter):
    """
    Enhanced search filter with performance optimizations.
    
    Provides case-insensitive search with database-level optimizations
    and support for related field searching.
    """
    
    def get_search_terms(self, request):
        """
        Extract and clean search terms from request.
        
        Args:
            request: HTTP request object
            
        Returns:
            list: Cleaned search terms
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # Remove null bytes
        return params.split()
    
    def construct_search(self, field_name):
        """
        Construct database search lookup for field.
        
        Args:
            field_name: Name of field to search
            
        Returns:
            str: Database lookup string
        """
        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = 'icontains'
        return models.Q(**{field_name + '__' + lookup: models.Value('')})


class EnhancedOrderingFilter(OrderingFilter):
    """
    Enhanced ordering filter with additional capabilities.
    
    Provides consistent ordering with support for related fields
    and default ordering fallbacks.
    """
    
    def get_default_ordering(self, view):
        """
        Get default ordering for view.
        
        Args:
            view: API view instance
            
        Returns:
            list: Default ordering fields
        """
        ordering = getattr(view, 'ordering', None)
        if ordering:
            return ordering
        
        # Fallback to model ordering
        queryset = getattr(view, 'queryset', None)
        if queryset is not None:
            model_ordering = queryset.model._meta.ordering
            if model_ordering:
                return model_ordering
        
        # Final fallback to primary key
        return ['pk']
    
    def get_valid_fields(self, queryset, view, context={}):
        """
        Get valid fields for ordering.
        
        Args:
            queryset: QuerySet to order
            view: API view instance
            context: Additional context
            
        Returns:
            list: Valid ordering fields
        """
        valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)
        
        if valid_fields == '__all__':
            # Allow ordering on all model fields and some related fields
            valid_fields = [
                field.name for field in queryset.model._meta.fields
                if not field.many_to_many and not field.one_to_many
            ]
            
            # Add some common related field patterns
            for field in queryset.model._meta.fields:
                if field.is_relation and not field.many_to_many:
                    # Add related field name patterns
                    related_model = field.related_model
                    if hasattr(related_model, 'name'):
                        valid_fields.append(f'{field.name}__name')
                    if hasattr(related_model, 'title'):
                        valid_fields.append(f'{field.name}__title')
        
        if valid_fields is None:
            return self.get_default_valid_fields(queryset, view)
        
        return [(item, item) for item in valid_fields]


class PerformantDjangoFilterBackend(DjangoFilterBackend):
    """
    Enhanced Django filter backend with performance optimizations.
    
    Provides optimized filtering with query analysis and
    automatic select_related/prefetch_related optimizations.
    """
    
    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset with performance optimizations.
        
        Args:
            request: HTTP request object
            queryset: QuerySet to filter
            view: API view instance
            
        Returns:
            QuerySet: Filtered queryset
        """
        filter_class = self.get_filterset_class(view, queryset)
        if filter_class:
            # Apply filters
            filterset = filter_class(
                request.query_params,
                queryset=queryset,
                request=request
            )
            
            if filterset.is_valid():
                queryset = filterset.qs
                
                # Optimize queryset based on applied filters
                queryset = self._optimize_queryset(queryset, filterset, view)
        
        return queryset
    
    def _optimize_queryset(self, queryset, filterset, view):
        """
        Optimize queryset based on applied filters.
        
        Args:
            queryset: Filtered queryset
            filterset: Applied filterset
            view: API view instance
            
        Returns:
            QuerySet: Optimized queryset
        """
        # Add select_related for foreign key filters
        select_related_fields = []
        prefetch_related_fields = []
        
        for filter_name, filter_value in filterset.data.items():
            if filter_value and '__' in filter_name:
                field_parts = filter_name.split('__')
                if len(field_parts) >= 2:
                    field_name = field_parts[0]
                    
                    # Check if it's a foreign key field
                    try:
                        field = queryset.model._meta.get_field(field_name)
                        if field.is_relation and not field.many_to_many:
                            if field_name not in select_related_fields:
                                select_related_fields.append(field_name)
                        elif field.many_to_many or field.one_to_many:
                            if field_name not in prefetch_related_fields:
                                prefetch_related_fields.append(field_name)
                    except:
                        pass  # Field doesn't exist, skip optimization
        
        # Apply optimizations
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)
        
        if prefetch_related_fields:
            queryset = queryset.prefetch_related(*prefetch_related_fields)
        
        return queryset