# CSV Import for Research Groups

This module provides functionality to import research group data from CSV files into the OneStep system.

## Features

- Import organizational groups from CSV files
- Automatic creation of Campus and KnowledgeArea records
- Automatic creation of Person records for leaders
- Deduplication based on email (Person) and name (Campus, KnowledgeArea)
- Skip duplicate groups (same short_name + campus)
- Comprehensive validation and error reporting
- Per-row transaction handling for fault tolerance

## Usage

### Admin Interface

1. Navigate to the Organizational Groups admin page
2. Click the "Import from CSV" button in the top right
3. Select your CSV file
4. Click "Import"
5. Review the import results

### CSV File Format

The CSV file must have the following columns (header row required):

- **Sigla** - Group abbreviation (optional, will be generated if empty)
- **Nome** - Full group name (required)
- **repositorio** - Repository URL (optional)
- **Site** - Website URL (optional, not imported)
- **AreaConhecimento** - Knowledge area (required)
- **Unidade** - Campus name (required)
- **Lideres** - Leaders in format "Name (email), Name (email)" (optional)

### Example CSV

```csv
Sigla,Nome,repositorio,Site,AreaConhecimento,Unidade,Lideres
AI,Artificial Intelligence Lab,https://github.com/ai-lab,,Computer Science,Main Campus,"John Doe (john@example.com), Jane Smith (jane@example.com)"
BIO,Biology Research Group,https://github.com/bio-group,,Biology,North Campus,"Alice Johnson (alice@example.com)"
```

See `examples/sample_research_groups.csv` for a complete example.

## Components

- **CSVParser** - Parses CSV files with UTF-8 encoding support
- **DataValidator** - Validates row data before processing
- **CampusHandler** - Creates or retrieves Campus records
- **KnowledgeAreaHandler** - Creates or retrieves KnowledgeArea records
- **PersonHandler** - Creates or retrieves Person records
- **GroupHandler** - Creates OrganizationalGroup records with relationships
- **ImportProcessor** - Orchestrates the import process
- **ImportReporter** - Tracks statistics and errors

## Error Handling

The import process uses per-row transactions, meaning:
- If a row fails, only that row is rolled back
- Other rows continue to be processed
- All errors are logged with row numbers
- A summary report is displayed after import

## Validation Rules

- Nome (name) is required
- Unidade (campus) is required
- AreaConhecimento (knowledge area) is required
- Email addresses must be valid format
- URLs must be valid format (if provided)
- Leader format must be "Name (email)"

## Deduplication

- **Campus**: Case-insensitive name lookup
- **KnowledgeArea**: Case-insensitive name lookup
- **Person**: Case-insensitive email lookup
- **OrganizationalGroup**: Skipped if same `(short_name, campus, organization)` combination exists

### Multiple Groups with Same Short Name

The system allows multiple groups to have the same `short_name` as long as they are on **different campuses**. This is useful for multi-campus institutions where different campuses may independently use the same acronyms.

**Example:**
- NEEF at Cariacica campus ✓
- NEEF at Serra campus ✓
- Both can coexist

The uniqueness constraint is: `(short_name, organization, campus)`

## Automatic Short Name Generation

When a group doesn't have a `Sigla` (short name) in the CSV, the system automatically generates one using an intelligent acronym-based approach:

### Generation Algorithm

1. **Extract significant words** - Filters out common articles, prepositions, and conjunctions (e.g., "de", "em", "para", "the", "of", "and")
2. **Create acronym** - Takes the first letter of each significant word
3. **Apply constraints** - Limits to 10 characters maximum, ensures at least 2 characters
4. **Add campus code** - Appends campus code for uniqueness (e.g., "AC-COL", "BU-VIT")

### Examples

| Group Name | Campus | Generated Short Name |
|------------|--------|---------------------|
| Ambiente Construído | Colatina | AC-COL |
| Análise e Desenvolvimento em Sistemas Mecânicos | Vitória | ADSM-VIT |
| Biodiversidade Urbana | Vitória | BU-VIT |
| Ciência e Tecnologia de Alimentos | Venda Nova | CTA-VEN |

**Benefits:**
- Meaningful acronyms derived from actual group names
- Campus code ensures uniqueness across campuses
- Consistent and predictable naming

For detailed information, see [SHORT_NAME_GENERATION.md](SHORT_NAME_GENERATION.md).

## Notes

- All imported groups have type "Research"
- Campus codes are auto-generated from names
- Short names are auto-generated if not provided (see Automatic Short Name Generation above)
- Leader relationships are created with current date as start_date
- The Site column is not imported (only repositorio is used for the URL field)
- Groups with the same short_name can exist on different campuses
