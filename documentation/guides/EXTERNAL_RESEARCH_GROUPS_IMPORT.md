# External Research Groups CSV Import

## Overview
The initiatives CSV import now supports creating and associating external research groups (organizational units) with research projects.

## New Feature: GrupoPesquisaExterno Field

### CSV Column
- **Column Name:** `GrupoPesquisaExterno`
- **Format:** Comma-separated list of external research group names
- **Example:** `"University of São Paulo, MIT Research Lab, Stanford AI Group"`

### Behavior

When importing research projects, the system will:

1. **Parse External Groups:** Split the `GrupoPesquisaExterno` field by commas
2. **Create if Not Exists:** For each external group name:
   - Search for existing organizational unit (by name or short_name, case-insensitive)
   - If not found, create a new organizational unit with:
     - **Name:** Normalized to Title Case
     - **Short Name:** Auto-generated acronym or truncated name
     - **Type:** Research
     - **Organization:** "External Organizations"
     - **Campus:** "External" (code: EXTERNAL)
     - **Knowledge Area:** Inherited from the initiative's knowledge area
3. **Associate with Initiative:** Add the initiative to the external group's initiatives
4. **Sync Knowledge Areas:** Update the external group's knowledge areas from associated initiatives

### Auto-Generated Defaults

External research groups are created with these defaults:

| Field | Value | Description |
|-------|-------|-------------|
| Organization | "External Organizations" | Special organization for external groups |
| Campus | "External" (EXTERNAL) | Special campus for external entities |
| Type | Research | Organizational type |
| Short Name | Auto-generated | Acronym from words or truncated name |
| Knowledge Area | From initiative | Inherited from the research project |

### Short Name Generation

The system generates short names automatically:
- **Multiple words:** Creates acronym (e.g., "Massachusetts Institute of Technology" → "MIT")
- **Single word:** Truncates to 20 characters (e.g., "Stanford" → "STANFORD")
- **Limit:** Maximum 20 characters

## CSV Format Example

```csv
Titulo,Coordenador,EmailCoordenador,Inicio,Fim,Pesquisadores,Estudantes,AreaConhecimento,GrupoPesquisa,GrupoPesquisaExterno
"AI Research Project","Dr. John Smith","john@example.com","2024-01-01","2024-12-31","Jane Doe, Bob Wilson","Alice Brown","Computer Science","Internal Lab","MIT AI Lab, Stanford NLP Group"
```

## Differences: GrupoPesquisa vs GrupoPesquisaExterno

| Feature | GrupoPesquisa | GrupoPesquisaExterno |
|---------|---------------|----------------------|
| **Purpose** | Internal organizational units | External research partners |
| **Creation** | Must exist beforehand | Auto-created if not found |
| **Organization** | Various internal orgs | "External Organizations" |
| **Campus** | Various campuses | "External" campus |
| **Multiple Values** | Single value | Comma-separated list |

## Use Cases

### 1. International Collaborations
```csv
GrupoPesquisaExterno: "University of Oxford, ETH Zurich, Tokyo Institute of Technology"
```

### 2. Industry Partnerships
```csv
GrupoPesquisaExterno: "Google Research, Microsoft Research, IBM Watson"
```

### 3. Mixed Internal/External
```csv
GrupoPesquisa: "Internal AI Lab"
GrupoPesquisaExterno: "MIT CSAIL, Carnegie Mellon Robotics"
```

## Implementation Details

### Code Changes

1. **`apps/initiatives/csv_import/group_handler.py`**
   - Added `get_or_create_external_research_group()` method
   - Added `generate_short_name()` method
   - Creates external groups with proper defaults

2. **`apps/initiatives/csv_import/processor.py`**
   - Added processing for `GrupoPesquisaExterno` field
   - Supports comma-separated multiple groups
   - Associates groups with initiatives

### Database Impact

- Creates new records in `organizational_group_organizationalunit` table
- Creates "External Organizations" organization (once)
- Creates "External" campus (once)
- Uses existing "Research" organizational type

## Benefits

1. **Automatic Creation:** No need to manually create external research groups before import
2. **Collaboration Tracking:** Track external partnerships and collaborations
3. **Knowledge Area Sync:** External groups automatically inherit knowledge areas from projects
4. **Flexible Format:** Support multiple external groups per project
5. **Deduplication:** Prevents duplicate external groups (case-insensitive matching)

## Validation

The import will:
- ✅ Skip empty external group names
- ✅ Normalize names to Title Case
- ✅ Handle duplicate names gracefully
- ✅ Associate knowledge areas automatically
- ✅ Create missing default entities (organization, campus, type)

## Error Handling

- **Empty names:** Silently skipped
- **Duplicate names:** Uses existing unit
- **Race conditions:** Handles concurrent imports
- **Validation errors:** Logged in import report

## Testing

To test the feature:

1. Prepare a CSV with `GrupoPesquisaExterno` column
2. Import via Django admin: `/admin/initiatives/initiative/import-csv/`
3. Check created external groups: `/admin/organizational_group/organizationalunit/`
4. Filter by Organization = "External Organizations"
5. Verify associations in initiative detail pages

## Future Enhancements

Potential improvements:
- Support for external group types (university, industry, government)
- Custom campus assignment for external groups
- Bulk update of external group details
- Import external group metadata (country, website, etc.)
