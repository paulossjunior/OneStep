# Design Document

## Overview

This design document outlines the technical approach for renaming the `group_organization` Django app to `organizational_group` and renaming the models `GroupOrganization` to `OrganizationalGroup` and `GroupLeadership` to `OrganizationalGroupLeadership`. The refactoring will be performed systematically to ensure zero data loss and minimal disruption to the application.

## Architecture

### Refactoring Strategy

The refactoring will follow a systematic approach:

1. **File System Changes**: Rename the app directory and update all file references
2. **Model Renaming**: Update model class names and metadata
3. **Database Migration**: Create migrations to rename database tables
4. **Code Updates**: Update all imports, references, and related code
5. **Testing**: Verify all functionality works correctly after changes

### Migration Strategy

Django migrations will handle database table renaming:
- Use `migrations.RenameModel()` operations to rename tables
- Preserve all data, indexes, and constraints
- Maintain referential integrity across foreign keys

## Components and Interfaces

### 1. App Directory Structure

**Before:**
```
apps/group_organization/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── tests/
├── migrations/
└── management/
```

**After:**
```
apps/organizational_group/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── tests/
├── migrations/
└── management/
```

### 2. Model Renaming Map

| Old Name | New Name | Database Table (Old) | Database Table (New) |
|----------|----------|---------------------|---------------------|
| `GroupOrganization` | `OrganizationalGroup` | `group_organization_grouporganization` | `organizational_group_organizationalgroup` |
| `GroupLeadership` | `OrganizationalGroupLeadership` | `group_organization_groupleadership` | `organizational_group_organizationalgroupleadership` |

### 3. Model Relationships

**OrganizationalGroup Model:**
- `leaders` (ManyToManyField) → through `OrganizationalGroupLeadership`
- `members` (ManyToManyField) → `Person`
- `initiatives` (ManyToManyField) → `Initiative`

**OrganizationalGroupLeadership Model:**
- `group` (ForeignKey) → `OrganizationalGroup`
- `person` (ForeignKey) → `Person`

### 4. Related Name Updates

| Model | Field | Old Related Name | New Related Name |
|-------|-------|-----------------|------------------|
| `OrganizationalGroupLeadership` | `group` | N/A | N/A |
| `OrganizationalGroup` | `leaders` | `led_groups` | `led_groups` (unchanged) |
| `OrganizationalGroup` | `members` | `member_groups` | `member_groups` (unchanged) |
| `OrganizationalGroup` | `initiatives` | `groups` | `groups` (unchanged) |

### 5. Admin Configuration

**Admin Classes:**
- `GroupAdmin` → `OrganizationalGroupAdmin`
- `GroupLeadershipInline` → `OrganizationalGroupLeadershipInline`
- `GroupMemberInline` → `OrganizationalGroupMemberInline`
- `GroupInitiativeInline` → `OrganizationalGroupInitiativeInline`

**Admin Registration:**
```python
@admin.register(OrganizationalGroup)
class OrganizationalGroupAdmin(admin.ModelAdmin):
    ...

# Inline classes reference OrganizationalGroupLeadership
```

### 6. API Layer

**Serializers:**
- `GroupSerializer` → `OrganizationalGroupSerializer`
- `GroupDetailSerializer` → `OrganizationalGroupDetailSerializer`
- `GroupCreateUpdateSerializer` → `OrganizationalGroupCreateUpdateSerializer`
- `GroupLeadershipSerializer` → `OrganizationalGroupLeadershipSerializer`

**ViewSets:**
- `GroupViewSet` → `OrganizationalGroupViewSet`

**API Endpoints:**
- `/api/groups/` → Keep unchanged for backward compatibility
- URL routing will map to `OrganizationalGroupViewSet`

### 7. Import Statement Updates

**Files requiring import updates:**
- `onestep/settings.py`
- `onestep/api_urls.py`
- `apps/initiatives/models.py` (if it references the group models)
- `apps/core/management/commands/create_sample_data.py`
- All test files
- Management commands

**Import pattern change:**
```python
# Old
from apps.group_organization.models import GroupOrganization, GroupLeadership

# New
from apps.organizational_group.models import OrganizationalGroup, OrganizationalGroupLeadership
```

## Data Models

### OrganizationalGroup Model

```python
class OrganizationalGroup(TimestampedModel):
    """
    Represents a university research or organizational group.
    """
    
    TYPE_RESEARCH = 'research'
    TYPE_EXTENSION = 'extension'
    TYPE_CHOICES = [
        (TYPE_RESEARCH, 'Research'),
        (TYPE_EXTENSION, 'Extension'),
    ]
    
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50)
    url = models.URLField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    knowledge_area = models.CharField(max_length=200)
    campus = models.CharField(max_length=200)
    
    leaders = models.ManyToManyField(
        'people.Person',
        through='OrganizationalGroupLeadership',
        related_name='led_groups'
    )
    members = models.ManyToManyField(
        'people.Person',
        related_name='member_groups',
        blank=True
    )
    initiatives = models.ManyToManyField(
        'initiatives.Initiative',
        related_name='groups',
        blank=True
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Organizational Group'
        verbose_name_plural = 'Organizational Groups'
        db_table = 'organizational_group_organizationalgroup'
```

### OrganizationalGroupLeadership Model

```python
class OrganizationalGroupLeadership(TimestampedModel):
    """
    Through model tracking leadership relationships with history.
    """
    
    group = models.ForeignKey(
        'OrganizationalGroup',
        on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'people.Person',
        on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Organizational Group Leadership'
        verbose_name_plural = 'Organizational Group Leaderships'
        db_table = 'organizational_group_organizationalgroupleadership'
```

## Migration Plan

### Migration File Structure

**Migration 1: Rename Models**
```python
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('organizational_group', '0001_initial'),
    ]
    
    operations = [
        migrations.RenameModel(
            old_name='GroupOrganization',
            new_name='OrganizationalGroup',
        ),
        migrations.RenameModel(
            old_name='GroupLeadership',
            new_name='OrganizationalGroupLeadership',
        ),
        migrations.AlterModelOptions(
            name='organizationalgroup',
            options={
                'ordering': ['name'],
                'verbose_name': 'Organizational Group',
                'verbose_name_plural': 'Organizational Groups',
            },
        ),
        migrations.AlterModelOptions(
            name='organizationalgroupleadership',
            options={
                'ordering': ['-start_date'],
                'verbose_name': 'Organizational Group Leadership',
                'verbose_name_plural': 'Organizational Group Leaderships',
            },
        ),
    ]
```

### Migration Execution Steps

1. Create new app directory structure
2. Copy all files to new location
3. Update all code references
4. Create migration for model renaming
5. Apply migration to database
6. Remove old app directory
7. Run tests to verify functionality

## Error Handling

### Potential Issues and Solutions

**Issue 1: Import Errors**
- **Problem**: Old imports still reference `group_organization`
- **Solution**: Use IDE find-and-replace to update all imports systematically
- **Verification**: Run `python manage.py check` to catch import errors

**Issue 2: Migration Conflicts**
- **Problem**: Existing migrations reference old model names
- **Solution**: Django's `RenameModel` operation handles this automatically
- **Verification**: Test migration on a copy of production database

**Issue 3: Admin URL Patterns**
- **Problem**: Admin URLs change from `/admin/group_organization/` to `/admin/organizational_group/`
- **Solution**: Update any hardcoded URLs in tests and documentation
- **Verification**: Test all admin pages manually

**Issue 4: API Endpoint Changes**
- **Problem**: API consumers may expect specific endpoint names
- **Solution**: Keep `/api/groups/` endpoint unchanged for backward compatibility
- **Verification**: Run API tests to ensure endpoints work

**Issue 5: Foreign Key References**
- **Problem**: Other models reference the old model names
- **Solution**: Update all ForeignKey and ManyToManyField references
- **Verification**: Check `Initiative` model and any other models with relationships

## Testing Strategy

### Test Categories

**1. Unit Tests**
- Model creation and validation
- Model methods (add_leader, remove_leader, etc.)
- Serializer validation
- Admin display methods

**2. Integration Tests**
- API endpoint functionality
- Admin interface operations
- Database queries and relationships
- Migration execution

**3. Regression Tests**
- Existing test suite must pass
- No data loss during migration
- All relationships remain functional

### Test Execution Plan

1. **Pre-Migration Tests**
   - Run full test suite on old code
   - Document all passing tests
   - Create database backup

2. **Post-Refactoring Tests**
   - Run full test suite on new code
   - Verify all tests still pass
   - Test admin interface manually
   - Test API endpoints manually

3. **Migration Tests**
   - Test migration on development database
   - Verify data integrity after migration
   - Test rollback capability

### Test Files to Update

- `apps/organizational_group/tests/test_models.py`
- `apps/organizational_group/tests/test_admin.py`
- `apps/organizational_group/tests/test_api.py`
- `apps/organizational_group/tests/test_serializers.py`
- `apps/core/management/commands/create_sample_data.py`

## Implementation Checklist

### Phase 1: Preparation
- [ ] Create backup of current codebase
- [ ] Create backup of database
- [ ] Document all current functionality
- [ ] Run full test suite to establish baseline

### Phase 2: File System Changes
- [ ] Create new `apps/organizational_group/` directory
- [ ] Copy all files from old directory
- [ ] Update `apps.py` configuration
- [ ] Update `__init__.py` if needed

### Phase 3: Model Updates
- [ ] Rename `GroupOrganization` to `OrganizationalGroup`
- [ ] Rename `GroupLeadership` to `OrganizationalGroupLeadership`
- [ ] Update Meta classes with new verbose names
- [ ] Update all model methods and properties
- [ ] Update docstrings

### Phase 4: Admin Updates
- [ ] Rename admin classes
- [ ] Update admin registrations
- [ ] Update inline classes
- [ ] Update display methods
- [ ] Test admin interface

### Phase 5: API Updates
- [ ] Rename serializer classes
- [ ] Update serializer Meta classes
- [ ] Rename viewset classes
- [ ] Update viewset methods
- [ ] Test API endpoints

### Phase 6: Import Updates
- [ ] Update `settings.py` INSTALLED_APPS
- [ ] Update `api_urls.py` imports
- [ ] Update test file imports
- [ ] Update management command imports
- [ ] Search codebase for any remaining old imports

### Phase 7: Migration
- [ ] Create migration file
- [ ] Test migration on development database
- [ ] Verify data integrity
- [ ] Document migration process

### Phase 8: Testing
- [ ] Run full test suite
- [ ] Fix any failing tests
- [ ] Test admin interface manually
- [ ] Test API endpoints manually
- [ ] Verify all relationships work

### Phase 9: Documentation
- [ ] Update README.md
- [ ] Update API_DOCUMENTATION.md
- [ ] Update code comments
- [ ] Update example code snippets

### Phase 10: Cleanup
- [ ] Remove old `apps/group_organization/` directory
- [ ] Remove any temporary files
- [ ] Commit changes to version control

## Rollback Plan

If issues arise during implementation:

1. **Before Migration**: Simply revert code changes
2. **After Migration**: 
   - Restore database from backup
   - Revert code changes
   - Re-run old migrations if needed

## Performance Considerations

- Model renaming does not affect query performance
- Database table renaming is a metadata operation (fast)
- No data copying required
- Indexes and constraints are preserved
- Foreign key relationships remain optimized

## Security Considerations

- No security implications from renaming
- Maintain existing permission checks
- Preserve authentication requirements
- Keep API authentication unchanged

## Backward Compatibility

- API endpoint `/api/groups/` remains unchanged
- Related names remain unchanged where possible
- Serializer field names remain unchanged
- Database relationships preserved
