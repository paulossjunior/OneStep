# Requirements Document

## Introduction

This feature ensures that when importing research projects from CSV files, the `ParceiroDemandante` column (which represents a demanding partner organization) is properly processed. Each unique demanding partner should be created as an Organization record and linked to the corresponding Initiative.

## Glossary

- **Initiative**: A research project, program, or event in the system
- **Organization**: A top-level organizational entity that represents companies, institutions, or partner organizations
- **OrganizationalUnit**: A sub-unit within an Organization (e.g., research groups, departments)
- **ParceiroDemandante**: Portuguese term meaning "Demanding Partner" - an organization that requests or demands an initiative
- **CSV Import System**: The system that processes CSV files containing research project data
- **GroupHandler**: Component responsible for creating and managing Organization and OrganizationalUnit instances
- **ResearchProjectImportProcessor**: Main processor that orchestrates the CSV import workflow

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want the CSV import to create Organization records for demanding partners, so that I can track which organizations request initiatives

#### Acceptance Criteria

1. WHEN the CSV import processes a row with a non-empty ParceiroDemandante value, THE System SHALL create or retrieve an Organization for that demanding partner
2. THE System SHALL normalize the demanding partner name to Title Case before processing
3. THE System SHALL check for existing Organization records using case-insensitive matching on the name field
4. IF an Organization with the same name already exists, THEN THE System SHALL reuse the existing record
5. THE System SHALL set the demanding_partner field on the Initiative to reference the Organization

### Requirement 2

**User Story:** As a system administrator, I want demanding partners to have descriptive information, so that I can understand their role in the system

#### Acceptance Criteria

1. WHEN creating a new demanding partner Organization, THE System SHALL set the description field to indicate it is a demanding partner
2. THE System SHALL use the description "Organization that demands or requests initiatives" for demanding partner Organizations
3. THE System SHALL allow the description field to be updated manually after import
4. THE System SHALL preserve existing Organization records if they already exist with the same name

### Requirement 3

**User Story:** As a system administrator, I want the Initiative model to support Organization as demanding partner, so that I can link initiatives to partner organizations

#### Acceptance Criteria

1. THE Initiative model SHALL have a demanding_partner field that references the Organization model
2. THE demanding_partner field SHALL be optional (null=True, blank=True)
3. THE demanding_partner field SHALL use SET_NULL on delete to preserve Initiative records when Organizations are deleted
4. THE System SHALL create a reverse relationship named "demanded_initiatives" on the Organization model
5. THE System SHALL allow querying all initiatives demanded by a specific Organization

### Requirement 4

**User Story:** As a system administrator, I want to see clear import results, so that I can verify demanding partners were processed correctly

#### Acceptance Criteria

1. WHEN the CSV import completes, THE System SHALL include demanding partner creation in the success count
2. IF a demanding partner creation fails, THEN THE System SHALL log an error with the row number and error message
3. THE System SHALL continue processing subsequent rows even if one demanding partner creation fails
4. THE System SHALL provide a summary report showing total rows processed, successes, errors, and skips
5. THE System SHALL log whether a demanding partner Organization was created or reused for each row

### Requirement 5

**User Story:** As a system administrator, I want the import to handle edge cases gracefully, so that the system remains stable

#### Acceptance Criteria

1. WHEN the ParceiroDemandante field is empty or contains only whitespace, THE System SHALL skip demanding partner creation
2. WHEN a database integrity error occurs during demanding partner creation, THE System SHALL log the error and continue processing
3. THE System SHALL use database transactions to ensure atomicity for each row
4. IF an error occurs processing a row, THEN THE System SHALL rollback changes for that row only
5. THE System SHALL handle race conditions where multiple processes attempt to create the same Organization simultaneously
