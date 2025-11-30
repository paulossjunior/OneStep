# Scholarship Management API Documentation

## Overview

The Scholarship Management API provides comprehensive REST endpoints for managing scholarships and scholarship types. The API supports full CRUD operations, advanced filtering, searching, and statistical analysis.

## API Documentation Access

### Interactive Documentation

The API documentation is available through multiple interfaces:

1. **Swagger UI** (Interactive API Explorer)
   - URL: `http://localhost:8000/api/docs/`
   - Features: Interactive testing, request/response examples, authentication support

2. **ReDoc** (Clean Documentation)
   - URL: `http://localhost:8000/api/redoc/`
   - Features: Clean, responsive documentation with search

3. **OpenAPI Schema** (Machine-readable)
   - URL: `http://localhost:8000/api/schema/`
   - Format: OpenAPI 3.0 YAML/JSON

## Authentication

All scholarship endpoints require authentication. The API supports multiple authentication methods:

- **JWT Authentication** (Recommended for API clients)
  - Obtain token: `POST /api/v1/auth/token/`
  - Use in header: `Authorization: Bearer <token>`
  
- **Session Authentication** (For browser-based access)
  - Login through Django admin or custom login endpoint
  
- **Basic Authentication** (For development/testing)
  - Use HTTP Basic Auth with username and password

## Endpoints

### Scholarship Types

#### List Scholarship Types
```
GET /api/v1/scholarship-types/
```

**Query Parameters:**
- `is_active` (boolean): Filter by active status
- `search` (string): Search by name, code, or description
- `ordering` (string): Order by name, code, is_active, created_at, updated_at
- `page` (integer): Page number for pagination
- `page_size` (integer): Number of items per page (max 100)

**Response:** Paginated list of scholarship types with scholarship count

#### Create Scholarship Type
```
POST /api/v1/scholarship-types/
```

**Request Body:**
```json
{
  "name": "Research Scholarship",
  "code": "research",
  "description": "Scholarships for research activities",
  "is_active": true
}
```

#### Get Scholarship Type Details
```
GET /api/v1/scholarship-types/{id}/
```

**Response:** Detailed scholarship type information including scholarship count

#### Update Scholarship Type
```
PUT /api/v1/scholarship-types/{id}/
PATCH /api/v1/scholarship-types/{id}/
```

#### Delete Scholarship Type
```
DELETE /api/v1/scholarship-types/{id}/
```

**Note:** Cannot delete scholarship types that have associated scholarships.

---

### Scholarships

#### List Scholarships
```
GET /api/v1/scholarships/
```

**Query Parameters:**

*Filtering:*
- `type` (integer): Filter by scholarship type ID
- `campus` (integer): Filter by campus ID
- `supervisor` (integer): Filter by supervisor (Person) ID
- `student` (integer): Filter by student (Person) ID
- `sponsor` (integer): Filter by sponsor (Organization) ID
- `initiative` (integer): Filter by initiative ID
- `is_active` (boolean): Filter by active status
- `start_date_after` (date): Scholarships starting after date (YYYY-MM-DD)
- `start_date_before` (date): Scholarships starting before date (YYYY-MM-DD)
- `end_date_after` (date): Scholarships ending after date (YYYY-MM-DD)
- `end_date_before` (date): Scholarships ending before date (YYYY-MM-DD)
- `value_min` (decimal): Minimum monthly value
- `value_max` (decimal): Maximum monthly value

*Search:*
- `search` (string): Search by title, student name, supervisor name, or sponsor name

*Ordering:*
- `ordering` (string): Order by start_date, end_date, value, student__name, supervisor__name, created_at, updated_at
  - Prefix with `-` for descending order (e.g., `-start_date`)

*Pagination:*
- `page` (integer): Page number
- `page_size` (integer): Items per page (max 100)

**Response:** Paginated list of scholarships with nested related objects

#### Create Scholarship
```
POST /api/v1/scholarships/
```

**Request Body:**
```json
{
  "title": "Research Scholarship - Machine Learning",
  "type": 1,
  "campus": 1,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "supervisor": 5,
  "student": 10,
  "value": "1500.00",
  "sponsor": 2,
  "initiative": 3
}
```

**Required Fields:**
- `title`: Scholarship title
- `type`: Scholarship type ID
- `campus`: Campus ID
- `start_date`: Start date (YYYY-MM-DD)
- `supervisor`: Supervisor person ID
- `student`: Student person ID
- `value`: Monthly value (decimal, must be > 0)

**Optional Fields:**
- `end_date`: End date (YYYY-MM-DD)
- `sponsor`: Sponsor organization ID
- `initiative`: Initiative ID

**Validation Rules:**
- Value must be greater than zero
- End date must be after or equal to start date
- Start date cannot be more than 10 years in the future
- End date cannot be more than 10 years after start date
- Supervisor and student must be different people
- Student cannot have overlapping scholarships

#### Get Scholarship Details
```
GET /api/v1/scholarships/{id}/
```

**Response:** Detailed scholarship information including:
- All basic fields
- Nested type, campus, supervisor, student, sponsor, initiative details
- Computed properties: duration_months, is_active, total_value

#### Update Scholarship
```
PUT /api/v1/scholarships/{id}/
PATCH /api/v1/scholarships/{id}/
```

**Request Body:** Same as create, all validations apply

#### Delete Scholarship
```
DELETE /api/v1/scholarships/{id}/
```

#### Get Scholarship Statistics
```
GET /api/v1/scholarships/statistics/
```

**Response:**
```json
{
  "total_count": 150,
  "active_count": 45,
  "total_monthly_value": "67500.00",
  "by_type": [
    {"type__name": "Research", "count": 80},
    {"type__name": "Extension", "count": 40}
  ],
  "by_campus": [
    {"campus__name": "Main Campus", "count": 100},
    {"campus__name": "Branch Campus", "count": 50}
  ],
  "top_supervisors": [
    {"supervisor__name": "Dr. João Silva", "count": 15}
  ],
  "top_sponsors": [
    {"sponsor__name": "FAPES", "count": 30}
  ]
}
```

**Note:** All filters from the list endpoint apply to statistics.

## Response Format

### Success Response
```json
{
  "id": 1,
  "title": "Research Scholarship - Machine Learning",
  "type": {
    "id": 1,
    "name": "Research Scholarship",
    "code": "research"
  },
  "campus": {
    "id": 1,
    "name": "Main Campus",
    "code": "MC"
  },
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "supervisor": {
    "id": 5,
    "name": "Dr. João Silva",
    "email": "joao@example.com"
  },
  "student": {
    "id": 10,
    "name": "Maria Santos",
    "email": "maria@example.com"
  },
  "value": "1500.00",
  "sponsor": {
    "id": 2,
    "name": "FAPES"
  },
  "initiative": {
    "id": 3,
    "name": "AI Research Project",
    "type": "project"
  },
  "duration_months": 12,
  "is_active": true,
  "total_value": "18000.00",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z"
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Failed to create scholarship",
    "details": "End date must be after or equal to start date."
  }
}
```

### Validation Error Response
```json
{
  "field_name": [
    "Error message for this field"
  ]
}
```

## Pagination

All list endpoints return paginated results:

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/scholarships/?page=2",
  "previous": null,
  "results": [...]
}
```

## Example Usage

### Using cURL

**Get all active scholarships:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/scholarships/?is_active=true"
```

**Create a scholarship:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research Scholarship",
    "type": 1,
    "campus": 1,
    "start_date": "2024-01-01",
    "supervisor": 5,
    "student": 10,
    "value": "1500.00"
  }' \
  "http://localhost:8000/api/v1/scholarships/"
```

**Search scholarships:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/scholarships/?search=machine+learning"
```

**Filter by date range:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/scholarships/?start_date_after=2024-01-01&start_date_before=2024-12-31"
```

### Using Python (requests)

```python
import requests

# Obtain token
response = requests.post(
    'http://localhost:8000/api/v1/auth/token/',
    json={'username': 'admin', 'password': 'password'}
)
token = response.json()['access']

# Set headers
headers = {'Authorization': f'Bearer {token}'}

# List scholarships
response = requests.get(
    'http://localhost:8000/api/v1/scholarships/',
    headers=headers,
    params={'is_active': True, 'page_size': 50}
)
scholarships = response.json()

# Create scholarship
new_scholarship = {
    'title': 'Research Scholarship',
    'type': 1,
    'campus': 1,
    'start_date': '2024-01-01',
    'supervisor': 5,
    'student': 10,
    'value': '1500.00'
}
response = requests.post(
    'http://localhost:8000/api/v1/scholarships/',
    headers=headers,
    json=new_scholarship
)
created = response.json()

# Get statistics
response = requests.get(
    'http://localhost:8000/api/v1/scholarships/statistics/',
    headers=headers
)
stats = response.json()
```

## Rate Limiting

- **Anonymous users:** 100 requests per hour
- **Authenticated users:** 1000 requests per hour

## Requirements Mapping

This API implementation satisfies the following requirements:

- **Requirement 6.1:** REST API endpoints for scholarship CRUD operations
- **Requirement 6.2:** Scholarship type, campus, and initiative details in API responses
- **Requirement 6.3:** Student and supervisor basic information in API responses
- **Requirement 6.4:** Sponsor information in API responses
- **Requirement 6.5:** Filtering scholarships by type, campus, initiative, date range, supervisor, student, and sponsor

## Additional Resources

- **Django REST Framework Documentation:** https://www.django-rest-framework.org/
- **OpenAPI Specification:** https://swagger.io/specification/
- **drf-spectacular Documentation:** https://drf-spectacular.readthedocs.io/

## Support

For issues or questions about the API:
1. Check the interactive documentation at `/api/docs/`
2. Review the OpenAPI schema at `/api/schema/`
3. Contact the development team
