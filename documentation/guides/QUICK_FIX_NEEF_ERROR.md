# Quick Fix for NEEF Import Error

## The Error You're Seeing

```
Row 251: Validation error: {'short_name': ['An organizational unit with 
short name "NEEF" already exists in organization "Default Organization".']}
```

## Why This Happens

The database constraint hasn't been updated yet. It's still using the old rule that doesn't allow the same short_name on different campuses.

## The Fix (3 Simple Steps)

### Step 1: Open Terminal

Navigate to your project directory where `manage.py` is located.

### Step 2: Run This Command

```bash
python manage.py migrate organizational_group
```

You should see output like:
```
Running migrations:
  Applying organizational_group.0002_allow_same_shortname_different_campus... OK
```

### Step 3: Re-import the CSV

Go back to Django admin and import the CSV again, or run:
```bash
python manage.py import_research_groups example/research_group/research_groups.csv
```

## Done! ✓

The NEEF group at Serra should now import successfully alongside the NEEF group at Cariacica.

---

## Alternative: Check Migration Status First

If you want to verify the migration status before applying:

```bash
python manage.py check_migration_status
```

This will tell you if the migration has been applied or not.

---

## Still Having Issues?

### If you don't have terminal access:

You'll need to ask your system administrator or DevOps team to run:
```bash
python manage.py migrate organizational_group
```

### If you're using Docker:

```bash
docker-compose exec web python manage.py migrate organizational_group
```

### If migration command doesn't work:

Make sure you're in the correct directory and your virtual environment is activated:
```bash
# Check if you're in the right place
ls manage.py  # Should show the file

# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

---

## What Changed?

**Before:** Groups with same short_name couldn't exist in the same organization (even on different campuses)

**After:** Groups with same short_name CAN exist if they're on different campuses

**Database Constraint:**
- Old: `(short_name, organization)` must be unique
- New: `(short_name, organization, campus)` must be unique

This allows:
- ✓ NEEF at Cariacica
- ✓ NEEF at Serra
- ✗ Two NEEF groups at the same campus (still not allowed)
