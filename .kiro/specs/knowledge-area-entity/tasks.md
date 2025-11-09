# Implementation Plan: Knowledge Area Entity

## Overview
This implementation plan converts the KnowledgeArea feature design into actionable coding tasks. Each task builds incrementally on previous work, ending with full integration of the KnowledgeArea entity to replace the CharField implementation in OrganizationalGroup.

---

## Tasks

- [x] 1. Create KnowledgeArea model and initial migration
  - Create KnowledgeArea model in `apps/organizational_group/models.py` with fields: name (CharField, max_length=200), description (TextField, blank=True), created_at, updated_at
  - Implement `clean()` method with case-insensitive uniqueness validation and empty name validation
  - Implement `group_count()` method to return count of associated groups
  - Implement `__str__()` method returning the name
  - Add Meta class with ordering=['name'], verbose_name, verbose_name_plural, and indexes on name field
  - Generate migration file using `python manage.py makemigrations`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Add foreign key field to OrganizationalGroup
  - Add nullable `knowledge_area_id` ForeignKey field to OrganizationalGroup model pointing to KnowledgeArea
  - Use `on_delete=models.PROTECT` to prevent deletion of referenced KnowledgeArea records
  - Add `related_name='groups'` for reverse relationship
  - Keep existing `knowledge_area` CharField temporarily for data migration
  - Generate migration file using `python manage.py makemigrations`
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Create data migration to populate KnowledgeArea
  - Create data migration using `python manage.py makemigrations --empty organizational_group`
  - Extract all unique knowledge_area CharField values from OrganizationalGroup (case-insensitive)
  - Create KnowledgeArea records for each unique value with proper deduplication
  - Map each OrganizationalGroup to the appropriate KnowledgeArea via knowledge_area_id FK
  - Add validation to ensure all OrganizationalGroup records have knowledge_area_id populated
  - Make migration reversible to restore CharField values if needed
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Finalize OrganizationalGroup model changes
  - Remove old `knowledge_area` CharField from OrganizationalGroup model
  - Rename `knowledge_area_id` field to `knowledge_area` in the model
  - Add NOT NULL constraint to knowledge_area FK
  - Update model's `clean()` method to validate knowledge_area FK exists
  - Update indexes to include knowledge_area FK
  - Generate migration file using `python manage.py makemigrations`
  - _Requirements: 2.1, 2.5_

- [x] 5. Register KnowledgeArea in Django admin
  - Create KnowledgeAreaAdmin class in `apps/organizational_group/admin.py`
  - Configure list_display with: name, description_preview (truncated), group_count_display, created_at
  - Add list_filter for created_at and updated_at
  - Add search_fields for name and description
  - Add readonly_fields for id, created_at, updated_at, group_count_display
  - Implement `group_count_display()` method with HTML formatting showing count of associated groups
  - Implement `get_queryset()` with annotation for group_count performance optimization
  - Add fieldsets to organize form layout
  - Register model with @admin.register(KnowledgeArea) decorator
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6. Update OrganizationalGroupAdmin for KnowledgeArea
  - Add 'knowledge_area' to autocomplete_fields in OrganizationalGroupAdmin
  - Update list_display to show knowledge_area name instead of CharField
  - Add 'knowledge_area' to list_filter
  - Update search_fields to include 'knowledge_area__name'
  - Update get_queryset() to use select_related('knowledge_area', 'campus') for optimization
  - Create knowledge_area_display() method with HTML formatting
  - Update help text for knowledge_area field in get_form()
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Create KnowledgeArea API serializer and viewset
  - Create KnowledgeAreaSerializer in `apps/organizational_group/serializers.py` with all model fields
  - Add group_count as SerializerMethodField with get_group_count() method
  - Set read_only_fields for id, created_at, updated_at, group_count
  - Implement validate_name() to enforce non-empty validation
  - Create KnowledgeAreaViewSet in `apps/organizational_group/views.py` with ModelViewSet
  - Configure permission_classes=[IsAuthenticated]
  - Add filter_backends: DjangoFilterBackend, SearchFilter, OrderingFilter
  - Configure filterset_fields=['name'], search_fields=['name', 'description']
  - Add pagination_class=StandardResultsSetPagination
  - Implement get_queryset() with annotated group count for performance
  - Implement custom destroy() method to handle PROTECT constraint errors with clear error messages
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.4_

- [x] 8. Update OrganizationalGroup API for nested KnowledgeArea
  - Update OrganizationalGroupSerializer to include nested KnowledgeArea representation (read-only)
  - Display KnowledgeArea as nested object with id, name, description, group_count fields
  - Update OrganizationalGroupCreateUpdateSerializer to accept knowledge_area_id (write-only, required)
  - Implement validate_knowledge_area_id() to verify KnowledgeArea exists
  - Update get_queryset() in OrganizationalGroupViewSet to use select_related('knowledge_area')
  - Update filterset_fields to include 'knowledge_area_id'
  - Update search_fields to include 'knowledge_area__name'
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9. Register KnowledgeArea API endpoint
  - Add KnowledgeArea router registration in `apps/organizational_group/urls.py`
  - Register as 'knowledge-areas' endpoint with KnowledgeAreaViewSet
  - Fix existing GroupViewSet reference to OrganizationalGroupViewSet
  - Verify URL patterns are correctly configured
  - _Requirements: 6.1_

- [x] 10. Update CSV import for KnowledgeArea integration
  - Locate CSV import handler code (likely in management commands or views)
  - Update import logic to use get_or_create for KnowledgeArea with case-insensitive lookup
  - Implement: `KnowledgeArea.objects.get_or_create(name__iexact=value, defaults={'name': value.strip()})`
  - Update OrganizationalGroup creation to use knowledge_area FK instead of CharField
  - Add validation for empty knowledge_area values in CSV
  - Add error handling for KnowledgeArea validation errors with row number reporting
  - Wrap import in database transaction for rollback on errors
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]* 11. Write tests for KnowledgeArea model
  - Create `apps/organizational_group/tests/test_knowledge_area_model.py`
  - Test KnowledgeArea creation with valid data
  - Test case-insensitive uniqueness constraint
  - Test empty name validation
  - Test clean() method validation logic
  - Test group_count() method returns correct count
  - Test __str__() method returns name
  - _Requirements: 1.1, 1.2, 1.3, 8.1, 8.2_

- [ ]* 12. Write tests for KnowledgeArea admin interface
  - Create `apps/organizational_group/tests/test_knowledge_area_admin.py`
  - Test KnowledgeArea admin list view displays all columns correctly
  - Test search functionality on name and description
  - Test filtering by creation date
  - Test group_count_display shows correct formatted count
  - Test creating KnowledgeArea via admin
  - Test editing KnowledgeArea via admin
  - Test deletion prevention when groups reference the KnowledgeArea
  - Test autocomplete functionality from OrganizationalGroup admin
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1_

- [ ]* 13. Write tests for KnowledgeArea API
  - Create `apps/organizational_group/tests/test_knowledge_area_api.py`
  - Test GET /api/knowledge-areas/ list endpoint with pagination
  - Test POST /api/knowledge-areas/ create endpoint with valid data
  - Test validation errors for empty name and duplicate names
  - Test GET /api/knowledge-areas/{id}/ retrieve endpoint
  - Test PUT/PATCH /api/knowledge-areas/{id}/ update endpoints
  - Test DELETE /api/knowledge-areas/{id}/ with and without associated groups
  - Test filtering by name
  - Test search functionality on name and description
  - Test authentication requirement
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 14. Write tests for OrganizationalGroup API with KnowledgeArea
  - Update `apps/organizational_group/tests/test_api.py`
  - Test GET /api/organizational-groups/{id}/ returns nested KnowledgeArea object
  - Test POST /api/organizational-groups/ with knowledge_area_id creates group correctly
  - Test validation error for invalid knowledge_area_id
  - Test PATCH /api/organizational-groups/{id}/ to update knowledge_area_id
  - Test filtering by knowledge_area_id
  - Test search by knowledge_area name
  - Verify select_related optimization prevents N+1 queries
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 15. Write tests for data migration
  - Create `apps/organizational_group/tests/test_knowledge_area_migration.py`
  - Test migration creates unique KnowledgeArea records from existing data
  - Test case-insensitive deduplication (e.g., "Computer Science" and "computer science" → one record)
  - Test all OrganizationalGroup records have knowledge_area_id populated after migration
  - Test correct KnowledgeArea assignment to each group
  - Test migration reversibility restores CharField values
  - Test edge cases: whitespace, special characters, very long names
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 16. Write tests for CSV import with KnowledgeArea
  - Update or create CSV import tests in appropriate test file
  - Test import with existing KnowledgeArea uses existing record (case-insensitive)
  - Test import with new knowledge_area value creates KnowledgeArea automatically
  - Test import with empty knowledge_area reports validation error
  - Test batch import with multiple groups using same knowledge_area creates single KnowledgeArea
  - Test transaction rollback on validation errors
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

---

## Notes

- Tasks marked with `*` are optional testing tasks focused on comprehensive test coverage
- Core implementation tasks (1-10) must be completed in order as each builds on the previous
- Testing tasks (11-16) can be implemented in parallel with core tasks or after completion
- All migrations should be tested in a development environment before applying to production
- Backup database before running migrations in production
- The implementation follows the same pattern as the Campus model which serves as a reference

