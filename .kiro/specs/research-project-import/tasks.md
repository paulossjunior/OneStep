# Implementation Plan

## Overview
This implementation plan outlines the tasks required to build a CSV import feature for research projects in the OneStep system. Research projects will be imported as Initiative entities with type "Research Project", along with their associated people (coordinators, team members, and students).

---

## Tasks

- [x] 1. Set up CSV import infrastructure
  - Create `apps/initiatives/csv_import/` directory structure
  - Reuse existing CSVParser from organizational_group app
  - Reuse existing ImportReporter from organizational_group app
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 1.1 Create csv_import package structure
  - Create `apps/initiatives/csv_import/__init__.py`
  - Copy `CSVParser` from `apps/organizational_group/csv_import/parser.py` to `apps/initiatives/csv_import/parser.py`
  - Copy `ImportReporter` from `apps/organizational_group/csv_import/reporter.py` to `apps/initiatives/csv_import/reporter.py`
  - _Requirements: 1.1, 1.2_

- [x] 2. Implement data validation
  - Create validator for research project CSV data
  - Validate required fields (Titulo, Coordenador, EmailCoordenador, Inicio, Fim)
  - Validate date formats (DD-MM-YY)
  - Validate email addresses
  - Validate date logic (end_date >= start_date)
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2.1 Create ResearchProjectValidator class
  - Create `apps/initiatives/csv_import/validator.py`
  - Implement `ValidationResult` class to hold validation results
  - Implement `ResearchProjectValidator` class with `validate_row()` method
  - Implement `validate_email()` method for email format validation
  - Implement `validate_date()` method for DD-MM-YY format validation
  - Implement `parse_date()` method to convert date strings to date objects
  - Implement `validate_date_range()` method to ensure end_date >= start_date
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 3. Implement person management
  - Create handler for Person creation and deduplication
  - Handle coordinator creation with email
  - Handle team member and student creation (with or without email)
  - Generate placeholder emails for people without emails
  - Parse semicolon-separated lists of names
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.1 Create PersonHandler class
  - Create `apps/initiatives/csv_import/person_handler.py`
  - Implement `PersonHandler` class
  - Implement `get_or_create_person()` method for coordinator creation (with email)
  - Implement deduplication by email (case-insensitive)
  - Implement deduplication by name for people without emails
  - Implement `generate_placeholder_email()` method (format: firstname.lastname@noemail.local)
  - Implement `normalize_name()` method for Title Case normalization
  - Implement `parse_people_list()` method for semicolon-separated lists
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 4. Implement initiative management
  - Create handler for Initiative creation
  - Create or retrieve "Research Project" InitiativeType
  - Detect duplicate initiatives (same name + coordinator)
  - Assign coordinator, team members, and students relationships
  - Normalize initiative names to Title Case
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 4.1 Create InitiativeHandler class
  - Create `apps/initiatives/csv_import/initiative_handler.py`
  - Implement `InitiativeHandler` class
  - Implement `get_research_project_type()` method to get/create "Research Project" InitiativeType
  - Implement `create_or_skip_initiative()` method to create Initiative or skip if duplicate
  - Implement `is_duplicate()` method to check for duplicates (same name + coordinator)
  - Implement `normalize_name()` method for Title Case normalization
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 5. Implement import processor
  - Create processor to orchestrate the import process
  - Coordinate between validator, person handler, and initiative handler
  - Manage database transactions (one per row)
  - Handle errors and rollback on failure
  - Track statistics via ImportReporter
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 5.1 Create ResearchProjectImportProcessor class
  - Create `apps/initiatives/csv_import/processor.py`
  - Implement `ResearchProjectImportProcessor` class
  - Implement `process_csv()` method to process entire CSV file
  - Implement `process_row()` method to process a single row within a transaction
  - Use `@transaction.atomic` decorator for transaction management
  - Handle ValidationError, IntegrityError, and general exceptions
  - Track success, skip, and error counts using ImportReporter
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 6. Create Django management command
  - Create management command for CLI import
  - Accept CSV file path as argument
  - Display import results and statistics
  - Return appropriate exit codes
  - _Requirements: 1.1, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 6.1 Implement import_research_projects command
  - Create `apps/initiatives/management/` directory if it doesn't exist
  - Create `apps/initiatives/management/__init__.py`
  - Create `apps/initiatives/management/commands/` directory
  - Create `apps/initiatives/management/commands/__init__.py`
  - Create `apps/initiatives/management/commands/import_research_projects.py`
  - Implement `Command` class extending `BaseCommand`
  - Add `csv_file` argument to accept file path
  - Call `ResearchProjectImportProcessor.process_csv()` with file path
  - Display import summary using `reporter.generate_summary()`
  - Display detailed errors if any
  - Return exit code 0 for success, 1 for errors
  - _Requirements: 1.1, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 7. Integrate with Django admin interface
  - Add "Import Research Projects from CSV" button to Initiative changelist
  - Create file upload form with format documentation
  - Display import results with success/warning/error messages
  - Limit error display to first 10 errors
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 12.1, 12.2, 12.3, 12.4, 12.5, 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 7.1 Create custom admin view for CSV import
  - Update `apps/initiatives/admin.py` to add custom URL for import
  - Override `get_urls()` method in `InitiativeAdmin` to add import URL
  - Implement `import_csv_view()` method to handle file upload and import
  - Handle GET request to display upload form
  - Handle POST request to process uploaded CSV file
  - Validate file extension (.csv only)
  - Call `ResearchProjectImportProcessor.process_csv()` with uploaded file
  - Display success messages for imported projects
  - Display warning messages for skipped duplicates
  - Display error messages (limit to first 10)
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 7.2 Create admin templates for CSV import
  - Create `apps/initiatives/templates/` directory if it doesn't exist
  - Create `apps/initiatives/templates/admin/` directory
  - Create `apps/initiatives/templates/admin/initiatives/` directory
  - Create `apps/initiatives/templates/admin/initiatives/initiative/` directory
  - Create `change_list.html` template extending default changelist
  - Add "Import Research Projects from CSV" button to changelist
  - Create `import_csv.html` template for file upload form
  - Add CSV format documentation table with column descriptions
  - Add example values for each column
  - Explain date format (DD-MM-YY) and list format (semicolon-separated)
  - _Requirements: 11.1, 11.2, 11.3, 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 7.3 Update InitiativeAdmin configuration
  - Set `change_list_template` to custom template path
  - Ensure admin uses custom changelist template
  - _Requirements: 11.1, 11.2_

- [ ]* 8. Write unit tests for CSV import components
  - Test validator with valid and invalid data
  - Test person handler deduplication logic
  - Test initiative handler duplicate detection
  - Test import processor transaction management
  - _Requirements: All requirements_

- [ ]* 8.1 Create test_validator.py
  - Create `apps/initiatives/csv_import/tests/` directory
  - Create `apps/initiatives/csv_import/tests/__init__.py`
  - Create `apps/initiatives/csv_import/tests/test_validator.py`
  - Test valid row with all fields
  - Test valid row with only required fields
  - Test missing required fields (Titulo, Coordenador, EmailCoordenador)
  - Test invalid date formats
  - Test invalid email formats
  - Test end date before start date
  - Test empty semicolon-separated lists
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 8.2 Create test_person_handler.py
  - Create `apps/initiatives/csv_import/tests/test_person_handler.py`
  - Test create person with email
  - Test create person without email (placeholder generation)
  - Test deduplicate by email (case-insensitive)
  - Test deduplicate by name (case-insensitive)
  - Test parse semicolon-separated list
  - Test handle empty names in list
  - Test name normalization (Title Case)
  - Test placeholder email uniqueness
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 8.3 Create test_initiative_handler.py
  - Create `apps/initiatives/csv_import/tests/test_initiative_handler.py`
  - Test create initiative with all relationships
  - Test create initiative with only coordinator
  - Test duplicate detection (same name + coordinator)
  - Test non-duplicate (same name, different coordinator)
  - Test non-duplicate (different name, same coordinator)
  - Test name normalization (Title Case)
  - Test Research Project type creation
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]* 8.4 Create test_processor.py
  - Create `apps/initiatives/csv_import/tests/test_processor.py`
  - Test process valid CSV file
  - Test process CSV with errors
  - Test process CSV with duplicates
  - Test transaction rollback on error
  - Test statistics tracking
  - Test row-by-row processing
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 9. Write integration tests
  - Test end-to-end CSV import
  - Test admin interface import functionality
  - Test management command execution
  - _Requirements: All requirements_

- [ ]* 9.1 Create test_integration.py
  - Create `apps/initiatives/csv_import/tests/test_integration.py`
  - Test import complete CSV file end-to-end
  - Verify all Initiatives created
  - Verify all People created
  - Verify all relationships assigned
  - Verify statistics accuracy
  - _Requirements: All requirements_

- [ ]* 9.2 Create test_admin_integration.py
  - Create `apps/initiatives/tests/test_admin_csv_import.py`
  - Test access import form view
  - Test upload CSV file via admin
  - Test view import results
  - Test error message display
  - Test success message display
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ]* 9.3 Create test_command.py
  - Create `apps/initiatives/tests/test_import_command.py`
  - Test execute command with valid file
  - Test execute command with invalid file
  - Test verify console output
  - Test verify exit codes
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10. Create sample CSV files for testing
  - Create example CSV file with valid research project data
  - Document CSV format in README or documentation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 10.1 Create sample CSV files
  - Create `examples/` directory if it doesn't exist
  - Create `examples/sample_research_projects.csv` with valid data
  - Include examples with all fields populated
  - Include examples with only required fields
  - Include examples with semicolon-separated lists
  - Use DD-MM-YY date format
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 10.2 Create CSV format documentation
  - Create or update `docs/CSV_IMPORT_GUIDE.md`
  - Document required columns (Titulo, Inicio, Fim, Coordenador, EmailCoordenador)
  - Document optional columns (Pesquisadores, Estudantes)
  - Document date format (DD-MM-YY)
  - Document list format (semicolon-separated)
  - Provide example CSV content
  - Document common errors and solutions
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

---

## Notes

- Tasks marked with `*` are optional and focus on testing
- Each task references specific requirements from the requirements document
- Tasks build incrementally on previous tasks
- The implementation follows the existing CSV import pattern from organizational_group app
- Transaction management ensures data integrity (one transaction per row)
- Duplicate detection prevents redundant imports
- Person deduplication avoids duplicate Person records
