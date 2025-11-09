# Django Admin & API Development Focus

## Development Priorities
This project focuses exclusively on:
1. **Django Admin Interface** - Administrative backend
2. **REST API** - Public/private API endpoints

## Django Admin Guidelines

### Admin Configuration
- Register all models in admin.py with proper ModelAdmin classes
- Customize list_display, list_filter, search_fields for usability
- Use fieldsets to organize form layouts
- Implement custom admin actions where needed
- Add proper help_text and verbose_name to model fields

### Admin Best Practices
- Use readonly_fields for computed or sensitive data
- Implement get_queryset() for performance optimization
- Add custom admin views for complex operations
- Use inlines for related model editing
- Implement proper permissions and user groups

## API Development Guidelines

### DRF Patterns
- Use ViewSets for CRUD operations
- Implement proper serializers with validation
- Use permissions classes for access control
- Implement filtering, searching, and pagination
- Follow RESTful URL patterns

### API Structure
```python
# Standard ViewSet pattern
class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['field1', 'field2']
    search_fields = ['name', 'description']
```

### Response Standards
- Use consistent JSON response formats
- Implement proper HTTP status codes
- Include pagination metadata
- Provide meaningful error messages
- Follow API versioning conventions

## No Frontend Development
- **No HTML templates** (except admin customization)
- **No static frontend assets** (CSS/JS for user-facing pages)
- **No client-side frameworks** (React, Vue, etc.)
- Focus purely on backend API and admin interface

## Testing Focus
- Test API endpoints thoroughly
- Test admin interface functionality
- Test model validation and business logic
- Use Django's test client for admin testing
- Use DRF test utilities for API testing