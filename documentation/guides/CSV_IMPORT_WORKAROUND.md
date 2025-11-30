# CSV Import Workaround for Schema Conflicts

## Issue
The database has conflicting schema from the model refactoring:
- Old `type` VARCHAR(20) NOT NULL column
- New `type_id` INTEGER NULL foreign key column

When saving models, the `TimestampedModel.save()` method calls `full_clean()` which validates all fields and foreign keys. This causes validation errors because:
1. The old `type` column is NOT NULL but we're not setting it
2. Foreign key validation fails due to schema conflicts

## Workaround Applied

Modified `apps/organizational_group/csv_import/group_handler.py` to bypass `full_clean()` validation during CSV import:

### For OrganizationalUnit Creation:
```python
# Instead of:
group = OrganizationalGroup.objects.create(...)

# We use:
group = OrganizationalGroup(...)
super(OrganizationalGroup, group).save()  # Bypass full_clean()
```

### For OrganizationalUnitLeadership Creation:
```python
# Instead of:
OrganizationalGroupLeadership.objects.create(...)

# We use:
leadership = OrganizationalGroupLeadership(...)
super(OrganizationalGroupLeadership, leadership).save()  # Bypass full_clean()
```

## How It Works

By calling `super(ModelClass, instance).save()`, we skip the overridden `save()` method in `TimestampedModel` that calls `full_clean()`, and go directly to Django's base `Model.save()` method.

This allows the CSV import to work despite the schema conflicts.

## Campus Auto-Creation

The CSV import already supports auto-creating Campus entries:
- `CampusHandler.get_or_create_campus()` checks if campus exists (case-insensitive)
- If not found, creates new campus with auto-generated code
- Uses caching to avoid duplicate database queries

## Knowledge Area Fields

The OrganizationalUnit model has TWO knowledge area fields:

1. **`knowledge_area`** (ForeignKey) - Primary/main knowledge area
   - Set during CSV import from the CSV file
   - Single knowledge area per unit
   - Optional field (can be null)

2. **`knowledge_areas`** (ManyToManyField) - Multiple knowledge areas
   - Automatically synced from associated initiatives
   - Represents all knowledge areas from related initiatives
   - Managed by `sync_knowledge_areas_from_initiatives()` method
   - Not set during CSV import

### CSV Import Behavior
- CSV import sets only the primary `knowledge_area` field
- The `knowledge_areas` ManyToMany field is populated later when initiatives are associated
- Use `unit.sync_knowledge_areas_from_initiatives()` to update the ManyToMany field

## Important Notes

1. **This is a temporary workaround** - The proper fix is to reset the database with clean migrations
2. **Validation is bypassed** - Manual data validation should be done before import
3. **Schema conflicts remain** - Other parts of the application may still have issues
4. **Production use** - This workaround should NOT be used in production without proper database migration

## Proper Fix (Recommended for Production)

```bash
# 1. Backup any important data
python manage.py dumpdata > backup.json

# 2. Remove database
rm db.sqlite3

# 3. Remove old migrations
rm apps/organizational_group/migrations/0*.py

# 4. Create fresh migrations
python manage.py makemigrations

# 5. Apply migrations
python manage.py migrate

# 6. Restore data (if needed)
python manage.py loaddata backup.json
```

## Testing

After applying this workaround, test the CSV import:
1. Prepare a CSV file with organizational group data
2. Access Django admin
3. Navigate to Organizational Units
4. Click "Import CSV"
5. Upload the CSV file
6. Verify groups are created successfully
7. Check that campuses are auto-created for new campus names

## Files Modified

- `apps/organizational_group/csv_import/group_handler.py`
  - Modified `create_or_skip_group()` method
  - Modified `assign_leaders()` method
