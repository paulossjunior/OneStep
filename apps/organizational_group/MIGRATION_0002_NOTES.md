# Migration 0002: Allow Same Short Name on Different Campuses

## Overview

This migration updates the database constraint to allow organizational units (research groups) to have the same `short_name` as long as they are on different campuses.

## Problem

The original constraint enforced uniqueness on `(short_name, organization)`, which prevented two groups with the same short name from existing even if they were on different campuses.

**Example of the issue:**
- NEEF group at Cariacica campus ✓
- NEEF group at Serra campus ✗ (blocked by constraint)

## Solution

Changed the unique constraint from:
```python
UniqueConstraint(fields=['short_name', 'organization'])
```

To:
```python
UniqueConstraint(fields=['short_name', 'organization', 'campus'])
```

## Impact

### Before Migration
- Groups with the same short_name could NOT exist in the same organization, regardless of campus
- Import would fail with error: "An organizational unit with short name 'NEEF' already exists in organization 'Default Organization'"

### After Migration
- Groups with the same short_name CAN exist if they are on different campuses
- NEEF at Cariacica ✓
- NEEF at Serra ✓
- Both can coexist peacefully

## Real-World Use Case

From the research groups CSV, we have:
1. **NEEF** - Núcleo de Estruturação do Ensino de Física do IFES (Cariacica)
2. **NEEF** - NUCLEO DE ESTUDOS EM ENSINO DE FISICA (Serra)

These are two distinct research groups that happen to use the same acronym but operate on different campuses.

## Database Changes

### Constraint Removed
- Name: `unique_short_name_organization`
- Fields: `['short_name', 'organization']`

### Constraint Added
- Name: `unique_short_name_organization_campus`
- Fields: `['short_name', 'organization', 'campus']`

## Migration Steps

1. Remove old constraint `unique_short_name_organization`
2. Add new constraint `unique_short_name_organization_campus`

## Running the Migration

```bash
# Apply the migration
python manage.py migrate organizational_group

# Verify migration status
python manage.py showmigrations organizational_group
```

## Rollback (if needed)

To rollback this migration:
```bash
python manage.py migrate organizational_group 0001_initial
```

**Warning:** Rolling back will restore the old constraint, which may cause issues if you already have groups with the same short_name on different campuses.

## Testing

After applying the migration, you can verify it works by:

1. Importing the research groups CSV:
   ```bash
   python manage.py import_research_groups example/research_group/research_groups.csv
   ```

2. Checking that both NEEF groups are imported:
   ```python
   from apps.organizational_group.models import OrganizationalUnit
   
   neef_groups = OrganizationalUnit.objects.filter(short_name='NEEF')
   print(f"Found {neef_groups.count()} NEEF groups")
   for group in neef_groups:
       print(f"  - {group.name} at {group.campus.name}")
   ```

Expected output:
```
Found 2 NEEF groups
  - Núcleo De Estruturação Do Ensino De Física Do Ifes at Cariacica
  - Nucleo De Estudos Em Ensino De Fisica at Serra
```

## Related Files

- Model: `apps/organizational_group/models.py`
- Migration: `apps/organizational_group/migrations/0002_allow_same_shortname_different_campus.py`
- Import Logic: `apps/organizational_group/csv_import/group_handler.py`

## Notes

- This change aligns the database constraint with the import logic, which already checks for duplicates based on `(short_name, campus, organization)`
- The constraint now properly reflects the business rule: "A group's short name must be unique within a campus and organization"
- This is a common pattern in multi-campus university systems where different campuses may independently use the same acronyms
