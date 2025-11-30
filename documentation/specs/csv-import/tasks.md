# Implementation Plan: CSV Import for Research Groups

## Overview
This implementation plan covers the development of CSV import functionality for research groups, including a Django management command and admin interface integration.

## Tasks

- [x] 1. Create CSV import core components
  - Implement CSV parser, validators, and handler classes for processing research group data
  - Create reusable components for Campus, Person, and OrganizationalGroup handling
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 1.1 Implement CSVParser class
  - Create `apps/organizational_group/csv_import/parser.py` with CSVParser class
  - Implement `parse_file()` method using csv.DictReader with UTF-8 encoding support
  - Handle BOM for Excel compatibility and strip whitespace from values
  - Yield rows iteratively for memory efficiency
  - _Requirements: 1.3_

- [x] 1.2 Implement DataValidator class
  - Create `apps/organizational_group/csv_import/validator.py` with DataValidator class
  - Implement `validate_row()` method checking required fields (Nome, Unidade, AreaConhecimento)
  - Implement `validate_email()` using Django's EmailValidator
  - Implement `validate_url()` using Django's URLValidator (allow empty)
  - Parse and validate leader format with regex pattern "Name (email)"
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 1.3 Implement CampusHandler class
  - Create `apps/organizational_group/csv_import/campus_handler.py` with CampusHandler class
  - Implement `get_or_create_campus()` with case-insensitive name lookup
  - Implement `generate_campus_code()` from name (uppercase, remove spaces, truncate to 20 chars)
  - Handle code collisions by appending numeric suffix
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 1.3.1 Implement KnowledgeAreaHandler class
  - Create `apps/organizational_group/csv_import/knowledge_area_handler.py` with KnowledgeAreaHandler class
  - Implement `get_or_create_knowledge_area()` with case-insensitive name lookup
  - Strip whitespace from knowledge area names before lookup or creation
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 1.4 Implement PersonHandler class
  - Create `apps/organizational_group/csv_import/person_handler.py` with PersonHandler class
  - Implement `parse_leaders()` to extract (name, email) tuples from comma-separated string
  - Use regex to parse "Name (email)" pattern
  - Implement `get_or_create_person()` with case-insensitive email lookup
  - Normalize email to lowercase and strip whitespace from names
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 1.5 Implement GroupHandler class
  - Create `apps/organizational_group/csv_import/group_handler.py` with GroupHandler class
  - Implement `create_or_skip_group()` checking for duplicates by (short_name, campus)
  - Map CSV columns: Sigla→short_name, Nome→name, repositorio→url, AreaConhecimento→knowledge_area (FK)
  - Generate short_name from full name if Sigla is empty
  - Implement `assign_leaders()` creating OrganizationalGroupLeadership records
  - Set start_date to current date and is_active to True for new leaders
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 1.6 Implement ImportProcessor class
  - Create `apps/organizational_group/csv_import/processor.py` with ImportProcessor class
  - Implement `process_csv()` orchestrating the full import workflow
  - Implement `process_row()` with per-row transaction handling
  - Wrap each row in database transaction with rollback on error
  - Continue processing remaining rows after individual failures
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 1.7 Implement ImportReporter class
  - Create `apps/organizational_group/csv_import/reporter.py` with ImportReporter class
  - Implement methods: `add_success()`, `add_skip()`, `add_error()`
  - Implement `generate_summary()` returning formatted summary report
  - Implement `get_errors()` returning list of error dictionaries with row numbers
  - Track total rows, successful imports, skipped duplicates, and errors
  - _Requirements: 1.4, 1.5, 7.4_

- [x] 2. Create Django management command
  - Implement `import_research_groups` management command
  - Integrate ImportProcessor and display results with colored output
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [x] 2.1 Create management command file
  - Create `apps/organizational_group/management/commands/import_research_groups.py`
  - Implement Command class extending BaseCommand
  - Add `csv_file` argument accepting file path parameter
  - Validate file exists before processing
  - Instantiate ImportProcessor and call `process_csv()`
  - Display progress information during import (every 10 rows)
  - Display summary report using self.stdout.write()
  - Use self.style.SUCCESS, WARNING, ERROR for colored output
  - Show detailed error list with row numbers
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [ ]* 2.2 Write management command tests
  - Create `apps/organizational_group/tests/test_csv_import_command.py`
  - Test command with valid CSV file
  - Test command with missing file
  - Test command with malformed CSV
  - Test command output formatting
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3. Integrate CSV import into Django admin
  - Add custom admin action for CSV file upload
  - Create upload form template and process uploaded files
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 3.1 Add admin action to OrganizationalGroupAdmin
  - Modify `apps/organizational_group/admin.py`
  - Add `import_from_csv` method to OrganizationalGroupAdmin class
  - Add action to actions list
  - Handle POST request with uploaded file
  - Process file using ImportProcessor
  - Display success/error messages using self.message_user()
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 3.2 Create CSV upload form template
  - Create `apps/organizational_group/templates/admin/organizational_group/import_csv.html`
  - Extend admin/base_site.html template
  - Add file upload form with CSRF token
  - Include CSV format documentation with column descriptions (Sigla, Nome, repositorio, Site, AreaConhecimento, Unidade, Lideres)
  - Add submit and cancel buttons
  - _Requirements: 8.2_

- [ ]* 3.3 Write admin integration tests
  - Create tests in `apps/organizational_group/tests/test_admin.py` for CSV import
  - Test admin action appears in action list
  - Test file upload form display
  - Test successful CSV upload and processing
  - Test error message display for invalid files
  - _Requirements: 8.5_
