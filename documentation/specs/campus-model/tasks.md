# Implementation Plan

- [x] 1. Create Campus model and initial migration
  - Add Campus model to `apps/organizational_group/models.py` with name, code, and location fields
  - Implement `__str__()`, `clean()`, and `group_count()` methods
  - Add Meta class with ordering, indexes, and verbose names
  - Create initial migration for Campus model
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Add campus_id field to OrganizationalGroup
  - Add nullable `campus_id` ForeignKey field to OrganizationalGroup model
  - Keep existing `campus` CharField temporarily for data migration
  - Create migration for adding campus_id field
  - _Requirements: 5.1, 5.5_

- [x] 3. Create data migration for campus conversion
  - Write data migration to extract unique campus values from OrganizationalGroup
  - Implement `generate_campus_code()` function to create codes from names
  - Create Campus records for each unique campus value
  - Map OrganizationalGroup records to Campus foreign keys
  - Handle edge cases (empty, null, duplicate names)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4. Finalize OrganizationalGroup model changes
  - Make `campus_id` field non-nullable
  - Remove old `campus` CharField
  - Update unique constraint from `['short_name', 'campus']` to `['short_name', 'campus_id']`
  - Update `clean()` method validation logic for campus foreign key
  - Create migration for finalizing schema changes
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 5. Create Campus serializer
  - Implement `CampusSerializer` in `apps/organizational_group/serializers.py`
  - Add `group_count` SerializerMethodField
  - Implement field validation for name and code
  - Add code auto-uppercase logic in validation
  - _Requirements: 3.1, 3.2, 3.3, 3.8_

- [x] 6. Update OrganizationalGroup serializers
  - Add nested `CampusSerializer` for read operations
  - Add `campus_id` write-only field for create/update operations
  - Update `OrganizationalGroupCreateUpdateSerializer` to handle campus_id
  - Update validation logic to work with campus foreign key
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7. Create Campus ViewSet and API endpoints
  - Implement `CampusViewSet` in `apps/organizational_group/views.py`
  - Configure filtering by name and code
  - Configure search across name, code, and location
  - Add ordering capabilities
  - Optimize queryset with group count annotation
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 8. Update OrganizationalGroup ViewSet
  - Update queryset to use `select_related('campus')`
  - Update filtering to support campus_id
  - Ensure nested campus data appears in responses
  - _Requirements: 6.1, 6.2, 6.6_

- [x] 9. Register Campus API routes
  - Update `apps/organizational_group/urls.py` to register CampusViewSet
  - Ensure routes are at `/api/campuses/`
  - Verify routes are included in main URL configuration
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 10. Create Campus admin interface
  - Implement `CampusAdmin` in `apps/organizational_group/admin.py`
  - Configure list_display with name, code, location, and group_count
  - Add filtering and search capabilities
  - Implement `group_count_display()` method with HTML formatting
  - Configure fieldsets for organized form layout
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [-] 11. Update OrganizationalGroup admin interface
  - Update list_display to show campus name
  - Update list_filter to use campus foreign key
  - Add campus to autocomplete_fields
  - Update queryset to use `select_related('campus')`
  - Update form help text for campus field
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 12. Run and verify migrations
  - Run `python manage.py makemigrations` to generate all migrations
  - Review generated migration files for correctness
  - Run `python manage.py migrate` to apply migrations
  - Verify Campus table created with correct schema
  - Verify OrganizationalGroup table updated correctly
  - Verify data migrated successfully from CharField to Campus FK
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

- [x] 13. Update documentation
  - Update `apps/organizational_group/README.md` with Campus model documentation
  - Update `apps/organizational_group/API_DOCUMENTATION.md` with Campus API endpoints
  - Add Campus usage examples and database schema updates
  - Update product.md steering rule with Campus in data model diagram
  - _Requirements: All requirements for documentation completeness_

- [ ]* 14. Write Campus model tests
  - Create `apps/organizational_group/tests/test_campus_models.py`
  - Test campus creation with valid data
  - Test campus string representation
  - Test campus validation (empty name, empty code)
  - Test campus code uniqueness constraint
  - Test group_count() method
  - Test campus code auto-uppercase in clean()
  - _Requirements: 8.1, 8.2, 8.3_

- [ ]* 15. Write Campus serializer tests
  - Create `apps/organizational_group/tests/test_campus_serializers.py`
  - Test campus serialization
  - Test campus deserialization
  - Test validation errors for empty name and code
  - Test group_count field in serialized output
  - Test code auto-uppercase in validation
  - _Requirements: 8.7_

- [ ]* 16. Write Campus API tests
  - Create `apps/organizational_group/tests/test_campus_api.py`
  - Test list campuses endpoint with pagination
  - Test create campus endpoint
  - Test retrieve campus endpoint
  - Test update campus endpoint (PUT and PATCH)
  - Test delete campus endpoint
  - Test filtering by name and code
  - Test search functionality across fields
  - Test ordering by different fields
  - _Requirements: 8.4, 8.6_

- [ ]* 17. Write Campus admin tests
  - Create `apps/organizational_group/tests/test_campus_admin.py`
  - Test campus list view displays correctly
  - Test campus create form
  - Test campus edit form
  - Test campus delete with and without associated groups
  - Test search functionality
  - Test filtering capabilities
  - _Requirements: 8.4_

- [ ]* 18. Update OrganizationalGroup tests
  - Update `apps/organizational_group/tests/test_models.py` for campus FK
  - Test group creation with campus foreign key
  - Test unique constraint with campus_id
  - Test PROTECT cascade behavior when deleting campus
  - Test validation with invalid campus_id
  - Update `apps/organizational_group/tests/test_serializers.py` for nested campus
  - Test nested campus serialization in group responses
  - Test campus_id write operation
  - Test validation with invalid campus_id
  - Update `apps/organizational_group/tests/test_api.py` for campus integration
  - Test creating group with campus_id
  - Test updating group campus_id
  - Test filtering groups by campus_id
  - Test nested campus data in API responses
  - Update `apps/organizational_group/tests/test_admin.py` for campus autocomplete
  - Test campus autocomplete functionality
  - Test campus display in list view
  - Test campus filtering
  - _Requirements: 8.5, 8.6, 8.7_

- [ ]* 19. Write migration tests
  - Create `apps/organizational_group/tests/test_migrations.py`
  - Test forward migration creates Campus records from existing data
  - Test forward migration maps OrganizationalGroup to Campus correctly
  - Test migration handles empty campus values gracefully
  - Test migration handles duplicate campus names
  - Test reverse migration restores campus CharField
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
