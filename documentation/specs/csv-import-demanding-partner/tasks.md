# Implementation Plan: CSV Import Demanding Partner Feature

## Status: Refactoring Required

The demanding partner functionality was implemented using `OrganizationalUnit`, but the requirements specify using `Organization` (top-level entity). This requires refactoring the implementation.

**Current State:**
- ✅ CSV processor has demanding partner logic
- ✅ Admin interface displays demanding partner
- ❌ Uses `OrganizationalUnit` instead of `Organization`
- ❌ API does not expose demanding partner

**Required Changes:**
- Change `Initiative.demanding_partner` from `OrganizationalUnit` to `Organization`
- Update `GroupHandler` to create/retrieve `Organization` records
- Update admin interface to reflect new model relationship
- Expose demanding partner in REST API

---

## Tasks

- [x] 1. Refactor Initiative model to use Organization for demanding partner
  - Change `demanding_partner` field from `ForeignKey(OrganizationalUnit)` to `ForeignKey(Organization)`
  - Keep `null=True, blank=True, on_delete=models.SET_NULL`
  - Keep `related_name='demanded_initiatives'`
  - Create and apply database migration
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 2. Update GroupHandler to create Organization records
  - Rename method to `get_or_create_demanding_partner_organization()`
  - Change return type from `OrganizationalUnit` to `Organization`
  - Create Organization with name and description "Organization that demands or requests initiatives"
  - Use case-insensitive matching on Organization.name
  - Handle race conditions with IntegrityError
  - Remove OrganizationalUnit, OrganizationalType, and Campus creation logic
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 5.5_

- [x] 3. Update CSV import processor to use new Organization-based handler
  - Update call to use `get_or_create_demanding_partner_organization()`
  - Remove knowledge_area parameter (Organizations don't have knowledge areas)
  - Update error handling for Organization creation
  - _Requirements: 1.1, 1.5, 4.1, 4.2, 4.3, 4.5_

- [x] 4. Update admin interface for Organization demanding partner
  - Update `demanding_partner_display()` to link to Organization admin
  - Update filters to use Organization model
  - Update fieldsets and help text
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Expose demanding partner in REST API
  - Add `demanding_partner` field to InitiativeSerializer
  - Add `demanding_partner_id` write field to InitiativeCreateUpdateSerializer
  - Include demanding partner in InitiativeDetailSerializer with nested Organization data
  - Update API to support filtering initiatives by demanding partner
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 6. Add comprehensive tests for demanding partner functionality
  - _Requirements: All requirements 1-5_

- [ ]* 6.1 Write unit tests for GroupHandler.get_or_create_demanding_partner_organization()
  - Test creating new demanding partner Organization
  - Test returning existing demanding partner (case-insensitive)
  - Test handling empty/whitespace names
  - Test description field is set correctly
  - Test race condition handling (IntegrityError)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 5.1, 5.2, 5.5_

- [ ]* 6.2 Write integration tests for CSV import with demanding partner
  - Test importing row with demanding partner
  - Test importing row without demanding partner (empty field)
  - Test multiple rows with same demanding partner (reuse)
  - Test error handling for demanding partner creation failures
  - _Requirements: 1.1, 1.5, 4.1, 4.2, 4.3, 4.5, 5.1, 5.2, 5.3, 5.4_

- [ ]* 6.3 Write model tests for Initiative.demanding_partner field
  - Test demanding_partner field is optional (null=True, blank=True)
  - Test SET_NULL behavior when Organization is deleted
  - Test demanded_initiatives reverse relationship
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 6.4 Write API tests for demanding partner endpoints
  - Test retrieving initiatives with demanding partner data
  - Test creating initiative with demanding_partner_id
  - Test updating initiative demanding partner
  - Test filtering initiatives by demanding partner
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

---

## Notes

### Refactoring Rationale

The current implementation uses `OrganizationalUnit` but the requirements clearly specify using top-level `Organization` entities. The refactoring will:

1. **Simplify the model**: Demanding partners are organizations, not sub-units
2. **Match requirements**: Align implementation with specification
3. **Reduce complexity**: No need for OrganizationalType, Campus, or parent Organization
4. **Improve clarity**: Direct Organization reference is more intuitive

### Migration Strategy

1. Create migration to change ForeignKey from OrganizationalUnit to Organization
2. Data migration may be needed if existing data uses OrganizationalUnit
3. Update all references in code (admin, serializers, handlers)
4. Test thoroughly before deploying

### Implementation Details (After Refactoring)

- Demanding partners stored as top-level `Organization` records
- Description field: "Organization that demands or requests initiatives"
- Case-insensitive duplicate detection prevents redundant entries
- Race condition handling via IntegrityError catching
- Simple, direct relationship between Initiative and Organization
