# Organizational Group App

## Overview

The Organizational Group app manages university research and organizational groups within the OneStep system. It provides functionality for creating and managing groups with leaders, members, and associations with initiatives.

## Features

- **Group Management**: Create, read, update, and delete groups
- **Leadership Tracking**: Track current and historical leaders with date ranges
- **Member Management**: Assign people as group members
- **Initiative Associations**: Link groups to initiatives (programs, projects, events)
- **Filtering & Search**: Comprehensive filtering by type, campus, knowledge area
- **REST API**: Full CRUD API with custom actions for leadership management
- **Django Admin**: Administrative interface for group management

## Models

### Campus

Represents a university campus location where organizational groups operate.

**Fields:**
- `name` - Full campus name (max 200 characters, required)
- `code` - Short campus code/identifier (max 20 characters, unique, required)
- `location` - Physical location or address (max 300 characters, optional)
- `created_at` - Timestamp of creation
- `updated_at` - Timestamp of last update

**Relationships:**
- `groups` - One-to-many with OrganizationalGroup (reverse relation)

**Methods:**
- `__str__()` - Returns campus name
- `clean()` - Validates name and code are not empty, auto-uppercases code
- `group_count()` - Returns count of associated organizational groups

**Constraints:**
- `code` must be unique across all campuses
- `name` and `code` cannot be empty strings
- `code` is automatically converted to uppercase

### OrganizationalGroup

Represents a university research or organizational group.

**Fields:**
- `name` - Full group name
- `short_name` - Abbreviated name (unique per campus)
- `url` - Group website (optional)
- `type` - Group type: `research` or `extension`
- `knowledge_area` - Research/study domain
- `campus` - Foreign key to Campus (required, PROTECT on delete)

**Relationships:**
- `campus` - Foreign key to Campus (required)
- `leaders` - Many-to-many with Person (through OrganizationalGroupLeadership)
- `members` - Many-to-many with Person
- `initiatives` - Many-to-many with Initiative

**Methods:**
- `get_current_leaders()` - Returns active leaders
- `get_historical_leaders()` - Returns all leaders including past
- `add_leader(person, start_date)` - Add a new leader
- `remove_leader(person, end_date)` - Remove a leader
- `leader_count()` - Count of current leaders
- `member_count()` - Count of members
- `initiative_count()` - Count of associated initiatives

**Constraints:**
- `short_name` + `campus_id` combination must be unique
- Cannot delete a Campus that has associated groups (PROTECT)

### OrganizationalGroupLeadership

Through model for tracking leadership relationships with history.

**Fields:**
- `group` - Foreign key to OrganizationalGroup
- `person` - Foreign key to Person
- `start_date` - Leadership start date
- `end_date` - Leadership end date (null for current leaders)
- `is_active` - Boolean flag for current leadership

## API Endpoints

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API documentation.

### Campus Endpoints

**Base URL:** `/api/campuses/`

**Main Endpoints:**
- `GET /api/campuses/` - List campuses
- `POST /api/campuses/` - Create campus
- `GET /api/campuses/{id}/` - Get campus details
- `PUT /api/campuses/{id}/` - Update campus (full)
- `PATCH /api/campuses/{id}/` - Update campus (partial)
- `DELETE /api/campuses/{id}/` - Delete campus

**Features:**
- Filtering by name and code
- Search across name, code, and location
- Ordering by name, code, created_at, updated_at
- Returns group_count for each campus

### Organizational Group Endpoints

**Base URL:** `/api/groups/`

**Main Endpoints:**
- `GET /api/groups/` - List groups
- `POST /api/groups/` - Create group
- `GET /api/groups/{id}/` - Get group details
- `PUT /api/groups/{id}/` - Update group (full)
- `PATCH /api/groups/{id}/` - Update group (partial)
- `DELETE /api/groups/{id}/` - Delete group

**Custom Actions:**
- `GET /api/groups/{id}/current_leaders/` - Get current leaders
- `POST /api/groups/{id}/add_leader/` - Add a leader
- `POST /api/groups/{id}/remove_leader/` - Remove a leader
- `GET /api/groups/{id}/leadership_history/` - Get leadership history

**Features:**
- Nested campus data in responses
- Filtering by campus_id
- campus_id required for create/update operations

## Django Admin

The Organizational Groups app provides a comprehensive Django Admin interface:

**Features:**
- List view with group details and counts
- Filtering by type, campus, and knowledge area
- Search by name and short_name
- Inline editing for leaders (with history)
- Inline editing for members
- Inline editing for initiative associations
- Custom admin methods for displaying counts

**Access:** `/admin/organizational_group/organizationalgroup/`

## Usage Examples

### Creating a Campus

```python
from apps.organizational_group.models import Campus

# Create a campus
campus = Campus.objects.create(
    name="Main Campus",
    code="MAIN",
    location="123 University Ave, City, State 12345"
)

# Get group count
count = campus.group_count()
print(f"{campus.name} has {count} groups")
```

### Creating a Group

```python
from apps.organizational_group.models import OrganizationalGroup, Campus
from apps.people.models import Person

# Get or create campus
campus = Campus.objects.get(code="MAIN")

# Create a group
group = OrganizationalGroup.objects.create(
    name="Artificial Intelligence Research Lab",
    short_name="AI-LAB",
    url="https://ai-lab.university.edu",
    type="research",
    knowledge_area="Computer Science",
    campus=campus
)

# Add a leader
person = Person.objects.get(id=1)
group.add_leader(person, start_date="2024-01-01")

# Add members
members = Person.objects.filter(id__in=[2, 3, 4])
group.members.set(members)
```

### Querying Campuses

```python
from django.db.models import Count

# Get all campuses with group counts
campuses = Campus.objects.annotate(
    group_count=Count('groups')
).order_by('-group_count')

# Get campus by code
main_campus = Campus.objects.get(code='MAIN')

# Get campuses with groups
campuses_with_groups = Campus.objects.filter(
    groups__isnull=False
).distinct()
```

### Querying Groups

```python
# Get all research groups
research_groups = OrganizationalGroup.objects.filter(type='research')

# Get groups on Main Campus
main_campus = Campus.objects.get(code='MAIN')
main_campus_groups = OrganizationalGroup.objects.filter(campus=main_campus)

# Get groups with current leaders (optimized)
groups_with_leaders = OrganizationalGroup.objects.filter(
    organizationalgroupleadership__is_active=True
).select_related('campus').distinct()

# Get group with prefetched data
group = OrganizationalGroup.objects.select_related(
    'campus'
).prefetch_related(
    'members',
    'initiatives',
    'organizationalgroupleadership_set__person'
).get(id=1)

# Access nested campus data
print(f"Group: {group.name}")
print(f"Campus: {group.campus.name} ({group.campus.code})")
print(f"Location: {group.campus.location}")
```

### Managing Leadership

```python
from datetime import date

# Add a new leader
group.add_leader(person, start_date=date.today())

# Remove a leader
group.remove_leader(person, end_date=date.today())

# Get current leaders
current_leaders = group.get_current_leaders()

# Get all leaders (including historical)
all_leaders = group.get_historical_leaders()
```

## Testing

The Organizational Groups app includes comprehensive tests:

- **Model Tests** (`tests/test_models.py`) - Test model creation, validation, and methods
- **Serializer Tests** (`tests/test_serializers.py`) - Test API serialization
- **API Tests** (`tests/test_api.py`) - Test API endpoints and custom actions
- **Admin Tests** (`tests/test_admin.py`) - Test Django Admin interface

Run tests:
```bash
python manage.py test apps.organizational_group
```

## Sample Data

### Fixtures

Load sample groups:
```bash
python manage.py loaddata apps/organizational_group/fixtures/sample_groups.json
```

### Management Command

Create sample data programmatically:
```bash
python manage.py create_sample_data --groups 10
```

## Database Schema

```
┌──────────────────────────────┐
│         Campus               │
├──────────────────────────────┤
│ id (PK)                      │
│ name                         │
│ code (UK)                    │
│ location                     │
│ created_at                   │
│ updated_at                   │
└──────────────────────────────┘
         │
         │ (one-to-many)
         ▼
┌──────────────────────────────┐
│   OrganizationalGroup        │
├──────────────────────────────┤
│ id (PK)                      │
│ name                         │
│ short_name                   │
│ url                          │
│ type                         │
│ knowledge_area               │
│ campus_id (FK)               │
│ created_at                   │
│ updated_at                   │
└──────────────────────────────┘
         │
         │ (through OrganizationalGroupLeadership)
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌──────────────────────────────┐  ┌─────────────────────┐
│ OrganizationalGroupLeadership│  │      Person         │
├──────────────────────────────┤  ├─────────────────────┤
│ id (PK)                      │  │ id (PK)             │
│ group_id (FK)                │  │ name                │
│ person_id (FK)               │  │ email               │
│ start_date                   │  │ created_at          │
│ end_date                     │  │ updated_at          │
│ is_active                    │  └─────────────────────┘
│ created_at                   │
│ updated_at                   │
└──────────────────────────────┘

         │ (many-to-many)
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│   group_members     │  │    Initiative       │
├─────────────────────┤  ├─────────────────────┤
│ group_id (FK)       │  │ id (PK)             │
│ person_id (FK)      │  │ name                │
└─────────────────────┘  │ description         │
                         │ type                │
┌─────────────────────┐  │ start_date          │
│ group_initiatives   │  │ end_date            │
├─────────────────────┤  │ created_at          │
│ group_id (FK)       │  │ updated_at          │
│ initiative_id (FK)  │  └─────────────────────┘
└─────────────────────┘
```

## Constraints

### Campus
- `code` must be unique across all campuses
- `name` and `code` cannot be empty strings
- `code` is automatically converted to uppercase

### OrganizationalGroup
- `short_name` + `campus_id` must be unique
- `campus_id` is required (cannot be null)
- Cannot delete a Campus that has associated groups (PROTECT)
- `name` and `short_name` are required
- `type` must be either `research` or `extension`

### OrganizationalGroupLeadership
- `end_date` must be >= `start_date`
- Cannot have duplicate active leaders for the same person

## Performance Considerations

### Campus Queries
- Indexes on `name` and `code` for fast lookups
- Use `annotate(group_count=Count('groups'))` instead of calling `group_count()` in loops
- Use `prefetch_related('groups')` when accessing multiple campuses with their groups

### OrganizationalGroup Queries
- Use `select_related('campus')` for campus data in group queries
- Use `prefetch_related()` for members and initiatives
- Indexes on `type`, `campus_id`, `knowledge_area` for filtering
- Composite index on `short_name` + `campus_id` for uniqueness check
- Annotate counts in querysets to avoid N+1 queries

### Example Optimized Queries

```python
# Optimized campus list with group counts
campuses = Campus.objects.annotate(
    group_count=Count('groups')
).order_by('name')

# Optimized group list with campus data
groups = OrganizationalGroup.objects.select_related(
    'campus'
).prefetch_related(
    'members',
    'initiatives'
).all()

# Optimized nested query
groups = OrganizationalGroup.objects.select_related(
    'campus'
).prefetch_related(
    'organizationalgroupleadership_set__person',
    'members',
    'initiatives'
).filter(campus__code='MAIN')
```

## Future Enhancements

- Group publications or outputs tracking
- Group activity timeline
- Group budget management
- Group dashboard with analytics
- Group participation metrics in initiatives
- Email notifications for leadership changes
- Group hierarchy (parent-child groups)
