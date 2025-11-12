# Migration: Allow Zero Scholarship Values

## Problem

Scholarships with `Valor` = 0, blank, or empty were not being imported because the database had a constraint requiring `value > 0`.

## Solution

Updated the database constraint to allow `value >= 0` (zero or greater).

## Changes Made

1. **Model Updated** (`apps/scholarships/models.py`):
   - Changed constraint from `value__gt=0` to `value__gte=0`
   - Renamed constraint from `scholarship_value_positive` to `scholarship_value_non_negative`

2. **Migration Created** (`0004_allow_zero_scholarship_value.py`):
   - Removes old constraint
   - Adds new constraint allowing zero values

3. **CSV Import Updated**:
   - Empty/blank Valor fields default to 0
   - Validation allows zero values
   - Only negative values are rejected

## Apply the Migration

Run this command to update the database:

```bash
python manage.py migrate scholarships
```

Expected output:
```
Running migrations:
  Applying scholarships.0004_allow_zero_scholarship_value... OK
```

## After Migration

You can now:
- Import scholarships with `Valor` = 0
- Import scholarships with blank/empty `Valor` (defaults to 0)
- Create scholarships with value = 0 through admin

## Use Cases for Zero Value Scholarships

Zero-value scholarships are useful for:
- **Voluntary scholarships** (Voluntário) - No monetary value
- **Pending scholarships** - Value not yet determined
- **In-kind scholarships** - Non-monetary benefits
- **Historical records** - Scholarships that had no stipend

## Validation Rules

After this change:
- ✓ Value can be 0
- ✓ Value can be any positive number
- ✗ Value cannot be negative

## Re-import CSV

After applying the migration, re-import your CSV file:

1. Via Django Admin:
   - Go to Scholarships
   - Click "Import from CSV"
   - Select your file
   - Click "Import"

2. Via Command Line:
   ```bash
   python manage.py import_scholarships example/scholarship/scholarship.csv
   ```

Scholarships with zero or empty values will now be imported successfully!
