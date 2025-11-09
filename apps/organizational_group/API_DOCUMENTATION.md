# Organizational Group API Documentation

## Overview

The Organizational Group API provides endpoints for managing university research and organizational groups. Groups can have leaders (with historical tracking), members, and associations with initiatives.

**Note:** This API uses the endpoint `/api/groups/` for backward compatibility, but the Django app is named `organizational_group` and the model is named `OrganizationalGroup` to avoid conflicts with Django's built-in `Group` model from `django.contrib.auth`.

## Base URL

```
/api/groups/
```

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. List Groups

**GET** `/api/groups/`

Retrieve a paginated list of all groups with comprehensive filtering, searching, and ordering capabilities.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by group type (`research` or `extension`) |
| `campus` | string | Filter by campus name |
| `knowledge_area` | string | Filter by knowledge area |
| `search` | string | Search across name and short_name |
| `ordering` | string | Order results by field (prefix with `-` for descending). Options: `name`, `short_name`, `type`, `campus`, `created_at`, `updated_at` |
| `page` | integer | Page number for pagination |
| `page_size` | integer | Number of results per page (default: 10, max: 100) |

#### Example Request

```bash
GET /api/groups/?type=research&campus=Main%20Campus&ordering=-created_at
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
      "campus": "Main Campus",
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

### 2. Create Group

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
  "campus": "Main Campus",
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
| `campus` | string | Yes | University campus (max 200 characters) |
| `leader_ids` | array | No | List of person IDs to add as leaders |
| `member_ids` | array | No | List of person IDs to add as members |
| `initiative_ids` | array | No | List of initiative IDs to associate |

#### Validation Rules

- `name` and `short_name` are required
- `short_name` + `campus` combination must be unique
- `type` must be either `research` or `extension`
- `url` must be a valid URL format (if provided)

#### Example Response

```json
{
  "id": 6,
  "name": "Quantum Computing Lab",
  "short_name": "QC-LAB",
  "url": "https://quantum.university.edu",
  "type": "research",
  "knowledge_area": "Physics",
  "campus": "Main Campus",
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
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `409 Conflict` - Duplicate short_name + campus combination

---

### 3. Get Group Details

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
  "campus": "Main Campus",
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

### 4. Update Group (Full)

**PUT** `/api/groups/{id}/`

Perform a full update of a group. All fields must be provided.

#### Request Body

Same as Create Group, all fields required.

#### Status Codes

- `200 OK` - Group successfully updated
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group not found

---

### 5. Update Group (Partial)

**PATCH** `/api/groups/{id}/`

Perform a partial update of a group. Only provided fields will be updated.

#### Example Request

```json
{
  "url": "https://new-url.university.edu",
  "knowledge_area": "Advanced Computer Science"
}
```

#### Status Codes

- `200 OK` - Group successfully updated
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group not found

---

### 6. Delete Group

**DELETE** `/api/groups/{id}/`

Delete a group. This will also remove all leadership relationships, member associations, and initiative associations.

#### Status Codes

- `204 No Content` - Group successfully deleted
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Group not found

---

## Custom Actions

### 7. Get Current Leaders

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

### 8. Add Leader

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

### 9. Remove Leader

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

### 10. Get Leadership History

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

### OrganizationalGroup

```json
{
  "id": integer,
  "name": string,
  "short_name": string,
  "url": string,
  "type": string,  // "research" or "extension"
  "knowledge_area": string,
  "campus": string,
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
| `CREATION_FAILED` | Failed to create group |
| `UPDATE_FAILED` | Failed to update group |
| `DELETION_FAILED` | Failed to delete group |
| `ADD_LEADER_FAILED` | Failed to add leader |
| `REMOVE_LEADER_FAILED` | Failed to remove leader |

---

## Examples

### Example 1: Create a Research Group with Leaders

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
    "campus": "Main Campus",
    "leader_ids": [1, 2],
    "member_ids": [3, 4, 5]
  }'
```

### Example 2: Search for Groups

```bash
curl -X GET "http://localhost:8000/api/groups/?search=AI&type=research" \
  -H "Authorization: Bearer <access_token>"
```

### Example 3: Add a Leader with Start Date

```bash
curl -X POST http://localhost:8000/api/groups/1/add_leader/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": 5,
    "start_date": "2024-02-01"
  }'
```

### Example 4: Get Leadership History

```bash
curl -X GET http://localhost:8000/api/groups/1/leadership_history/ \
  -H "Authorization: Bearer <access_token>"
```

### Example 5: Filter Groups by Campus and Knowledge Area

```bash
curl -X GET "http://localhost:8000/api/groups/?campus=Main%20Campus&knowledge_area=Computer%20Science&ordering=-created_at" \
  -H "Authorization: Bearer <access_token>"
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Pagination is applied to list endpoints with default page_size of 10
- The `short_name` + `campus` combination must be unique across all groups
- Leadership history is automatically maintained when adding/removing leaders
- Deleting a group will cascade delete all leadership relationships
- Members and initiatives use many-to-many relationships and are not deleted when a group is deleted
