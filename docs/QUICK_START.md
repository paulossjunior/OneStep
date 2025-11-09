# Quick Start: CSV Import

## Access the Feature

1. **Start the server**:
   ```bash
   python manage.py runserver
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000/admin/
   ```

3. **Log in** with your superuser credentials

4. **Navigate to Organizational Groups**:
   - Click on "Organizational Groups" in the admin menu
   - Or go directly to: `http://localhost:8000/admin/organizational_group/organizationalgroup/`

5. **Click "Import from CSV"**:
   - Look for the button in the top right corner
   - It's next to the "Add Organizational Group" button

6. **Upload your CSV file**:
   - Click "Choose File"
   - Select your CSV file (or use `examples/sample_research_groups.csv`)
   - Click "Import"

7. **Review the results**:
   - Green messages = Success
   - Yellow messages = Warnings (duplicates skipped)
   - Red messages = Errors (with row numbers)

## Try the Sample File

Use the included sample file to test:

```bash
examples/sample_research_groups.csv
```

This file contains 5 research groups with various scenarios:
- Groups with multiple leaders
- Groups with single leaders
- Groups with and without repository URLs
- Groups with and without short names

## What Gets Created

When you import the sample file, the system will create:

- **5 Organizational Groups** (or fewer if duplicates exist)
- **4 Campus records**: Main Campus, North Campus, South Campus, East Campus
- **5 Knowledge Areas**: Computer Science, Biology, Chemistry, Physics, Mathematics
- **7 Person records**: John Doe, Jane Smith, Alice Johnson, Bob Wilson, Carol Davis, David Brown, Eve Martinez
- **Leadership relationships** linking people to groups

## Verify the Import

After importing, check:

1. **Organizational Groups list** - Should show the imported groups
2. **Campus list** - Should show the new campuses
3. **Knowledge Areas list** - Should show the new knowledge areas
4. **People list** - Should show the new people

## Common First-Time Issues

### "Please select a CSV file to upload"
- Make sure you clicked "Choose File" and selected a file

### "File must be a CSV file"
- Ensure your file has a .csv extension

### "Nome (name) is required"
- Check that your CSV has a header row
- Verify the column name is exactly "Nome"

### No errors but nothing imported
- Check if the groups already exist (duplicates are skipped)
- Look for yellow warning messages about skipped duplicates

## Next Steps

Once you've successfully imported the sample file:

1. **Create your own CSV** following the format
2. **Export existing data** to see the structure
3. **Import your real data** in batches
4. **Review and verify** each import

For detailed information, see:
- `docs/CSV_IMPORT_GUIDE.md` - Complete user guide
- `apps/organizational_group/csv_import/README.md` - Technical documentation
