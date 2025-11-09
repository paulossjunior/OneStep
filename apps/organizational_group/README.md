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

### OrganizationalGroup

Represents a university research or organizational group.

**Fields:**
- `name` - Full group name
- `short_name` - Abbreviated name (unique per campus)
- `url` - Group website (optional)
- `type` - Group type: `research` or `extension`
- `knowledge_area` - Research/study domain
- `campus` - University campus location

**Relationships:**
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

**Base URL:** `/api/groups/`

**Main Endpoints:**
- `GET /api/organizationalgroups/` - List groups
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

### Creating a Group

```python
from apps.organizational_group.models import OrganizationalGroup
from apps.people.models import Person

# Create a group
group = OrganizationalGroup.objects.create(
    name="Artificial Intelligence Research Lab",
    short_name="AI-LAB",
    url="https://ai-lab.university.edu",
    type="research",
    knowledge_area="Computer Science",
    campus="Main Campus"
)

# Add a leader
person = Person.objects.get(id=1)
group.add_leader(person, start_date="2024-01-01")

# Add members
members = Person.objects.filter(id__in=[2, 3, 4])
group.members.set(members)
```

### Querying Groups

```python
# Get all research groups
research_groups = OrganizationalGroup.objects.filter(type='research')

# Get groups on Main Campus
main_campus_groups = OrganizationalGroup.objects.filter(campus='Main Campus')

# Get groups with current leaders
from django.db.models import Q
groups_with_leaders = OrganizationalGroup.objects.filter(
    organizationalgroupleadership__is_active=True
).distinct()

# Get group with prefetched data
group = OrganizationalGroup.objects.prefetch_related(
    'members',
    'initiatives',
    'organizationalgroupleadership_set__person'
).get(id=1)
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
│   OrganizationalGroup        │
├──────────────────────────────┤
│ id (PK)                      │
│ name                         │
│ short_name                   │
│ url                          │
│ type                         │
│ knowledge_area               │
│ campus                       │
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

- `short_name` + `campus` must be unique
- `end_date` must be >= `start_date` in OrganizationalGroupLeadership
- Cannot have duplicate active leaders for the same person
- `name` and `short_name` are required
- `type` must be either `research` or `extension`

## Performance Considerations

- Use `select_related()` for leader queries
- Use `prefetch_related()` for members and initiatives
- Indexes on `type`, `campus`, `knowledge_area` for filtering
- Composite index on `short_name` + `campus` for uniqueness check
- Annotate counts in querysets to avoid N+1 queries

## Future Enhancements

- Group publications or outputs tracking
- Group activity timeline
- Group budget management
- Group dashboard with analytics
- Group participation metrics in initiatives
- Email notifications for leadership changes
- Group hierarchy (parent-child groups)
