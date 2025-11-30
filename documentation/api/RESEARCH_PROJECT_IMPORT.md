# Research Project CSV Import

## Overview

The Research Project CSV Import feature allows administrators to bulk import research projects from CSV files into the OneStep system. Projects are imported as Initiative entities with the type "Research Project", along with their associated people (coordinators, team members, and students).

## Features

- **CSV Import**: Import research projects from CSV files via Django admin or management command
- **Person Management**: Automatically create or deduplicate people based on email or name
- **Multiple Emails**: Support for people with multiple email addresses
- **Duplicate Detection**: Skip duplicate projects (same name + coordinator)
- **Relationship Management**: Automatically assign coordinators, team members, and students
- **Error Handling**: Comprehensive error reporting with row-level details
- **Transaction Safety**: Each row is processed in its own transaction for data integrity

## CSV Format

### Required Columns

| Column Name | Description | Example |
|------------|-------------|---------|
| **Titulo** | Research project title | Machine Learning for Healthcare |
| **Coordenador** | Coordinator's full name | João Silva |
| **EmailCoordenador** | Coordinator's email address | joao.silva@example.com |
| **Inicio** | Start date (DD-MM-YY format) | 01-08-22 |
| **Fim** | End date (DD-MM-YY format) | 31-12-26 |

### Optional Columns

| Column Name | Description | Example |
|------------|-------------|---------|
| **Pesquisadores** | Team members (semicolon-separated) | Maria Santos; Pedro Costa; Ana Lima |
| **Estudantes** | Students (semicolon-separated) | Carlos Souza; Julia Oliveira |
| **AreaConhecimento** | Knowledge area name | Ciência da Computação |
| **GrupoPesquisa** | Organizational group name | Grupo de Automação Industrial |

### Format Notes

- **Date Format**: All dates must be in DD-MM-YY format (e.g., 01-08-22 for August 1, 2022)
- **List Format**: Multiple names must be separated by semicolons (;)
- **Duplicate Detection**: Projects with the same title and coordinator will be skipped
- **Person Deduplication**: 
  - People with emails are deduplicated by email (case-insensitive)
  - People without emails are deduplicated by name (case-insensitive)
- **Multiple Emails**: A person can have multiple email addresses tracked in the PersonEmail model
- **Knowledge Areas**: 
  - Knowledge areas are automatically created if they don't exist
  - Multiple knowledge areas can be associated with an initiative
  - Names are normalized to Title Case
- **Organizational Groups**: 
  - Only existing groups are linked (groups are not created automatically)
  - Groups are matched by name or short_name (case-insensitive)
  - Multiple groups can be associated with an initiative
  - Knowledge areas are automatically synced from initiatives to groups
  - Groups inherit knowledge areas from all their associated initiatives

## Usage

### Via Django Admin

1. Navigate to the Initiatives admin page
2. Click "Import Research Projects from CSV" button
3. Select your CSV file
4. Click "Import"
5. Review the import results (success, warnings, errors)

### Via Management Command

```bash
python manage.py import_research_projects <path_to_csv_file>
```

Example:
```bash
python manage.py import_research_projects examples/sample_research_projects.csv
```

## Example CSV

```csv
Titulo,Coordenador,EmailCoordenador,Inicio,Fim,Pesquisadores,Estudantes
Machine Learning for Healthcare,João Silva,joao.silva@example.com,01-08-22,31-12-26,Maria Santos; Pedro Costa; Ana Lima,Carlos Souza; Julia Oliveira
Data Science Research,Ana Lima,ana.lima@example.com,01-09-23,31-08-25,Roberto Alves; Fernanda Dias,Lucas Martins
Computer Vision Applications,Pedro Costa,pedro.costa@example.com,01-01-24,31-12-25,João Silva; Maria Santos,Beatriz Rocha; Diego Ferreira
```

## Model Updates

### Person Model
The Person model has been updated to support multiple email addresses:

- **Person.email**: Primary email address (optional, can be null)
- **PersonEmail**: New model to track multiple email addresses per person
  - Each email is unique across all people
  - One email can be marked as primary per person
  - Emails are automatically deduplicated during import

### Initiative Model
The Initiative model has been updated to support knowledge areas:

- **Initiative.knowledge_areas**: ManyToManyField to KnowledgeArea
  - Initiatives can be associated with multiple knowledge areas
  - Knowledge areas are automatically created during import

### OrganizationalGroup Model
The OrganizationalGroup model has been updated to support multiple knowledge areas:

- **OrganizationalGroup.knowledge_areas**: ManyToManyField to KnowledgeArea
  - Groups can have multiple knowledge areas
  - Knowledge areas are automatically synced from associated initiatives
  - Use `sync_knowledge_areas_from_initiatives()` method to update
  - Use `get_all_knowledge_areas()` to get both primary and synced knowledge areas

## Architecture

### Components

1. **CSVParser** (`apps/initiatives/csv_import/parser.py`)
   - Parses CSV files and yields rows as dictionaries
   - Handles both file paths and file-like objects
   - Cleans whitespace from all values

2. **ResearchProjectValidator** (`apps/initiatives/csv_import/validator.py`)
   - Validates required fields
   - Validates email formats
   - Validates date formats (DD-MM-YY)
   - Validates date ranges (end >= start)

3. **PersonHandler** (`apps/initiatives/csv_import/person_handler.py`)
   - Creates or retrieves Person records
   - Deduplicates by email (via PersonEmail) or name
   - Manages PersonEmail records
   - Normalizes names to Title Case

4. **InitiativeHandler** (`apps/initiatives/csv_import/initiative_handler.py`)
   - Creates or skips Initiative records
   - Detects duplicates (same name + coordinator)
   - Creates "Research Project" InitiativeType
   - Normalizes names to Title Case

5. **ResearchProjectImportProcessor** (`apps/initiatives/csv_import/processor.py`)
   - Orchestrates the import process
   - Manages transactions (one per row)
   - Handles errors and rollback
   - Tracks statistics via ImportReporter

6. **ImportReporter** (`apps/initiatives/csv_import/reporter.py`)
   - Tracks import statistics
   - Records successes, skips, and errors
   - Generates summary reports

7. **GroupHandler** (`apps/initiatives/csv_import/group_handler.py`)
   - Creates or retrieves KnowledgeArea records
   - Retrieves existing OrganizationalGroup records
   - Normalizes names to Title Case

## Error Handling

- **Validation Errors**: Invalid data (missing fields, bad formats, etc.)
- **Integrity Errors**: Database constraint violations
- **Transaction Rollback**: Each row is processed in its own transaction
- **Error Reporting**: Detailed error messages with row numbers
- **Partial Success**: Valid rows are imported even if some rows fail

## Statistics

After import, the system reports:
- Total rows processed
- Successful imports
- Skipped duplicates
- Errors encountered

## Testing

Sample CSV files are available in the `examples/` directory:
- `examples/sample_research_projects.csv` - Simple test data
- `example/research_group/research_group/research_projects.csv` - Real-world data

## Database Migrations

The following migrations were created:
- `apps/people/migrations/0002_alter_person_email_personemail_and_more.py`
  - Makes Person.email optional (nullable)
  - Creates PersonEmail model for multiple emails
  - Adds unique constraint on person+email combination
- `apps/initiatives/migrations/0003_initiative_knowledge_areas.py`
  - Adds knowledge_areas ManyToManyField to Initiative model
  - Allows initiatives to be associated with multiple knowledge areas
- `apps/organizational_group/migrations/0010_organizationalgroup_knowledge_areas_and_more.py`
  - Adds knowledge_areas ManyToManyField to OrganizationalGroup model
  - Allows groups to have multiple knowledge areas synced from initiatives
  - Updates help text for existing knowledge_area field

## Future Enhancements

- Support for additional CSV columns (description, keywords, etc.)
- Bulk update of existing projects
- Import preview before committing
- Export functionality
- Import history tracking
