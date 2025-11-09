.PHONY: help up down build logs restart ps shell migrate createsuperuser test clean prune backup restore prod-up prod-down prod-build prod-logs prod-shell prod-migrate prod-backup prod-restore

# Default target - show help
help:
	@echo "OneStep Docker Management Commands"
	@echo "==================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  make up              - Start all services (development)"
	@echo "  make down            - Stop all services gracefully"
	@echo "  make build           - Build/rebuild containers"
	@echo "  make logs            - View service logs"
	@echo "  make restart         - Restart all services"
	@echo "  make ps              - Show running containers"
	@echo ""
	@echo "Django Management Commands:"
	@echo "  make shell           - Open Django container shell"
	@echo "  make migrate         - Run database migrations"
	@echo "  make createsuperuser - Create Django admin superuser"
	@echo "  make test            - Run tests in container"
	@echo ""
	@echo "Database Commands:"
	@echo "  make backup          - Backup development database"
	@echo "  make restore         - Restore development database (requires BACKUP_FILE=path)"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-up         - Start all services (production)"
	@echo "  make prod-down       - Stop production services"
	@echo "  make prod-build      - Build production containers"
	@echo "  make prod-logs       - View production logs"
	@echo "  make prod-shell      - Open production container shell"
	@echo "  make prod-migrate    - Run production migrations"
	@echo "  make prod-backup     - Backup production database"
	@echo "  make prod-restore    - Restore production database"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean           - Stop services and remove volumes"
	@echo "  make prune           - Remove all unused Docker resources"
	@echo ""

# Basic Docker Compose Commands (Task 5.1)

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started successfully!"
	@echo "Django application: http://localhost:8000"
	@echo "Django admin: http://localhost:8000/admin/"

# Stop all services gracefully
down:
	@echo "Stopping all services gracefully..."
	docker-compose down
	@echo "Services stopped successfully!"

# Build or rebuild containers
build:
	@echo "Building/rebuilding containers..."
	docker-compose build --no-cache
	@echo "Build completed successfully!"

# View service logs
logs:
	@echo "Viewing service logs (Ctrl+C to exit)..."
	docker-compose logs -f

# Restart all services
restart:
	@echo "Restarting all services..."
	docker-compose restart
	@echo "Services restarted successfully!"

# Show running containers
ps:
	@echo "Running containers:"
	docker-compose ps

# Django Management Commands (Task 5.2)

# Open Django container shell
shell:
	@echo "Opening Django container shell..."
	docker-compose exec web /bin/bash

# Run database migrations
migrate:
	@echo "Running database migrations..."
	docker-compose exec web python manage.py migrate
	@echo "Migrations completed successfully!"


makemigrations:
	@echo "Running database migrations..."
	docker-compose exec web python manage.py makemigrations
	@echo "Migrations completed successfully!"

# Create Django admin superuser
createsuperuser:
	@echo "Creating Django admin superuser..."
	docker-compose exec web python manage.py createsuperuser

# Run tests in container
test:
	@echo "Running tests in container..."
	docker-compose exec web python manage.py test
	@echo "Tests completed!"

# Database Commands

# Backup development database
backup:
	@echo "Backing up development database..."
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U postgres onestep_dev > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup completed! Check backups/ directory."

# Restore development database
restore:
	@echo "Restoring development database..."
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "ERROR: Please specify BACKUP_FILE=path/to/backup.sql"; \
		echo "Example: make restore BACKUP_FILE=backups/backup_20240101_120000.sql"; \
		exit 1; \
	fi
	@echo "WARNING: This will overwrite the current database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cat $(BACKUP_FILE) | docker-compose exec -T db psql -U postgres onestep_dev; \
		echo "Database restored successfully!"; \
	else \
		echo "Restore cancelled."; \
	fi

# Utility Commands

# Stop services and remove volumes
clean:
	@echo "Stopping services and removing volumes..."
	docker-compose down -v
	@echo "Cleanup completed!"

# Remove all unused Docker resources
prune:
	@echo "Removing all unused Docker resources..."
	docker system prune -af --volumes
	@echo "Prune completed!"

# Production Commands (Task 6.1)

# Start production services
prod-up:
	@echo "Starting production services..."
	@if [ ! -f .env.prod ]; then \
		echo "ERROR: .env.prod file not found!"; \
		echo "Please copy .env.prod.example to .env.prod and configure it."; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
	@echo "Production services started successfully!"
	@echo "Application: http://localhost:8000"

# Stop production services
prod-down:
	@echo "Stopping production services..."
	docker-compose -f docker-compose.prod.yml down
	@echo "Production services stopped successfully!"

# Build production containers
prod-build:
	@echo "Building production containers..."
	docker-compose -f docker-compose.prod.yml build --no-cache
	@echo "Production build completed successfully!"

# View production logs
prod-logs:
	@echo "Viewing production logs (Ctrl+C to exit)..."
	docker-compose -f docker-compose.prod.yml logs -f

# Open production container shell
prod-shell:
	@echo "Opening production container shell..."
	docker-compose -f docker-compose.prod.yml exec web /bin/bash

# Run production migrations
prod-migrate:
	@echo "Running production database migrations..."
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
	@echo "Production migrations completed successfully!"

# Backup production database
prod-backup:
	@echo "Backing up production database..."
	@mkdir -p backups
	docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $${POSTGRES_USER} $${POSTGRES_DB} > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backup completed! Check backups/ directory."

# Restore production database
prod-restore:
	@echo "Restoring production database..."
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "ERROR: Please specify BACKUP_FILE=path/to/backup.sql"; \
		exit 1; \
	fi
	@echo "WARNING: This will overwrite the current database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f docker-compose.prod.yml exec -T db psql -U $${POSTGRES_USER} $${POSTGRES_DB} < $(BACKUP_FILE); \
		echo "Database restored successfully!"; \
	else \
		echo "Restore cancelled."; \
	fi
