# Implementation Plan: Scholarship Management System

## Tasks

- [x] 1. Create Django app structure
  - Create `scholarships` Django app
  - Add app to INSTALLED_APPS in settings
  - Create app directory structure (models, admin, serializers, views, urls, tests)
  - _Requirements: All_

- [x] 2. Implement ScholarshipType model
  - Create ScholarshipType model with name, code, description, is_active fields
  - Add unique constraints for name and code
  - Add indexes for code and is_active
  - Implement __str__ method
  - Implement clean() method for validation
  - Add scholarship_count() method
  - Create and apply migration
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3. Implement Scholarship model
  - Create Scholarship model with all required fields (title, type, campus, start_date, end_date, supervisor, student, value, sponsor, initiative)
  - Add ForeignKey relationships to Person, Organization, Campus, and Initiative
  - Add DecimalField for value with proper precision
  - Add database constraints (end_date >= start_date, value > 0)
  - Add indexes for frequently queried fields (title, campus, initiative, etc.)
  - Implement __str__ method
  - Implement clean() method with all validation rules
  - Add duration_months() property
  - Add is_active() property
  - Add total_value() property
  - Create and apply migration
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 4.1.1, 4.1.2, 4.1.3, 7.1, 7.2, 7.3, 7.4_

- [ ] 4. Implement ScholarshipType admin interface
  - Register ScholarshipType in admin
  - Configure list_display with name, code, is_active, scholarship_count, created_at
  - Add list_filter for is_active and created_at
  - Add search_fields for name, code, description
  - Add readonly_fields for id, created_at, updated_at, scholarship_count
  - Create fieldsets for organized form layout
  - Implement get_queryset with annotations for scholarship_count
  - Add custom display methods with formatting
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 5. Implement Scholarship admin interface
  - Register Scholarship in admin
  - Configure list_display with title, student, supervisor, type, campus, value, start_date, end_date, duration, status, sponsor
  - Add list_filter for type, campus, supervisor, student, sponsor, initiative, start_date, end_date
  - Add search_fields for title, student name, supervisor name, sponsor name
  - Add readonly_fields for duration_months, is_active, total_value, created_at, updated_at
  - Create fieldsets for organized form layout (Basic Info, Location, Duration, People, Funding, Project, Statistics, Metadata)
  - Implement get_queryset with select_related and prefetch_related (including campus and initiative)
  - Add custom display methods with color-coded status and formatted currency
  - Add autocomplete_fields for supervisor, student, sponsor, initiative
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. Implement REST API serializers
  - Create ScholarshipTypeSerializer with all fields and scholarship_count
  - Create ScholarshipSerializer with all fields and computed properties
  - Create ScholarshipDetailSerializer with nested objects
  - Create ScholarshipCreateUpdateSerializer for write operations
  - Add validation methods for all business rules
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7. Implement REST API views and URLs
  - Create ScholarshipTypeViewSet with CRUD operations
  - Create ScholarshipViewSet with CRUD operations
  - Configure filtering backend with all filter fields
  - Configure search backend
  - Configure ordering backend
  - Add pagination
  - Create URL patterns and register with router
  - Add API URLs to main urls.py
  - _Requirements: 6.1, 6.5_

- [x] 8. Create default scholarship types
  - Create data migration to populate default scholarship types
  - Add types: Research, Extension, Teaching, Innovation, Monitoring
  - _Requirements: 1.1_

- [x] 9. Update API documentation
  - Add scholarship endpoints to API schema
  - Update Swagger/ReDoc documentation
  - _Requirements: 6.1_

- [ ]* 10. Write tests
  - _Requirements: All_

- [ ]* 10.1 Write model tests
  - Test ScholarshipType model validation and methods
  - Test Scholarship model validation and methods
  - Test duration_months calculation
  - Test is_active property
  - Test total_value calculation
  - Test date validation constraints
  - Test value validation constraints
  - Test overlapping scholarship detection
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 7.1, 7.2, 7.3, 7.4_

- [ ]* 10.2 Write admin tests
  - Test ScholarshipType admin interface
  - Test Scholarship admin interface
  - Test filtering and searching
  - Test custom display methods
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 10.3 Write API tests
  - Test ScholarshipType API endpoints
  - Test Scholarship API endpoints
  - Test filtering, searching, and ordering
  - Test validation error responses
  - Test permissions
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

---

## Notes

### Implementation Order

The tasks are ordered to build incrementally:
1. App structure and configuration
2. Models (data layer)
3. Admin interface (for manual data management)
4. API (for programmatic access)
5. Tests (validation)

### Key Design Decisions

1. **Money Field:** Using DecimalField with max_digits=10, decimal_places=2 for Brazilian Real (BRL)
2. **Date Handling:** Using DateField (not DateTime) since scholarships are day-granular
3. **Relationships:** 
   - PROTECT for supervisor/student (prevent accidental deletion)
   - SET_NULL for sponsor (allow organization deletion)
4. **Validation:** Both database constraints and model clean() method for comprehensive validation
5. **API Design:** Separate serializers for list, detail, and write operations

### Dependencies

- Requires `people` app (Person model)
- Requires `organizational_group` app (Organization, Campus models)
- Requires `initiatives` app (Initiative model)
- Requires `core` app (TimestampedModel)

### Testing Notes

- Tests are marked as optional (*) to focus on core functionality first
- Comprehensive testing should be done before production deployment
- Focus on business logic validation and constraint enforcement
