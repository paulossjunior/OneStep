# Organizational Group API Documentation

## Overview

The Organizational Group API provides endpoints for managing university campuses and organizational groups. The API includes:

- **Campus Management**: Create and manage university campus locations
- **Group Management**: Create and manage research and organizational groups
- **Leadership Tracking**: Track current and historical group leaders
- **Member Management**: Assign people as group members
- **Initiative Associations**: Link groups to initiatives

**Note:** The groups API uses the endpoint `/api/groups/` for backward compatibility, but the Django app is named `organizational_group` and the model is named `OrganizationalGroup` to avoid conflicts with Django's built-in `Group` model from `django.contrib.auth`.

## Base URLs

```
/api/campuses/  - Campus management endpoints
/api/groups/    - Organizational group management endpoints
```

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Campus Endpoints

### 1. List Campuses

**GET** `/api/campuses/`

Retrieve a paginated list of all campuses with filtering, searching, and ordering capabilities.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Filter by campus name (exact match) |
| `code` | string | Filter by campus code (exact match) |
| `search` | string | Search across name, code, and location |
| `ordering` | string | Order results by field (prefix with `-` for descending). Options: `name`, `code`, `created_at`, `updated_at` |
| `page` | integer | Page number for pagination |
| `page_size` | integer | Number of results per page (default: 10, max: 100) |

#### Example Request

```bash
GET /api/campuses/?search=Main&ordering=name
```

#### Example Response

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Main Campus",
      "code": "MAIN",
      "location": "123 University Ave, City, State 12345",
      "group_count": 15,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "North Campus",
      "code": "NORTH",
      "location": "456 College Rd, City, State 12345",
      "group_count": 8,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

---

### 2. Create Campus

**POST** `/api/campuses/`

Create a new campus location.

#### Request Body

```json
{
  "name": "South Campus",
  "code": "SOUTH",
  "location": "789 Education Blvd, City, State 12345"
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Full campus name (max 200 characters) |
| `code` | string | Yes | Short campus code (max 20 characters, unique, auto-uppercased) |
| `location` | string | No | Physical location or address (max 300 characters) |

#### Validation Rules

- `name` and `code` are required and cannot be empty strings
- `code` must be unique across all campuses
- `code` is automatically converted to uppercase
- `name` and `code` are trimmed of whitespace

#### Example Response

```json
{
  "id": 3,
  "name": "South Campus",
  "code": "SOUTH",
  "location": "789 Education Blvd, City, State 12345",
  "group_count": 0,
  "created_at": "2024-01-15T14:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

#### Status Codes

- `201 Created` - Campus successfully created
- `400 Bad Request` - Validation error (empty name/code, duplicate code)
- `401 Unauthorized` - Authentication required

---

### 3. Get Campus Details

**GET** `/api/campuses/{id}/`

Retrieve detailed information about a specific campus.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Campus ID |

#### Example Request

```bash
GET /api/campuses/1/
```

#### Example Response

```json
{
  "id": 1,
  "name": "Main Campus",
  "code": "MAIN",
  "location": "123 University Ave, City, State 12345",
  "group_count": 15,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

#### Status Codes

- `200 OK` - Success
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Campus not found

---

### 4. Update Campus (Full)

**PUT** `/api/campuses/{id}/`

Perform a full update of a campus. All fields must be provided.

#### Request Body

```json
{
  "name": "Main Campus - Updated",
  "code": "MAIN",
  "location": "123 University Ave, Suite 100, City, State 12345"
}
```

#### Status Codes

- `200 OK` - Campus successfully updated
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Campus not found

---

### 5. Update Campus (Partial)

**PATCH** `/api/campuses/{id}/`

Perform a partial update of a campus. Only provided fields will be updated.

#### Example Request

```json
{
  "location": "123 University Ave, Building A, City, State 12345"
}
```

#### Status Codes

- `200 OK` - Campus successfully updated
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Campus not found

---

### 6. Delete Campus

**DELETE** `/api/campuses/{id}/`

Delete a campus. This operation will fail if there are organizational groups associated with the campus (PROTECT constraint).

#### Status Codes

- `204 No Content` - Campus successfully deleted
- `400 Bad Request` - Cannot delete campus with associated groups
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Campus not found

#### Error Response (when groups exist)

```json
{
  "error": {
    "code": "PROTECTED_ERROR",
    "message": "Cannot delete campus with associated organizational groups",
    "details": "This campus has 15 groups. Remove or reassign them before deleting the campus."
  }
}
```

---

## Organizational Group Endpoints

### 7. List Groups

**GET** `/api/groups/`

Retrieve a paginated list of all groups with comprehensive filtering, searching, and ordering capabilities.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by group type (`research` or `extension`) |
| `campus_id` | integer | Filter by campus ID |
| `knowledge_area` | string | Filter by knowledge area |
| `search` | string | Search across name and short_name |
| `ordering` | string | Order results by field (prefix with `-` for descending). Options: `name`, `short_name`, `type`, `campus`, `created_at`, `updated_at` |
| `page` | integer | Page number for pagination |
| `page_size` | integer | Number of results per page (default: 10, max: 100) |

#### Example Request

```bash
GET /api/groups/?type=research&campus_id=1&ordering=-created_at
```

#### Example Response

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/groups/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Artificial Intelligence Research Lab",
      "short_name": "AI-LAB",
      "url": "https://ai-lab.university.edu",
      "type": "research",
      "knowledge_area": "Computer Science",
      "campus": {
        "id": 1,
        "name": "Main Campus",
        "code": "MAIN",
        "location": "123 University Ave, City, State 12345",
        "group_count": 15
      },
      "current_leaders": [
        {
          "id": 1,
          "person": 1,
          "person_name": "Alice Johnson",
          "person_email": "alice.johnson@onestep.example.com",
          "start_date": "2023-01-01",
          "end_date": null,
          "is_active": true
        }
      ],
      "members": [
        {
          "id": 3,
          "name": "Carol Davis",
          "email": "carol.davis@onestep.example.com"
        }
      ],
      "initiatives": [
        {
          "id": 1,
          "name": "Digital Transformation Program",
          "type_name": "Program"
        }
      ],
      "leader_count": 1,
      "member_count": 3,
      "initiative_count": 2,
      "created_at": "2024-01-01T14:00:00Z",
      "updated_at": "2024-01-01T14:00:00Z"
    }
  ]
}
```

---

### 8. Create Group

**POST** `/api/groups/`

Create a new group with basic information. Leaders and members can be added after creation or during creation.

#### Request Body

```json
{
  "name": "Quantum Computing Lab",
  "short_name": "QC-LAB",
  "url": "https://quantum.university.edu",
  "type": "research",
  "knowledge_area": "Physics",
  "campus_id": 1,
  "leader_ids": [1, 2],
  "member_ids": [3, 4, 5],
  "initiative_ids": [1]
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Full group name (max 200 characters) |
| `short_name` | string | Yes | Abbreviated name (max 50 characters) |
| `url` | string | No | Group website URL |
| `type` | string | Yes | Group type: `research` or `extension` |
| `knowledge_area` | string | Yes | Research/study domain (max 200 characters) |
| `campus_id` | integer | Yes | Campus ID (foreign key to Campus) |
| `leader_ids` | array | No | List of person IDs to add as leaders |
| `member_ids` | array | No | List of person IDs to add as members |
| `initiative_ids` | array | No | List of initiative IDs to associate |

#### Validation Rules

- `name`, `short_name`, and `campus_id` are required
- `short_name` + `campus_id` combination must be unique
- `type` must be either `research` or `extension`
- `url` must be a valid URL format (if provided)
- `campus_id` must reference an existing Campus

#### Example Response

```json
{
  "id": 6,
  "name": "Quantum Computing Lab",
  "short_name": "QC-LAB",
  "url": "https://quantum.university.edu",
  "type": "research",
  "knowledge_area": "Physics",
  "campus": {
    "id": 1,
    "name": "Main Campus",
    "code": "MAIN",
    "location": "123 University Ave, City, State 12345",
    "group_count": 16
  },
  "current_leaders": [],
  "members": [],
  "initiatives": [],
  "leader_count": 0,
  "member_count": 0,
  "initiative_count": 0,
  "created_at": "2024-01-01T15:00:00Z",
  "updated_at": "2024-01-01T15:00:00Z"
}
```

#### Status Codes

- `201 Created` - Group successfully created
- `400 Bad Request` - Validation error (missing campus_id, invalid campus_id, duplicate short_name + campus_id)
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Campus not found

---

### 9. Get Group Details

**GET** `/api/groups/{id}/`

Retrieve detailed information about a specific group including all leaders (current and historical), members, and associated initiatives.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Group ID |

#### Example Request

```bash
GET /api/groups/1/
```

#### Example Response

```json
{
  "id": 1,
  "name": "Artificial Intelligence Research Lab",
  "short_name": "AI-LAB",
  "url": "https://ai-lab.university.edu",
  "type": "research",
  "knowledge_area": "Computer Science",
  "campus": {
    "id": 1,
    "name": "Main Campus",
    "code": "MAIN",
    "location": "123 University Ave, City, State 12345",
    "group_count": 15
  },
  "current_leaders": [
    {
      "id": 1,
      "person": 1,
      "person_name": "Alice Johnson",
      "person_email": "alice.johnson@onestep.example.com",
      "start_date": "2023-01-01",
      "end_date": null,
      "is_active": true
    },
    {
      "id": 2,
      "person": 2,
      "person_name": "Bob Smith",
      "person_email": "bob.smith@onestep.example.com",
      "start_date": "2024-01-01",
      "end_date": null,
      "is_active": true
    }
  ],
  "members": [
    {
      "id": 3,
      "name": "Carol Davis",
      "email": "carol.davis@onestep.example.com"
    },
    {
      "id": 4,
      "name": "David Wilson",
      "email": "david.wilson@onestep.example.com"
    }
  ],
  "initiatives": [
    {
      "id": 1,
      "name": "Digital Transformation Program",
      "type_name": "Program",
      "start_date": "2024-02-01",
      "end_date": "2025-01-31"
    }
  ],
  "leader_count": 2,
  "member_count": 3,
  "initiative_count": 2,
  "created_at": "2024-01-01T14:00:00Z",
  "updated_at": "2024-01-01T14:00:00Z"
}
```

#### Status Codes

- `200 OK` - Success
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group not found

---

### 10. Update Group (Full)

**PUT** `/api/groups/{id}/`

Perform a full update of a group. All fields must be provided.

#### Request Body

Same as Create Group, all fields required (including `campus_id`).

#### Status Codes

- `200 OK` - Group successfully updated
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group or Campus not found

---

### 11. Update Group (Partial)

**PATCH** `/api/groups/{id}/`

Perform a partial update of a group. Only provided fields will be updated.

#### Example Request

```json
{
  "url": "https://new-url.university.edu",
  "knowledge_area": "Advanced Computer Science",
  "campus_id": 2
}
```

#### Status Codes

- `200 OK` - Group successfully updated
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group or Campus not found

---

### 12. Delete Group

**DELETE** `/api/groups/{id}/`

Delete a group. This will also remove all leadership relationships, member associations, and initiative associations.

#### Status Codes

- `204 No Content` - Group successfully deleted
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group not found

---

## Custom Actions

### 13. Get Current Leaders

**GET** `/api/groups/{id}/current_leaders/`

Retrieve only the current active leaders for a group.

#### Example Response

```json
{
  "group_id": 1,
  "group_name": "Artificial Intelligence Research Lab",
  "current_leaders": [
    {
      "id": 1,
      "person": 1,
      "person_name": "Alice Johnson",
      "person_email": "alice.johnson@onestep.example.com",
      "start_date": "2023-01-01",
      "end_date": null,
      "is_active": true
    }
  ],
  "leader_count": 1
}
```

---

### 14. Add Leader

**POST** `/api/groups/{id}/add_leader/`

Add a person as a leader to the group. Creates a new leadership relationship with historical tracking.

#### Request Body

```json
{
  "person_id": 5,
  "start_date": "2024-01-15"
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `person_id` | integer | Yes | ID of the person to add as leader |
| `start_date` | string | No | Leadership start date (YYYY-MM-DD). Defaults to today |

#### Example Response

```json
{
  "message": "Emma Brown added as leader",
  "leadership": {
    "id": 5,
    "person": 5,
    "person_name": "Emma Brown",
    "person_email": "emma.brown@onestep.example.com",
    "start_date": "2024-01-15",
    "end_date": null,
    "is_active": true
  },
  "leader_count": 2
}
```

#### Status Codes

- `201 Created` - Leader successfully added
- `400 Bad Request` - Validation error or person already an active leader
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group or person not found

---

### 15. Remove Leader

**POST** `/api/groups/{id}/remove_leader/`

Remove a person as a leader from the group. Sets the leadership end date and marks as inactive.

#### Request Body

```json
{
  "person_id": 5,
  "end_date": "2024-06-30"
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `person_id` | integer | Yes | ID of the person to remove as leader |
| `end_date` | string | No | Leadership end date (YYYY-MM-DD). Defaults to today |

#### Example Response

```json
{
  "message": "Emma Brown removed as leader",
  "leader_count": 1
}
```

#### Status Codes

- `200 OK` - Leader successfully removed
- `400 Bad Request` - Validation error or person not an active leader
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group or person not found

---

### 16. Get Leadership History

**GET** `/api/groups/{id}/leadership_history/`

Retrieve the complete leadership history for a group, including both current and past leaders.

#### Example Response

```json
{
  "group_id": 2,
  "group_name": "Sustainable Agriculture Extension",
  "current_leaders": [
    {
      "id": 4,
      "person": 4,
      "person_name": "David Wilson",
      "person_email": "david.wilson@onestep.example.com",
      "start_date": "2024-01-01",
      "end_date": null,
      "is_active": true
    }
  ],
  "historical_leaders": [
    {
      "id": 3,
      "person": 3,
      "person_name": "Carol Davis",
      "person_email": "carol.davis@onestep.example.com",
      "start_date": "2022-06-01",
      "end_date": "2023-12-31",
      "is_active": false
    }
  ],
  "total_current": 1,
  "total_historical": 1,
  "total_all_time": 2
}
```

---

## Data Models

### Campus

```json
{
  "id": integer,
  "name": string,
  "code": string,  // Unique, auto-uppercased
  "location": string,
  "group_count": integer,  // Computed field
  "created_at": datetime,
  "updated_at": datetime
}
```

### OrganizationalGroup

```json
{
  "id": integer,
  "name": string,
  "short_name": string,
  "url": string,
  "type": string,  // "research" or "extension"
  "knowledge_area": string,
  "campus": {  // Nested Campus object (read-only)
    "id": integer,
    "name": string,
    "code": string,
    "location": string,
    "group_count": integer
  },
  "current_leaders": [OrganizationalGroupLeadership],
  "members": [Person],
  "initiatives": [Initiative],
  "leader_count": integer,
  "member_count": integer,
  "initiative_count": integer,
  "created_at": datetime,
  "updated_at": datetime
}
```

**Note:** When creating or updating a group, use `campus_id` (integer) instead of the nested `campus` object.

### OrganizationalGroupLeadership

```json
{
  "id": integer,
  "person": integer,
  "person_name": string,
  "person_email": string,
  "start_date": date,
  "end_date": date | null,
  "is_active": boolean
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details (optional)"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `MISSING_PERSON_ID` | person_id is required in request body |
| `PERSON_NOT_FOUND` | Person with given ID does not exist |
| `VALIDATION_ERROR` | Data validation failed |
| `CAMPUS_NOT_FOUND` | Campus with given ID does not exist |
| `PROTECTED_ERROR` | Cannot delete campus with associated groups |
| `CREATION_FAILED` | Failed to create campus or group |
| `UPDATE_FAILED` | Failed to update campus or group |
| `DELETION_FAILED` | Failed to delete campus or group |
| `ADD_LEADER_FAILED` | Failed to add leader |
| `REMOVE_LEADER_FAILED` | Failed to remove leader |

---

## Examples

### Example 1: Create a Campus

```bash
curl -X POST http://localhost:8000/api/campuses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "West Campus",
    "code": "west",
    "location": "999 Research Park Dr, City, State 12345"
  }'
```

### Example 2: List Campuses with Group Counts

```bash
curl -X GET "http://localhost:8000/api/campuses/?ordering=-group_count" \
  -H "Authorization: Bearer <access_token>"
```

### Example 3: Create a Research Group with Campus

```bash
curl -X POST http://localhost:8000/api/groups/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning Research Group",
    "short_name": "ML-RG",
    "url": "https://ml.university.edu",
    "type": "research",
    "knowledge_area": "Artificial Intelligence",
    "campus_id": 1,
    "leader_ids": [1, 2],
    "member_ids": [3, 4, 5]
  }'
```

### Example 4: Search for Groups

```bash
curl -X GET "http://localhost:8000/api/groups/?search=AI&type=research" \
  -H "Authorization: Bearer <access_token>"
```

### Example 5: Add a Leader with Start Date

```bash
curl -X POST http://localhost:8000/api/groups/1/add_leader/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": 5,
    "start_date": "2024-02-01"
  }'
```

### Example 6: Get Leadership History

```bash
curl -X GET http://localhost:8000/api/groups/1/leadership_history/ \
  -H "Authorization: Bearer <access_token>"
```

### Example 7: Filter Groups by Campus and Knowledge Area

```bash
curl -X GET "http://localhost:8000/api/groups/?campus_id=1&knowledge_area=Computer%20Science&ordering=-created_at" \
  -H "Authorization: Bearer <access_token>"
```

### Example 8: Update Group Campus

```bash
curl -X PATCH http://localhost:8000/api/groups/5/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "campus_id": 2
  }'
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Pagination is applied to list endpoints with default page_size of 10
- Campus `code` is automatically converted to uppercase
- The `short_name` + `campus_id` combination must be unique across all groups
- Cannot delete a Campus that has associated groups (PROTECT constraint)
- Leadership history is automatically maintained when adding/removing leaders
- Deleting a group will cascade delete all leadership relationships
- Members and initiatives use many-to-many relationships and are not deleted when a group is deleted
- When creating/updating groups, use `campus_id` (integer); responses include nested `campus` object
