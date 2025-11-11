# Requirements Document

## Introduction

This feature implements a scholarship management system to track academic scholarships, including their types, duration, financial details, and associated people (supervisors and students) and organizations (sponsors).

## Glossary

- **Scholarship**: A financial award given to a student to support their academic studies or research
- **ScholarshipType**: A category that classifies scholarships (e.g., Research, Extension, Teaching, Innovation)
- **Title**: A descriptive name for the scholarship
- **Campus**: The physical location where the scholarship is executed
- **Student**: A Person who receives the scholarship
- **Supervisor**: A Person who supervises the student receiving the scholarship
- **Sponsor**: An Organization that provides funding for the scholarship
- **Initiative**: A research project, program, or event that the scholarship is associated with
- **Value**: The monthly monetary amount of the scholarship in Brazilian Real (BRL)
- **System**: The OneStep scholarship management application

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to manage scholarship types, so that I can categorize scholarships appropriately

#### Acceptance Criteria

1. THE System SHALL provide a ScholarshipType entity with name, code, and description fields
2. THE System SHALL ensure ScholarshipType names are unique
3. THE System SHALL ensure ScholarshipType codes are unique
4. THE System SHALL allow ScholarshipTypes to be activated or deactivated
5. THE System SHALL display ScholarshipTypes in alphabetical order by name

### Requirement 2

**User Story:** As a system administrator, I want to create and manage scholarships, so that I can track all scholarship awards in the system

#### Acceptance Criteria

1. THE System SHALL provide a Scholarship entity with type, title, campus, start_date, end_date, supervisor, student, value, sponsor, and initiative fields
2. THE System SHALL require type, title, campus, start_date, supervisor, student, and value fields for scholarship creation
3. THE System SHALL allow end_date, sponsor, and initiative fields to be optional
4. THE System SHALL validate that end_date is after or equal to start_date when both are provided
5. THE System SHALL store monetary values with proper decimal precision (two decimal places)

### Requirement 3

**User Story:** As a system administrator, I want to associate scholarships with people, so that I can track supervisors and students

#### Acceptance Criteria

1. THE System SHALL link each scholarship to exactly one supervisor (Person)
2. THE System SHALL link each scholarship to exactly one student (Person)
3. THE System SHALL prevent deletion of a Person who is referenced as a supervisor in active scholarships
4. THE System SHALL prevent deletion of a Person who is referenced as a student in active scholarships
5. THE System SHALL provide reverse relationships to query all scholarships supervised by a person and all scholarships received by a person

### Requirement 4

**User Story:** As a system administrator, I want to associate scholarships with sponsor organizations and initiatives, so that I can track funding sources and related projects

#### Acceptance Criteria

1. THE System SHALL allow each scholarship to have zero or one sponsor Organization
2. WHEN a sponsor Organization is deleted, THE System SHALL set the scholarship sponsor field to null
3. THE System SHALL allow each scholarship to be associated with zero or one Initiative
4. WHEN an Initiative is deleted, THE System SHALL set the scholarship initiative field to null
5. THE System SHALL provide reverse relationships to query all scholarships sponsored by an organization and all scholarships related to an initiative
6. THE System SHALL display sponsor and initiative information in scholarship details
7. THE System SHALL allow filtering scholarships by sponsor and initiative

### Requirement 4.1

**User Story:** As a system administrator, I want to associate scholarships with campus locations, so that I can track scholarship distribution across campuses

#### Acceptance Criteria

1. THE System SHALL link each scholarship to exactly one Campus
2. THE System SHALL prevent deletion of a Campus that has associated scholarships
3. THE System SHALL provide a reverse relationship to query all scholarships at a campus
4. THE System SHALL display campus information in scholarship details
5. THE System SHALL allow filtering scholarships by campus

### Requirement 5

**User Story:** As a system administrator, I want to view scholarship information in the admin interface, so that I can manage scholarships efficiently

#### Acceptance Criteria

1. THE System SHALL display scholarships in a list view with title, type, student, supervisor, campus, value, start_date, and end_date
2. THE System SHALL allow filtering scholarships by type, supervisor, student, sponsor, campus, initiative, and date ranges
3. THE System SHALL allow searching scholarships by title, student name, supervisor name, and sponsor name
4. THE System SHALL display scholarship duration in months
5. THE System SHALL highlight active scholarships (current date between start_date and end_date)

### Requirement 6

**User Story:** As a system administrator, I want to access scholarship data via REST API, so that I can integrate with other systems

#### Acceptance Criteria

1. THE System SHALL provide REST API endpoints for scholarship CRUD operations
2. THE System SHALL include scholarship type, campus, and initiative details in API responses
3. THE System SHALL include student and supervisor basic information in API responses
4. THE System SHALL include sponsor information in API responses
5. THE System SHALL support filtering scholarships by type, campus, initiative, date range, supervisor, student, and sponsor via API

### Requirement 7

**User Story:** As a system administrator, I want to validate scholarship data, so that I can ensure data integrity

#### Acceptance Criteria

1. THE System SHALL validate that scholarship value is greater than zero
2. THE System SHALL validate that start_date is not in the far future (within 10 years)
3. THE System SHALL validate that end_date is not more than 10 years after start_date
4. THE System SHALL prevent creating scholarships with the same student and overlapping date ranges
5. THE System SHALL display clear error messages for validation failures

### Requirement 8

**User Story:** As a system administrator, I want to track scholarship statistics, so that I can analyze scholarship distribution

#### Acceptance Criteria

1. THE System SHALL calculate total scholarship value by type
2. THE System SHALL count active scholarships
3. THE System SHALL count scholarships by supervisor
4. THE System SHALL count scholarships by sponsor
5. THE System SHALL count scholarships by campus
6. THE System SHALL count scholarships by initiative
7. THE System SHALL display scholarship statistics in the admin dashboard
