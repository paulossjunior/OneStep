# Requirements Document - Scholarship CSV Import

## Introduction

This document specifies the requirements for implementing a CSV import feature for the scholarship management system. The feature will allow administrators to bulk import scholarship data from CSV files with automatic field mapping and validation.

## Glossary

- **CSV Import System**: The system component responsible for reading, parsing, validating, and importing scholarship data from CSV files
- **Field Mapping**: The process of translating CSV column names to database model fields
- **Validation Engine**: The component that validates imported data against business rules before database insertion
- **Import Report**: A summary document showing successful imports, errors, and warnings
- **Dry Run**: A validation-only mode that checks data without persisting to the database
- **Admin Interface**: The Django admin interface where CSV import functionality is accessible

## Requirements

### Requirement 1: CSV File Upload and Parsing

**User Story:** As an administrator, I want to upload a CSV file containing scholarship data, so that I can bulk import multiple scholarships at once.

#### Acceptance Criteria

1. WHEN the administrator accesses the scholarship admin interface, THE CSV Import System SHALL display an "Import from CSV" action button
2. WHEN the administrator clicks the import button, THE CSV Import System SHALL present a file upload form accepting CSV files
3. WHEN a CSV file is uploaded, THE CSV Import System SHALL parse the file using UTF-8 encoding with comma delimiters
4. IF the CSV file cannot be parsed, THEN THE CSV Import System SHALL display an error message indicating the parsing failure
5. WHEN the CSV file is successfully parsed, THE CSV Import System SHALL extract all rows and columns for processing

### Requirement 2: Field Mapping Configuration

**User Story:** As an administrator, I want the system to automatically map CSV columns to scholarship fields, so that I don't need to manually configure mappings for standard formats.

#### Acceptance Criteria

1. THE CSV Import System SHALL maintain a predefined mapping configuration for standard CSV formats
2. THE CSV Import System SHALL map the CSV column "Valor" to the Scholarship field "value"
3. THE CSV Import System SHALL map the CSV column "Programa" to the ScholarshipType field "name"
4. THE CSV Import System SHALL map the CSV column "CampusExecucao" to the Campus field "name"
5. THE CSV Import System SHALL map the CSV column "Orientador" to the supervisor Person field "name"
6. THE CSV Import System SHALL map the CSV column "Inicio" to the Scholarship field "start_date"
7. THE CSV Import System SHALL map the CSV column "Fim" to the Scholarship field "end_date"
8. THE CSV Import System SHALL map the CSV column "Orientado" to the student Person field "name"
9. WHERE custom mapping is required, THE CSV Import System SHALL allow administrators to override default mappings

### Requirement 3: Data Validation

**User Story:** As an administrator, I want the system to validate imported data before saving, so that I can identify and fix errors without corrupting the database.

#### Acceptance Criteria

1. WHEN processing each CSV row, THE Validation Engine SHALL validate all required fields are present
2. THE Validation Engine SHALL validate that "Valor" contains a valid decimal number greater than zero
3. THE Validation Engine SHALL validate that "Inicio" and "Fim" contain valid dates in DD-MM-YY format
4. THE Validation Engine SHALL validate that end date is after or equal to start date
5. THE Validation Engine SHALL validate that the scholarship type exists or can be created
6. THE Validation Engine SHALL validate that the campus exists in the database
7. THE Validation Engine SHALL validate that supervisor and student persons exist or can be created
8. IF validation fails for any row, THEN THE Validation Engine SHALL record the error with row number and field details
9. THE Validation Engine SHALL continue processing remaining rows after encountering errors

### Requirement 4: Foreign Key Resolution

**User Story:** As an administrator, I want the system to automatically find or create related entities, so that I don't need to manually create all persons, campuses, and types before importing.

#### Acceptance Criteria

1. WHEN a scholarship type name is encountered, THE CSV Import System SHALL search for an existing ScholarshipType by name
2. IF the scholarship type does not exist, THEN THE CSV Import System SHALL create a new ScholarshipType with the provided name
3. WHEN a campus name is encountered, THE CSV Import System SHALL search for an existing Campus by name
4. IF the campus does not exist, THEN THE CSV Import System SHALL record an error requiring manual campus creation
5. WHEN a person name is encountered, THE CSV Import System SHALL search for an existing Person by name
6. IF the person does not exist, THEN THE CSV Import System SHALL create a new Person with the provided name and email if available
7. THE CSV Import System SHALL use email addresses from "OrientadorEmail" and "OrientadoEmail" columns when creating persons

### Requirement 5: Dry Run Mode

**User Story:** As an administrator, I want to preview import results without saving data, so that I can verify the import will work correctly before committing changes.

#### Acceptance Criteria

1. THE CSV Import System SHALL provide a "Dry Run" checkbox option on the import form
2. WHEN dry run mode is enabled, THE CSV Import System SHALL perform all validation steps
3. WHEN dry run mode is enabled, THE CSV Import System SHALL NOT persist any data to the database
4. WHEN dry run mode is enabled, THE CSV Import System SHALL generate a complete import report showing what would be imported
5. THE CSV Import System SHALL display the number of scholarships that would be created in dry run mode

### Requirement 6: Import Report Generation

**User Story:** As an administrator, I want to see a detailed report after import, so that I can understand what was imported and identify any errors.

#### Acceptance Criteria

1. WHEN the import process completes, THE CSV Import System SHALL generate an Import Report
2. THE Import Report SHALL display the total number of rows processed
3. THE Import Report SHALL display the number of scholarships successfully imported
4. THE Import Report SHALL display the number of rows with errors
5. THE Import Report SHALL list each error with row number, field name, and error description
6. THE Import Report SHALL display the number of new scholarship types created
7. THE Import Report SHALL display the number of new persons created
8. THE Import Report SHALL provide a downloadable error log for rows that failed validation

### Requirement 7: Error Handling and Recovery

**User Story:** As an administrator, I want the system to handle errors gracefully, so that partial failures don't corrupt the database or lose valid data.

#### Acceptance Criteria

1. THE CSV Import System SHALL use database transactions to ensure atomicity
2. IF any critical error occurs during import, THEN THE CSV Import System SHALL rollback all changes
3. THE CSV Import System SHALL allow administrators to choose between "stop on first error" or "continue on error" modes
4. WHEN continuing on error, THE CSV Import System SHALL skip invalid rows and import valid ones
5. THE CSV Import System SHALL log all errors with sufficient detail for troubleshooting

### Requirement 8: Date Format Handling

**User Story:** As an administrator, I want the system to handle various date formats, so that I can import data from different sources without reformatting.

#### Acceptance Criteria

1. THE CSV Import System SHALL support date format DD-MM-YY (e.g., "01-09-25")
2. THE CSV Import System SHALL support date format DD/MM/YYYY (e.g., "01/09/2025")
3. THE CSV Import System SHALL support date format YYYY-MM-DD (e.g., "2025-09-01")
4. WHEN parsing dates, THE CSV Import System SHALL interpret two-digit years 00-49 as 2000-2049
5. WHEN parsing dates, THE CSV Import System SHALL interpret two-digit years 50-99 as 1950-1999
6. IF a date cannot be parsed, THEN THE CSV Import System SHALL record a validation error with the original value

### Requirement 9: Performance and Scalability

**User Story:** As an administrator, I want to import large CSV files efficiently, so that I can process hundreds of scholarships without timeout errors.

#### Acceptance Criteria

1. THE CSV Import System SHALL process CSV files with up to 1000 rows within 60 seconds
2. THE CSV Import System SHALL use bulk insert operations to minimize database queries
3. THE CSV Import System SHALL display a progress indicator during import processing
4. THE CSV Import System SHALL process imports asynchronously to avoid HTTP timeout errors
5. WHEN processing large files, THE CSV Import System SHALL provide status updates every 100 rows

### Requirement 10: Security and Permissions

**User Story:** As a system administrator, I want to restrict CSV import access to authorized users, so that unauthorized users cannot bulk modify scholarship data.

#### Acceptance Criteria

1. THE CSV Import System SHALL require Django admin authentication
2. THE CSV Import System SHALL restrict import functionality to users with "add_scholarship" permission
3. THE CSV Import System SHALL log all import attempts with username and timestamp
4. THE CSV Import System SHALL validate file size does not exceed 10MB
5. THE CSV Import System SHALL reject files with extensions other than .csv
