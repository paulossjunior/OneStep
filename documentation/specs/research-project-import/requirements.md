# Requirements Document

## Introduction

This specification defines the requirements for importing research project data from CSV files into the OneStep system as Initiative entities. The system must handle the creation of research projects along with their associated people (coordinators, team members, and students), ensuring data integrity and proper relationship management.

## Glossary

- **System**: The OneStep Django REST API application
- **Initiative**: A research project entity in the system with type "Research Project"
- **Person**: An individual who can be a coordinator, team member, or student
- **Coordinator**: The person responsible for leading the research project
- **Team Member**: A researcher participating in the project (Pesquisadores)
- **Student**: A student participating in the project (Estudantes)
- **CSV File**: A comma-separated values file containing research project data
- **Import Process**: The automated process of reading CSV data and creating database records

## Requirements

### Requirement 1: CSV File Format Support

**User Story:** As a system administrator, I want to import research projects from a CSV file, so that I can efficiently populate the system with existing project data.

#### Acceptance Criteria

1. THE System SHALL accept CSV files encoded in UTF-8 format
2. THE System SHALL require a header row with specific column names
3. THE System SHALL support the following required columns: Titulo, Inicio, Fim, Coordenador, EmailCoordenador
4. THE System SHALL support the following optional columns: Pesquisadores, Estudantes
5. THE System SHALL parse date fields in DD-MM-YY format

### Requirement 2: Research Project Creation

**User Story:** As a system administrator, I want research projects to be created as Initiative entities, so that they integrate with the existing initiative management system.

#### Acceptance Criteria

1. WHEN processing a CSV row, THE System SHALL create an Initiative with type "Research Project"
2. THE System SHALL map the Titulo column to the Initiative name field
3. THE System SHALL map the Inicio column to the Initiative start_date field
4. THE System SHALL map the Fim column to the Initiative end_date field
5. THE System SHALL apply text normalization (Title Case) to the project name

### Requirement 3: Coordinator Management

**User Story:** As a system administrator, I want coordinators to be automatically created or linked, so that project leadership is properly tracked.

#### Acceptance Criteria

1. WHEN processing a coordinator, THE System SHALL search for existing Person by email (case-insensitive)
2. IF the Person does not exist, THEN THE System SHALL create a new Person record
3. THE System SHALL map the Coordenador column to the Person name field
4. THE System SHALL map the EmailCoordenador column to the Person email field
5. THE System SHALL assign the Person as the Initiative coordinator
6. THE System SHALL apply text normalization (Title Case) to person names

### Requirement 4: Team Member Management

**User Story:** As a system administrator, I want researchers to be added as team members, so that project participation is tracked.

#### Acceptance Criteria

1. WHEN the Pesquisadores column contains data, THE System SHALL parse the semicolon-separated list of names
2. FOR each researcher name, THE System SHALL create or retrieve a Person record
3. THE System SHALL add each Person to the Initiative team_members relationship
4. IF a researcher name is empty after trimming, THEN THE System SHALL skip that entry
5. THE System SHALL apply text normalization (Title Case) to researcher names

### Requirement 5: Student Management

**User Story:** As a system administrator, I want students to be added to projects, so that student participation is tracked.

#### Acceptance Criteria

1. WHEN the Estudantes column contains data, THE System SHALL parse the semicolon-separated list of names
2. FOR each student name, THE System SHALL create or retrieve a Person record
3. THE System SHALL add each Person to the Initiative students relationship
4. IF a student name is empty after trimming, THEN THE System SHALL skip that entry
5. THE System SHALL apply text normalization (Title Case) to student names

### Requirement 6: Person Creation and Deduplication

**User Story:** As a system administrator, I want people to be deduplicated by name, so that duplicate person records are avoided.

#### Acceptance Criteria

1. WHEN creating a Person without email, THE System SHALL search by normalized name (case-insensitive)
2. IF a Person with the same normalized name exists, THEN THE System SHALL reuse the existing Person
3. IF no matching Person exists, THEN THE System SHALL create a new Person record
4. THE System SHALL generate a placeholder email in format "name.surname@noemail.local" for people without emails
5. THE System SHALL normalize all whitespace in person names

### Requirement 7: Data Validation

**User Story:** As a system administrator, I want invalid data to be reported, so that I can correct errors in the source file.

#### Acceptance Criteria

1. IF the Titulo field is empty, THEN THE System SHALL report a validation error
2. IF the Coordenador field is empty, THEN THE System SHALL report a validation error
3. IF the EmailCoordenador field is empty or invalid, THEN THE System SHALL report a validation error
4. IF date fields are in invalid format, THEN THE System SHALL report a validation error
5. IF the end date is before the start date, THEN THE System SHALL report a validation error

### Requirement 8: Transaction Management

**User Story:** As a system administrator, I want each row to be processed in a transaction, so that partial imports don't corrupt the database.

#### Acceptance Criteria

1. THE System SHALL wrap each row import in a database transaction
2. IF any error occurs during row processing, THEN THE System SHALL rollback the transaction for that row
3. THE System SHALL continue processing remaining rows after a row failure
4. THE System SHALL track successful, skipped, and failed row counts
5. THE System SHALL provide detailed error messages for failed rows

### Requirement 9: Duplicate Detection

**User Story:** As a system administrator, I want duplicate projects to be detected, so that I don't create redundant records.

#### Acceptance Criteria

1. THE System SHALL consider an Initiative duplicate IF a project with the same name and coordinator exists
2. WHEN a duplicate is detected, THE System SHALL skip the row and report it as skipped
3. THE System SHALL include the duplicate detection reason in the skip message
4. THE System SHALL perform case-insensitive comparison for duplicate detection
5. THE System SHALL normalize whitespace before duplicate comparison

### Requirement 10: Import Reporting

**User Story:** As a system administrator, I want a detailed import report, so that I can verify the import results.

#### Acceptance Criteria

1. THE System SHALL report the total number of rows processed
2. THE System SHALL report the number of successfully imported projects
3. THE System SHALL report the number of skipped duplicate projects
4. THE System SHALL report the number of rows with errors
5. THE System SHALL provide a list of errors with row numbers and error messages

### Requirement 11: Django Admin Integration

**User Story:** As a system administrator, I want to import research projects through the Django admin interface, so that I can easily upload CSV files without using command-line tools.

#### Acceptance Criteria

1. THE System SHALL provide a custom admin view for CSV file upload in the Initiative admin
2. THE System SHALL display an "Import Research Projects from CSV" button in the Initiative changelist page
3. WHEN the import button is clicked, THEN THE System SHALL display a file upload form
4. THE System SHALL validate that the uploaded file has a .csv extension
5. THE System SHALL display success, warning, and error messages after import completion

### Requirement 12: Admin Import Form

**User Story:** As a system administrator, I want clear instructions on the CSV format, so that I can prepare my data correctly.

#### Acceptance Criteria

1. THE System SHALL display a CSV format documentation table on the upload form
2. THE System SHALL indicate which columns are required and which are optional
3. THE System SHALL provide example values for each column
4. THE System SHALL explain the date format (DD-MM-YY)
5. THE System SHALL explain how to format lists (semicolon-separated)

### Requirement 13: Admin Import Feedback

**User Story:** As a system administrator, I want clear feedback after import, so that I know what succeeded and what failed.

#### Acceptance Criteria

1. WHEN import succeeds, THE System SHALL display a success message with the count of imported projects
2. WHEN duplicates are skipped, THE System SHALL display a warning message with the count
3. WHEN errors occur, THE System SHALL display error messages with row numbers
4. THE System SHALL limit error display to the first 10 errors to avoid overwhelming the interface
5. WHEN more than 10 errors exist, THE System SHALL indicate the count of additional errors
