# Requirements Document

## Introduction

This feature converts the `campus` field in the OrganizationalGroup model from a simple CharField to a proper Campus model with its own database table, API endpoints, and admin interface. This change will enable better campus data management, validation, and relationships across the OneStep system.

## Glossary

- **Campus**: A physical university location where organizational groups operate
- **OrganizationalGroup**: A university research or organizational group that operates on a specific campus
- **System**: The OneStep Django application
- **Admin Interface**: Django's built-in administrative interface
- **API**: REST API endpoints provided by Django REST Framework
- **Migration**: Database schema change managed by Django's migration system

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to manage campuses as separate entities, so that I can maintain consistent campus data across all organizational groups

#### Acceptance Criteria

1. THE System SHALL create a Campus model with name, code, and location fields
2. THE Campus model SHALL enforce unique campus codes across all campus records
3. THE Campus model SHALL provide a string representation using the campus name
4. THE System SHALL create database indexes on the name and code fields for query performance
5. THE System SHALL validate that campus name and code are not empty strings

### Requirement 2

**User Story:** As a system administrator, I want to access campus management through the Django admin interface, so that I can create, update, and delete campus records

#### Acceptance Criteria

1. THE System SHALL register the Campus model in the Django admin interface
2. THE Admin Interface SHALL display campus name, code, and location in the list view
3. THE Admin Interface SHALL enable filtering by name and code
4. THE Admin Interface SHALL enable searching by name, code, and location
5. THE Admin Interface SHALL display the count of organizational groups associated with each campus

### Requirement 3

**User Story:** As an API consumer, I want to access campus data through REST API endpoints, so that I can integrate campus information into external systems

#### Acceptance Criteria

1. THE System SHALL provide a REST API endpoint at /api/campuses/ for listing all campuses
2. THE System SHALL provide a REST API endpoint for creating new campus records
3. THE System SHALL provide a REST API endpoint for retrieving individual campus details
4. THE System SHALL provide a REST API endpoint for updating campus records
5. THE System SHALL provide a REST API endpoint for deleting campus records
6. THE API SHALL include filtering capabilities by name and code
7. THE API SHALL include search functionality across name, code, and location fields
8. THE API SHALL return the count of organizational groups associated with each campus

### Requirement 4

**User Story:** As a database administrator, I want to migrate existing campus data from the CharField to the new Campus model, so that no data is lost during the transition

#### Acceptance Criteria

1. THE System SHALL create a data migration that extracts unique campus values from existing OrganizationalGroup records
2. THE Migration SHALL create Campus records for each unique campus value
3. THE Migration SHALL update OrganizationalGroup records to reference the new Campus foreign key
4. THE Migration SHALL preserve all existing campus associations
5. IF a campus value is empty or null, THEN THE Migration SHALL handle it gracefully without failing

### Requirement 5

**User Story:** As a developer, I want the OrganizationalGroup model to use a foreign key relationship to Campus, so that campus data is normalized and consistent

#### Acceptance Criteria

1. THE System SHALL replace the campus CharField with a ForeignKey to the Campus model
2. THE OrganizationalGroup model SHALL enforce that campus is a required field
3. WHEN an OrganizationalGroup is deleted, THEN THE System SHALL preserve the Campus record
4. THE System SHALL update the unique constraint to use campus foreign key instead of campus CharField
5. THE System SHALL maintain the database index on the campus foreign key for query performance

### Requirement 6

**User Story:** As an API consumer, I want organizational group API responses to include campus details, so that I can access campus information without additional API calls

#### Acceptance Criteria

1. THE OrganizationalGroup API SHALL include nested campus data in list responses
2. THE OrganizationalGroup API SHALL include nested campus data in detail responses
3. THE Campus data SHALL include id, name, code, and location fields
4. THE OrganizationalGroup API SHALL accept campus_id when creating new groups
5. THE OrganizationalGroup API SHALL accept campus_id when updating existing groups
6. THE OrganizationalGroup API SHALL enable filtering by campus_id

### Requirement 7

**User Story:** As a system administrator, I want the admin interface to display campus information clearly, so that I can easily identify which campus each organizational group belongs to

#### Acceptance Criteria

1. THE OrganizationalGroup admin interface SHALL display campus name in the list view
2. THE OrganizationalGroup admin interface SHALL enable filtering by campus
3. THE OrganizationalGroup admin interface SHALL use a select dropdown for campus selection in forms
4. THE OrganizationalGroup admin interface SHALL display campus code alongside campus name in dropdowns
5. THE System SHALL update search functionality to work with the new Campus relationship

### Requirement 8

**User Story:** As a developer, I want comprehensive tests for the Campus model and its integration, so that I can ensure the feature works correctly

#### Acceptance Criteria

1. THE System SHALL include unit tests for Campus model creation and validation
2. THE System SHALL include tests for Campus model string representation
3. THE System SHALL include tests for Campus uniqueness constraints
4. THE System SHALL include API tests for all Campus CRUD operations
5. THE System SHALL include tests for OrganizationalGroup creation with Campus foreign key
6. THE System SHALL include tests for filtering and searching campuses
7. THE System SHALL include serializer tests for nested campus data in OrganizationalGroup responses
