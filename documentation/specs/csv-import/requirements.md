# Requirements Document

## Introduction

This feature enables importing research group data from CSV files into the OneStep system through a Django management command and admin interface. The import process will create Campus, Person, and OrganizationalGroup records from CSV data, avoiding duplicate entries and handling data validation.

## Glossary

- **CSV File**: Comma-separated values file containing research group data
- **Import Command**: Django management command that processes CSV files
- **System**: The OneStep Django application
- **Admin Interface**: Django's built-in administrative interface
- **Research Group**: An OrganizationalGroup with type='research'
- **Deduplication**: Process of avoiding duplicate records based on unique identifiers
- **KnowledgeArea**: A distinct academic or research domain entity that categorizes organizational groups

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to import research groups from a CSV file via management command, so that I can bulk load data into the system

#### Acceptance Criteria

1. THE System SHALL provide a Django management command for importing CSV files
2. THE Command SHALL accept a file path parameter for the CSV file location
3. THE Command SHALL parse CSV files with headers: Sigla, Nome, repositorio, Site, AreaConhecimento, Unidade, Lideres
4. THE Command SHALL display progress information during import
5. THE Command SHALL display a summary report after import completion

### Requirement 2

**User Story:** As a system administrator, I want the import process to create Campus records from unique campus names, so that campus data is normalized

#### Acceptance Criteria

1. THE System SHALL extract unique campus names from the Unidade column
2. WHEN a campus name does not exist in the database, THE System SHALL create a new Campus record
3. WHEN a campus name exists in the database, THE System SHALL reuse the existing Campus record
4. THE System SHALL generate campus codes from campus names using uppercase letters with spaces removed
5. WHEN the Unidade column is empty, THE System SHALL skip the row and log a validation error

### Requirement 3

**User Story:** As a system administrator, I want the import process to create Person records from leader information, so that people data is available for leadership assignments

#### Acceptance Criteria

1. THE System SHALL parse leader information from the Lideres column
2. THE System SHALL extract person names and email addresses from leader data
3. THE System SHALL create Person records for new people
4. THE System SHALL reuse existing Person records when email already exists
5. THE System SHALL handle multiple leaders per group separated by commas

### Requirement 4

**User Story:** As a system administrator, I want the import process to create KnowledgeArea records from knowledge area values, so that knowledge areas are normalized

#### Acceptance Criteria

1. THE System SHALL extract knowledge area values from the AreaConhecimento column
2. WHEN a knowledge area value does not exist in the database, THE System SHALL create a new KnowledgeArea record
3. WHEN a knowledge area value exists in the database using case-insensitive lookup, THE System SHALL reuse the existing KnowledgeArea record
4. THE System SHALL strip whitespace from knowledge area values before lookup or creation
5. WHEN the AreaConhecimento column is empty, THE System SHALL skip the row and log a validation error

### Requirement 5

**User Story:** As a system administrator, I want the import process to create OrganizationalGroup records with relationships, so that research groups are fully configured

#### Acceptance Criteria

1. THE System SHALL create OrganizationalGroup records with type set to 'research'
2. THE System SHALL map the Sigla column to short_name, Nome column to name, and repositorio column to url
3. THE System SHALL assign the Campus foreign key relationship using the campus created from the Unidade column
4. THE System SHALL assign the KnowledgeArea foreign key relationship using the knowledge area created from the AreaConhecimento column
5. THE System SHALL create OrganizationalGroupLeadership records linking each Person to the OrganizationalGroup
6. WHEN an OrganizationalGroup with the same short_name and campus combination exists, THE System SHALL skip creation and log the duplicate

### Requirement 6

**User Story:** As a system administrator, I want the import process to validate data before creating records, so that invalid data does not corrupt the database

#### Acceptance Criteria

1. THE System SHALL validate that the Nome, Unidade, and AreaConhecimento columns contain non-empty values
2. WHEN leader email addresses are present, THE System SHALL validate they match the format name@domain.extension
3. WHEN repository or site URLs are present, THE System SHALL validate they match the format http://domain or https://domain
4. WHEN validation fails, THE System SHALL log an error message including the row number and field name
5. WHEN a row fails validation, THE System SHALL skip that row and continue processing the next row

### Requirement 7

**User Story:** As a system administrator, I want the import process to handle errors without stopping, so that partial failures do not prevent successful imports

#### Acceptance Criteria

1. THE System SHALL wrap each row's database operations in a separate transaction
2. WHEN an error occurs, THE System SHALL log the error message with the row number and row data
3. WHEN a row fails processing, THE System SHALL continue processing the next row
4. THE System SHALL include total error count in the summary report displayed after import completion
5. WHEN an error occurs during row processing, THE System SHALL rollback all database changes for that row only

### Requirement 8

**User Story:** As a system administrator, I want to import CSV files through the Django admin interface, so that I can upload files without command line access

#### Acceptance Criteria

1. THE Admin Interface SHALL provide a custom admin action for CSV import
2. THE Admin Interface SHALL display a file upload form
3. THE Admin Interface SHALL process uploaded CSV files
4. THE Admin Interface SHALL display import results with success and error counts
5. THE Admin Interface SHALL show detailed error messages for failed rows


