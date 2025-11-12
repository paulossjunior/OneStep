# How to Apply Migration 0002

## The Problem

You're getting this error because the database still has the old constraint that doesn't allow the same short_name on different campuses. The migration file has been created but not yet applied to the database.

## Solution: Apply the Migration

You need to run the migration to update the database constraint. Here are your options:

### Option 1: Using Terminal (Recommended)

Open a terminal in your project directory and run:

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Apply the migration
python manage.py migrate organizational_group

# Verify it was applied
python manage.py showmigrations organizational_group
```

Expected output:
```
organizational_group
 [X] 0001_initial
 [X] 0002_allow_same_shortname_different_campus
```

### Option 2: Using Docker (if you're using Docker)

```bash
# If using docker-compose
docker-compose exec web python manage.py migrate organizational_group

# Or using make command
make migrate
```

### Option 3: Check Migration Status First

To see if the migration needs to be applied:

```bash
python manage.py showmigrations organizational_group
```

If you see:
```
organizational_group
 [X] 0001_initial
 [ ] 0002_allow_same_shortname_different_campus  ← Not applied yet
```

Then you need to run the migration.

## After Applying the Migration

Once the migration is applied, you can:

1. **Re-run the CSV import** from Django admin
2. **Or use the command line:**
   ```bash
   python manage.py import_research_groups example/research_group/research_groups.csv
   ```

The NEEF group at Serra (row 251) should now import successfully!

## Verification

After import, verify both NEEF groups exist:

```bash
python manage.py shell
```

Then in the Python shell:
```python
from apps.organizational_group.models import OrganizationalUnit

neef_groups = OrganizationalUnit.objects.filter(short_name='NEEF')
print(f"Found {neef_groups.count()} NEEF groups:")
for group in neef_groups:
    print(f"  - {group.name} at {group.campus.name}")
```

Expected output:
```
Found 2 NEEF groups:
  - Núcleo De Estruturação Do Ensino De Física Do Ifes at Cariacica
  - Nucleo De Estudos Em Ensino De Fisica at Serra
```

## Troubleshooting

### If migration fails with "constraint already exists"

This means the old constraint might still be there. You can:

1. Check current constraints:
   ```bash
   python manage.py dbshell
   ```
   
   Then in the database shell:
   ```sql
   -- For PostgreSQL
   SELECT conname FROM pg_constraint WHERE conname LIKE '%short_name%';
   
   -- For SQLite
   .schema organizational_group_organizationalunit
   ```

2. If you see the old constraint, you may need to manually drop it first.

### If you get "No such table" error

Run all migrations:
```bash
python manage.py migrate
```

### If migration was already applied but error persists

The database might have stale data. Try:
```bash
# Check migration status
python manage.py showmigrations organizational_group

# If it shows as applied, try fake-rolling back and re-applying
python manage.py migrate organizational_group 0001_initial --fake
python manage.py migrate organizational_group
```

## Need Help?

If you're still having issues, please provide:
1. Output of `python manage.py showmigrations organizational_group`
2. Your database type (PostgreSQL, SQLite, MySQL, etc.)
3. Any error messages you're seeing
