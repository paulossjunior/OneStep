# CSV Import Guide for Research Groups

This guide explains how to import research group data into the OneStep system using CSV files.

## Quick Start

1. **Access the Admin Interface**
   - Log in to the Django admin at `/admin/`
   - Navigate to "Organizational Groups"

2. **Start Import**
   - Click the "Import from CSV" button in the top right corner
   - You'll see a file upload form

3. **Upload Your CSV**
   - Click "Choose File" and select your CSV file
   - Click "Import" to start the process

4. **Review Results**
   - You'll see a summary of:
     - Successfully imported groups
     - Skipped duplicates
     - Any errors that occurred

## CSV File Requirements

### Required Columns

Your CSV file must include these columns with exact names:

- `Nome` - Full group name (required)
- `Unidade` - Campus name (required)
- `AreaConhecimento` - Knowledge area (required)

### Optional Columns

- `Sigla` - Group abbreviation (auto-generated if empty)
- `repositorio` - Repository URL
- `Site` - Website URL (not imported, for reference only)
- `Lideres` - Leaders in format "Name (email), Name (email)"

### File Format

- **Encoding**: UTF-8 (with or without BOM)
- **Extension**: .csv
- **Header Row**: Required (first row must contain column names)
- **Delimiter**: Comma (,)

## Example CSV

```csv
Sigla,Nome,repositorio,Site,AreaConhecimento,Unidade,Lideres
AI,Artificial Intelligence Lab,https://github.com/ai-lab,https://ai-lab.example.com,Computer Science,Main Campus,"John Doe (john.doe@example.com), Jane Smith (jane.smith@example.com)"
BIO,Biology Research Group,https://github.com/bio-group,https://bio.example.com,Biology,North Campus,"Alice Johnson (alice.johnson@example.com)"
CHEM,Chemistry Lab,https://github.com/chem-lab,,Chemistry,Main Campus,"Bob Wilson (bob.wilson@example.com)"
```

A sample file is available at `examples/sample_research_groups.csv`.

## Leader Format

Leaders must be formatted as: `Name (email)`

Multiple leaders are separated by commas:
```
"John Doe (john@example.com), Jane Smith (jane@example.com)"
```

**Important**: Wrap multiple leaders in quotes to handle the comma delimiter properly.

## What Happens During Import

### Automatic Record Creation

The import process automatically creates records for:

1. **Campus** - If a campus with the given name doesn't exist
   - Name is matched case-insensitively
   - Code is auto-generated from the name

2. **Knowledge Area** - If a knowledge area doesn't exist
   - Name is matched case-insensitively
   - Created with the exact name from CSV

3. **Person** - If a person with the given email doesn't exist
   - Email is matched case-insensitively
   - Name is updated if person exists but name differs

4. **Organizational Group** - If not a duplicate
   - Type is set to "Research"
   - Short name is auto-generated if not provided

### Duplicate Handling

Groups are considered duplicates if they have:
- Same short name (case-insensitive)
- Same campus

Duplicate groups are **skipped** and reported in the summary.

### Leadership Assignment

- Leaders are linked through OrganizationalGroupLeadership
- Start date is set to the import date
- Status is set to active

## Validation

The import validates:

- ✓ Required fields are present
- ✓ Email addresses are valid format
- ✓ URLs are valid format (if provided)
- ✓ Leader format matches "Name (email)"

Invalid rows are skipped and errors are reported.

## Error Handling

The import uses **per-row transactions**:

- If a row fails, only that row is rolled back
- Other rows continue to be processed
- All errors are logged with row numbers
- You can fix errors and re-import

## Tips for Success

### Preparing Your CSV

1. **Use UTF-8 encoding** - Most spreadsheet programs support this
2. **Include header row** - Column names must match exactly
3. **Quote multi-value fields** - Especially for multiple leaders
4. **Validate emails** - Ensure all email addresses are correct
5. **Check URLs** - Must start with http:// or https://

### Excel Users

When saving from Excel:
1. Choose "CSV UTF-8 (Comma delimited) (*.csv)"
2. This ensures proper encoding and format

### Google Sheets Users

1. File → Download → Comma-separated values (.csv)
2. The file will be in UTF-8 format

### Common Issues

**Issue**: "Nome (name) is required"
- **Solution**: Ensure the Nome column has values for all rows

**Issue**: "Invalid email for leader"
- **Solution**: Check email format in Lideres column

**Issue**: "Invalid repository URL"
- **Solution**: URLs must start with http:// or https://

**Issue**: "Skipped duplicate"
- **Solution**: This is normal - the group already exists

## After Import

### Verify Your Data

1. Check the import summary for success count
2. Review any errors or skipped rows
3. Navigate to the Organizational Groups list
4. Verify the imported groups appear correctly

### Fix Errors

If errors occurred:
1. Note the row numbers from error messages
2. Fix the issues in your CSV file
3. Re-import the file
4. Duplicate groups will be skipped automatically

## Advanced Usage

### Bulk Updates

To update existing groups:
1. Export current data
2. Modify the CSV
3. Delete old groups (if needed)
4. Re-import with updated data

### Incremental Imports

You can import multiple CSV files:
- Duplicates are automatically skipped
- New groups are added
- Existing people and campuses are reused

## Support

For issues or questions:
1. Check error messages for specific row numbers
2. Verify CSV format matches requirements
3. Review the example CSV file
4. Contact system administrator if problems persist

## Technical Details

For developers and technical users, see:
- `apps/organizational_group/csv_import/README.md` - Component documentation
- `.kiro/specs/csv-import/` - Full specification and design documents
