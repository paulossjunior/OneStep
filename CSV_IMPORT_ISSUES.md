# CSV Import Issues After Model Refactoring

## Overview
The CSV import functionality in `apps/organizational_group/csv_import/` has compatibility issues after the model refactoring from `OrganizationalGroup` to `OrganizationalUnit`.

## Issues Found

### 1. Model Name References (Low Priority)
**Files Affected:**
- `apps/organizational_group/csv_import/group_handler.py`
- `apps/organizational_group/admin.py` (line 10)

**Issue:**
Code uses `OrganizationalGroup` and `OrganizationalGroupLeadership` which are now backward compatibility aliases for `OrganizationalUnit` and `OrganizationalUnitLeadership`.

**Status:** ✅ Working (aliases provide backward compatibility)

**Recommendation:** Update imports to use the new model names for clarity:
```python
from .models import OrganizationalUnit, OrganizationalUnitLeadership, Campus, KnowledgeArea
```

### 2. TYPE_RESEARCH Constant (HIGH PRIORITY - BROKEN)
**File Affected:**
- `apps/organizational_group/csv_import/group_handler.py` (line 69)

**Issue:**
```python
type=OrganizationalGroup.TYPE_RESEARCH,
```

The model no longer has `TYPE_RESEARCH`, `TYPE_EXTENSION`, etc. constants. The new architecture uses `OrganizationalType` as a separate model with a foreign key relationship.

**Status:** ❌ BROKEN - This will cause a runtime error

**Required Fix:**
The code needs to be updated to:
1. Get or create an `OrganizationalType` instance
2. Use that instance as the `type` foreign key

Example fix:
```python
# In group_handler.py, add method to get/create type
def get_or_create_research_type(self):
    """Get or create Research organizational type."""
    from apps.organizational_group.models import OrganizationalType
    org_type, _ = OrganizationalType.objects.get_or_create(
        code='research',
        defaults={
            'name': 'Research',
            'description': 'Research groups'
        }
    )
    return org_type

# Then in create_or_skip_group method:
research_type = self.get_or_create_research_type()
group = OrganizationalGroup.objects.create(
    name=name,
    short_name=short_name,
    url=repository_url.strip() if repository_url else "",
    type=research_type,  # Use OrganizationalType instance
    knowledge_area=knowledge_area,
    campus=campus
)
```

### 3. Missing Organization Field (HIGH PRIORITY - BROKEN)
**File Affected:**
- `apps/organizational_group/csv_import/group_handler.py` (line 64-71)

**Issue:**
The `OrganizationalUnit` model now requires an `organization` foreign key field, but the CSV import code doesn't provide it.

**Status:** ❌ BROKEN - This will cause a database integrity error

**Required Fix:**
Add logic to get or create an `Organization` instance:
```python
# In group_handler.py, add method to get/create organization
def get_or_create_default_organization(self):
    """Get or create default organization for imports."""
    from apps/organizational_group.models import Organization
    org, _ = Organization.objects.get_or_create(
        name='Default Organization',
        defaults={
            'description': 'Default organization for imported groups'
        }
    )
    return org

# Then in create_or_skip_group method:
organization = self.get_or_create_default_organization()
group = OrganizationalGroup.objects.create(
    name=name,
    short_name=short_name,
    url=repository_url.strip() if repository_url else "",
    type=research_type,
    organization=organization,  # Add organization field
    knowledge_area=knowledge_area,
    campus=campus
)
```

## Summary

**✅ Fixed:**
- Added `get_or_create_research_type()` method to create OrganizationalType instances
- Added `get_or_create_default_organization()` method to create Organization instances
- Updated `create_or_skip_group()` to use these new methods
- Updated imports to use new model names with aliases for backward compatibility

**⚠️ Database Schema Issue:**
- The `organizational_group_organizationalunit` table has an old `type` VARCHAR column (NOT NULL)
- New `type_id` and `organization_id` foreign key columns were added
- The old `type` column conflicts with the new model structure

**Status:** PARTIALLY FIXED - Code is updated but database schema needs migration

## Database Migration Needed

The database has mixed old and new schema:
- Old: `type` VARCHAR(20) NOT NULL
- New: `type_id` INTEGER NULL (foreign key to OrganizationalType)
- New: `organization_id` INTEGER NULL (foreign key to Organization)

**Recommended Action:**
1. Run proper migrations to update the database schema
2. Or reset the database and run all migrations fresh

**Priority:** HIGH - The CSV import code is fixed but won't work until database schema is updated.
