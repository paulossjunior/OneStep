# Scholarship CSV Import

This module provides functionality to import scholarship data from CSV files into the OneStep system.

## Features

- Import scholarships from CSV files
- Automatic creation of related entities (types, people, campuses, sponsors)
- Duplicate detection and skipping
- Comprehensive validation and error reporting
- Per-row transaction handling for fault tolerance

## Usage

### Admin Interface

1. Navigate to the Scholarships admin page
2. Click the "Import from CSV" button in the top right
3. Select your CSV file
4. Click "Import"
5. Review the import results

### Command Line

```bash
python manage.py import_scholarships example/scholarship/scholarship.csv
```

## CSV File Format

The CSV file must have the following columns (header row required):

### Important Terminology

- **Orientado/OrientadoEmail**: Refers to the **student** (the person receiving the scholarship)
- **Orientador/OrientadorEmail**: Refers to the **supervisor** (the advisor/mentor guiding the student)

### Required Columns

- **Inicio** - Start date in DD-MM-YY format (e.g., "01-09-25")
- **Orientador** - Supervisor name (the advisor/mentor)
- **Orientado** - Student name (the scholarship recipient)
- **CampusExecucao** - Campus name

### Optional Columns

- **Valor** - Monthly scholarship value (defaults to 0 if empty, e.g., "300,00" or "300.00")
- **Fim** - End date in DD-MM-YY format
- **OrientadorEmail** - Supervisor email address
- **OrientadoEmail** - Student email address (scholarship recipient)
- **Programa** - Scholarship type/program (e.g., "Pibic", "Pibic-Jr")
- **TituloPT** - Scholarship title
- **TituloPJ** - Initiative/Project name (must exist in database)
- **AgFinanciadora** - Funding agency/sponsor name

## Column Mapping

| CSV Column | Database Field | Notes |
|------------|---------------|-------|
| Valor | value | Monthly scholarship value |
| Inicio | start_date | Start date |
| Fim | end_date | End date (optional) |
| Orientador | supervisor | Supervisor person (advisor/mentor) |
| OrientadorEmail | supervisor.email | Supervisor email - used to find/create supervisor |
| Orientado | student | Student person (scholarship recipient) |
| OrientadoEmail | student.email | Student email - used to find/create student |
| CampusExecucao | campus | Campus location |
| Programa | type | Scholarship type |
| TituloPT | title | Scholarship title |
| TituloPJ | initiative | Initiative (looked up by name) |
| AgFinanciadora | sponsor | Funding organization |

## Example CSV

```csv
Valor,Inicio,Fim,Orientador,OrientadorEmail,Orientado,OrientadoEmail,CampusExecucao,Programa,TituloPT,TituloPJ,AgFinanciadora
300,00,01-09-25,31-08-26,João Silva,joao@ifes.edu.br,Maria Santos,maria@example.com,Serra,Pibic-Jr,Research Project,AI Research Initiative,CNPq
700,00,01-09-25,31-08-26,Ana Costa,ana@ifes.edu.br,Pedro Oliveira,pedro@example.com,Vitória,Pibic,Data Science Study,,Fapes
```

## Automatic Entity Creation

The import process automatically creates the following entities if they don't exist:

- **Scholarship Types**: Created from `Programa` column
- **People**: Created from `Orientador`/`Orientado` with their emails
- **Campuses**: Created from `CampusExecucao` column
- **Sponsors**: Created from `AgFinanciadora` column

**Note**: Initiatives are NOT created automatically. They must exist in the database beforehand and are looked up by name from the `TituloPJ` column.

## Duplicate Detection

Scholarships are considered duplicates if they have the same:
- Student
- Start date
- Supervisor

Duplicates are skipped and reported in the import results.

## Validation Rules

- **Valor**: Optional, defaults to 0 if empty or blank; cannot be negative
- **Inicio**: Required, must be valid date
- **Fim**: Optional, must be after or equal to start date if provided
- **Orientado**: Required
- **CampusExecucao**: Required
- All model validation rules apply (see models.py)

## Error Handling

The import process uses per-row transactions:
- If a row fails, only that row is rolled back
- Other rows continue to be processed
- All errors are logged with row numbers
- A summary report is displayed after import

## Date Format

Dates must be in **DD-MM-YY** format:
- `01-09-25` = September 1, 2025
- `31-12-26` = December 31, 2026

Alternative formats supported:
- `DD/MM/YYYY` (e.g., `01/09/2025`)
- `YYYY-MM-DD` (e.g., `2025-09-01`)

## Value Format

Values can use comma or dot as decimal separator:
- `300,00` ✓
- `300.00` ✓
- `1500,50` ✓
- `R$ 300,00` ✓ (currency symbol is removed)

## Components

- **CSVParser** - Parses CSV files with UTF-8 encoding support
- **ScholarshipValidator** - Validates row data before processing
- **ScholarshipTypeHandler** - Creates or retrieves scholarship types
- **PersonHandler** - Creates or retrieves people
- **CampusHandler** - Creates or retrieves campuses
- **OrganizationHandler** - Creates or retrieves sponsors
- **InitiativeHandler** - Looks up initiatives by name
- **ScholarshipImportProcessor** - Orchestrates the import process
- **ImportReporter** - Tracks statistics and errors

## Troubleshooting

### Common Issues

**"Invalid Valor format"**
- Check that the value is a valid number
- Values can be empty (will default to 0)
- Values cannot be negative

**"Invalid Inicio date format"**
- Check that dates are in DD-MM-YY format
- Example: `01-09-25` not `09-01-25`

**"Could not create student"**
- Make sure `Orientado` column has a value (this is the student/scholarship recipient name)
- Provide `OrientadoEmail` if possible for better person matching and deduplication

**"Validation error: End date must be after or equal to start date"**
- Check that `Fim` date is after `Inicio` date

**"Initiative not found"**
- The initiative specified in `TituloPJ` doesn't exist
- Create the initiative first or leave `TituloPJ` empty

## Notes

- All text fields are automatically normalized to Title Case
- Email addresses are used for person deduplication
- Campus codes are auto-generated from campus names
- Scholarship type codes are auto-generated from type names
- The import is idempotent - running it multiple times with the same data will skip duplicates

## Related Documentation

- [Scholarship Models](../models.py)
- [Scholarship Admin](../admin.py)
- [Scholarship API](../API_DOCUMENTATION.md)
