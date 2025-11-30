# Development Workflow Guide

This guide covers the day-to-day development workflow using Docker for the OneStep project.

## Table of Contents

- [Getting Started](#getting-started)
- [Hot-Reload Development](#hot-reload-development)
- [Database Management](#database-management)
- [Testing Workflow](#testing-workflow)
- [Debugging](#debugging)
- [Backup and Restore](#backup-and-restore)
- [Production Deployment](#production-deployment)

## Getting Started

### Initial Setup

1. **Clone the repository and navigate to the project:**
   ```bash
   cd onestep
   ```

2. **Start the development environment:**
   ```bash
   make up
   ```
   
   This command will:
   - Build Docker images if they don't exist
   - Start PostgreSQL database
   - Start Django application
   - Run database migrations automatically
   - Collect static files

3. **Create your admin user:**
   ```bash
   make createsuperuser
   ```

4. **Access the application:**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

### Daily Workflow

```bash
# Start your day
make up

# View logs while developing
make logs

# Stop at end of day
make down
```

## Hot-Reload Development

The Docker development environment is configured for hot-reload, meaning code changes are reflected immediately without restarting containers.

### How It Works

- **Source code mounting**: Your local `apps/` and `onestep/` directories are mounted into the container
- **Django auto-reload**: Django's development server watches for file changes
- **Instant feedback**: Save a file and see changes immediately

### What Triggers Reload

✅ **Automatically reloads:**
- Python code changes (`.py` files)
- Template changes (if using templates)
- Most configuration changes

❌ **Requires restart:**
- Changes to `requirements.txt`
- Changes to environment variables
- Changes to Docker configuration files

### Making Code Changes

1. **Edit Python files** in your local editor (VSCode, etc.)
   ```python
   # apps/people/models.py
   class Person(models.Model):
       first_name = models.CharField(max_length=100)
       # Add new field
       middle_name = models.CharField(max_length=100, blank=True)
   ```

2. **Save the file** - Django automatically reloads

3. **Create and run migrations** for model changes:
   ```bash
   make migrate
   ```

4. **View changes** in your browser or API client

### When to Restart Containers

If you modify:
- **Dependencies**: `requirements.txt`
  ```bash
  make build
  make up
  ```

- **Environment variables**: `.env.dev`
  ```bash
  make down
  make up
  ```

- **Docker configuration**: `Dockerfile`, `docker-compose.yml`
  ```bash
  make build
  make up
  ```

## Database Management

### Running Migrations

```bash
# Create new migrations after model changes
docker-compose exec web python manage.py makemigrations

# Apply migrations
make migrate

# View migration status
docker-compose exec web python manage.py showmigrations

# Rollback to specific migration
docker-compose exec web python manage.py migrate app_name migration_name
```

### Accessing the Database

#### Using Django Shell

```bash
# Open Django shell
make shell

# Then in the shell:
from apps.people.models import Person
Person.objects.all()
```

#### Using PostgreSQL Shell

```bash
# Access PostgreSQL directly
docker-compose exec db psql -U postgres -d onestep_dev

# Common PostgreSQL commands:
\dt              # List tables
\d table_name    # Describe table
\q               # Quit
```

#### Using Database GUI Tools

Connect to PostgreSQL using tools like pgAdmin, DBeaver, or TablePlus:

- **Host**: localhost
- **Port**: 5432
- **Database**: onestep_dev
- **Username**: postgres
- **Password**: postgres

### Resetting the Database

```bash
# Complete reset (deletes all data)
make clean
make up

# Or manually:
docker-compose down -v
docker-compose up
```

### Sample Data

```bash
# Load sample data (if fixtures exist)
docker-compose exec web python manage.py loaddata sample_people
docker-compose exec web python manage.py loaddata sample_initiatives

# Create custom sample data
docker-compose exec web python manage.py create_sample_data
```

## Testing Workflow

### Running Tests

```bash
# Run all tests
make test

# Run specific app tests
docker-compose exec web python manage.py test apps.people

# Run specific test file
docker-compose exec web python manage.py test apps.people.tests.test_models

# Run with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

### Test-Driven Development

1. **Write a failing test:**
   ```python
   # apps/people/tests/test_models.py
   def test_person_full_name(self):
       person = Person.objects.create(
           first_name="John",
           last_name="Doe"
       )
       self.assertEqual(person.full_name, "John Doe")
   ```

2. **Run the test** (it should fail):
   ```bash
   make test
   ```

3. **Implement the feature:**
   ```python
   # apps/people/models.py
   class Person(models.Model):
       # ... fields ...
       
       @property
       def full_name(self):
           return f"{self.first_name} {self.last_name}"
   ```

4. **Run the test again** (it should pass):
   ```bash
   make test
   ```

## Debugging

### Viewing Logs

```bash
# All services
make logs

# Specific service
docker-compose logs -f web
docker-compose logs -f db

# Last N lines
docker-compose logs --tail=100 web
```

### Using Python Debugger

1. **Add breakpoint in code:**
   ```python
   import pdb; pdb.set_trace()
   ```

2. **Attach to container:**
   ```bash
   docker attach $(docker-compose ps -q web)
   ```

3. **Debug interactively** when breakpoint is hit

4. **Detach without stopping**: `Ctrl+P` then `Ctrl+Q`

### Inspecting Container

```bash
# Open shell in running container
make shell

# Check environment variables
docker-compose exec web env

# Check installed packages
docker-compose exec web pip list

# Check Django configuration
docker-compose exec web python manage.py diffsettings
```

## Backup and Restore

### Database Backup

#### Quick Backup

```bash
# Backup database using make command
make backup

# This creates a timestamped backup file in backups/ directory
# Example: backups/backup_20240101_120000.sql
```

#### Scheduled Backups

Create a backup script:

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres onestep_dev > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
echo "Backup created: backup_$TIMESTAMP.sql"
```

Make it executable and run:
```bash
chmod +x backup.sh
./backup.sh
```

### Database Restore

```bash
# Restore from backup file using make command
make restore BACKUP_FILE=backups/backup_20240101_120000.sql

# You will be prompted to confirm before overwriting the database
```

### Full Environment Backup

```bash
# Backup database
docker-compose exec db pg_dump -U postgres onestep_dev > db_backup.sql

# Backup media files (if any)
docker cp $(docker-compose ps -q web):/app/media ./media_backup

# Backup environment configuration
cp .env.dev .env.dev.backup
```

### Restore Full Environment

```bash
# Restore database
cat db_backup.sql | docker-compose exec -T db psql -U postgres -d onestep_dev

# Restore media files
docker cp ./media_backup $(docker-compose ps -q web):/app/media

# Restore environment
cp .env.dev.backup .env.dev
make down
make up
```

## Production Deployment

### Building for Production

```bash
# Use production Docker Compose configuration
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### Production Environment Setup

1. **Create production environment file:**
   ```bash
   cp .env.prod.example .env.prod
   ```

2. **Update production variables:**
   ```bash
   # .env.prod
   DEBUG=0
   SECRET_KEY=your-secure-random-secret-key
   POSTGRES_DB=onestep_prod
   POSTGRES_USER=onestep_user
   POSTGRES_PASSWORD=secure-password-here
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

3. **Deploy:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Production Checklist

See [PRODUCTION.md](PRODUCTION.md) for complete production deployment checklist.

Key considerations:
- ✅ Set `DEBUG=0`
- ✅ Use strong `SECRET_KEY`
- ✅ Configure `ALLOWED_HOSTS`
- ✅ Set up HTTPS/SSL
- ✅ Configure proper database credentials
- ✅ Set up automated backups
- ✅ Configure logging and monitoring
- ✅ Use Gunicorn instead of Django dev server
- ✅ Serve static files properly
- ✅ Set up health checks

## Best Practices

### Development Workflow

1. **Always use version control:**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git add .
   git commit -m "Add new feature"
   ```

2. **Keep containers updated:**
   ```bash
   # Rebuild after pulling changes
   git pull
   make build
   make up
   ```

3. **Clean up regularly:**
   ```bash
   # Remove unused Docker resources
   docker system prune
   ```

4. **Use meaningful commit messages:**
   ```bash
   git commit -m "Add Person model with email validation"
   ```

### Database Workflow

1. **Always create migrations for model changes**
2. **Test migrations before committing**
3. **Never edit migration files manually** (unless you know what you're doing)
4. **Backup before major migrations**
5. **Use descriptive migration names**

### Testing Workflow

1. **Write tests before or alongside features**
2. **Run tests before committing**
3. **Maintain high test coverage**
4. **Test both success and failure cases**
5. **Use factories or fixtures for test data**

## Quick Reference

### Essential Commands

```bash
# Start development
make up

# Stop development
make down

# View logs
make logs

# Run migrations
make migrate

# Access Django shell
make shell

# Run tests
make test

# Create superuser
make createsuperuser

# Backup database
make backup

# Restore database
make restore BACKUP_FILE=backups/backup_20240101_120000.sql

# Rebuild containers
make build

# Complete reset
make clean && make up
```

### File Locations

- **Source code**: `apps/`, `onestep/`
- **Database data**: Docker volume `postgres_data`
- **Static files**: Docker volume `static_volume`
- **Logs**: `logs/django.log`
- **Environment**: `.env.dev`, `.env.prod`
- **Docker config**: `docker-compose.yml`, `docker-compose.prod.yml`

### Useful Docker Commands

```bash
# List running containers
docker-compose ps

# View resource usage
docker stats

# Remove all stopped containers
docker-compose rm

# View Docker volumes
docker volume ls

# Inspect a volume
docker volume inspect onestep_postgres_data
```
