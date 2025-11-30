.PHONY: help install dev prod test clean migrate backup restore docker-up docker-down superset-backup superset-restore

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

##@ General

help: ## Display this help message
	@echo "$(BLUE)OneStep - Django REST API with Superset$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Setup

install: ## Install dependencies in virtual environment
	@echo "$(BLUE)Installing dependencies...$(NC)"
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev: ## Start development server
	@echo "$(BLUE)Starting development server...$(NC)"
	. venv/bin/activate && python manage.py runserver

shell: ## Open Django shell
	@echo "$(BLUE)Opening Django shell...$(NC)"
	. venv/bin/activate && python manage.py shell

##@ Database

migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	. venv/bin/activate && python manage.py migrate
	@echo "$(GREEN)✓ Migrations complete$(NC)"

makemigrations: ## Create new migrations
	@echo "$(BLUE)Creating migrations...$(NC)"
	. venv/bin/activate && python manage.py makemigrations
	@echo "$(GREEN)✓ Migrations created$(NC)"

migrate-app: ## Run migrations for specific app (usage: make migrate-app APP=initiatives)
	@echo "$(BLUE)Running migrations for $(APP)...$(NC)"
	. venv/bin/activate && python manage.py migrate $(APP)
	@echo "$(GREEN)✓ Migrations complete for $(APP)$(NC)"

showmigrations: ## Show migration status
	. venv/bin/activate && python manage.py showmigrations

dbshell: ## Open database shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	. venv/bin/activate && python manage.py dbshell

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	. venv/bin/activate && python manage.py test

test-app: ## Run tests for specific app (usage: make test-app APP=initiatives)
	@echo "$(BLUE)Running tests for $(APP)...$(NC)"
	. venv/bin/activate && python manage.py test $(APP)

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	. venv/bin/activate && coverage run --source='.' manage.py test
	. venv/bin/activate && coverage report
	. venv/bin/activate && coverage html
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

##@ Code Quality

lint: ## Run linting (flake8)
	@echo "$(BLUE)Running linter...$(NC)"
	. venv/bin/activate && flake8 .

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	. venv/bin/activate && black .
	@echo "$(GREEN)✓ Code formatted$(NC)"

check: ## Run Django system checks
	@echo "$(BLUE)Running system checks...$(NC)"
	. venv/bin/activate && python manage.py check
	@echo "$(GREEN)✓ System checks passed$(NC)"

##@ Docker Operations

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose -f docker-compose.superset.yml build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start all Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose -f docker-compose.superset.yml up -d
	@echo "$(GREEN)✓ Containers started$(NC)"
	@echo "$(YELLOW)Django Admin: http://localhost:8000/admin/$(NC)"
	@echo "$(YELLOW)Superset: http://localhost:8088$(NC)"

docker-down: ## Stop all Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose -f docker-compose.superset.yml down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

docker-restart: ## Restart all Docker containers
	@echo "$(BLUE)Restarting Docker containers...$(NC)"
	docker-compose -f docker-compose.superset.yml restart
	@echo "$(GREEN)✓ Containers restarted$(NC)"

docker-logs: ## Show Docker container logs
	docker-compose -f docker-compose.superset.yml logs -f

docker-logs-web: ## Show Django web container logs
	docker logs -f onestep_web

docker-logs-superset: ## Show Superset container logs
	docker logs -f superset

docker-logs-db: ## Show database container logs
	docker logs -f onestep_db

docker-ps: ## Show running containers
	docker-compose -f docker-compose.superset.yml ps

docker-clean: ## Remove all containers, volumes, and images
	@echo "$(RED)WARNING: This will remove all containers, volumes, and images!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose -f docker-compose.superset.yml down -v --rmi all; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	else \
		echo "$(YELLOW)Cleanup cancelled$(NC)"; \
	fi
docker-makemigrations: ## Create new migrations
	@echo "$(BLUE)Creating migrations...$(NC)"
	docker-compose -f docker-compose.superset.yml exec web python manage.py makemigrations
	@echo "$(GREEN)✓ Migrations created$(NC)"

docker-migrate: ## Create new migrations
	@echo "$(BLUE)Creating migrations...$(NC)"
	docker-compose -f docker-compose.superset.yml exec web python manage.py migrate
	@echo "$(GREEN)✓ Migrations created$(NC)"

docker-createsuperuser: ## Create new migrations
	@echo "$(BLUE)Creating migrations...$(NC)"
	docker-compose -f docker-compose.superset.yml exec web python manage.py createsuperuser
	@echo "$(GREEN)✓ Migrations created$(NC)"

##@ Superset Management

superset-init: ## Initialize Superset (first time setup)
	@echo "$(BLUE)Initializing Superset...$(NC)"
	docker exec superset superset db upgrade
	docker exec superset superset fab create-admin \
		--username admin \
		--firstname Admin \
		--lastname User \
		--email admin@superset.com \
		--password admin
	docker exec superset superset init
	@echo "$(GREEN)✓ Superset initialized$(NC)"
	@echo "$(YELLOW)Login at http://localhost:8088 with admin/admin$(NC)"

superset-upgrade: ## Upgrade Superset database
	@echo "$(BLUE)Upgrading Superset database...$(NC)"
	docker exec superset superset db upgrade
	@echo "$(GREEN)✓ Superset database upgraded$(NC)"

superset-shell: ## Open Superset container shell
	@echo "$(BLUE)Opening Superset shell...$(NC)"
	docker exec -it superset bash

##@ Superset Backup & Restore

superset-backup: ## Create Superset backup with timestamp
	@echo "$(BLUE)Creating Superset backup...$(NC)"
	@chmod +x scripts/backup_superset.sh
	@./scripts/backup_superset.sh
	@echo "$(GREEN)✓ Backup complete$(NC)"

superset-backup-named: ## Create named Superset backup (usage: make superset-backup-named NAME=my_backup)
	@if [ -z "$(NAME)" ]; then \
		echo "$(RED)Error: NAME parameter required$(NC)"; \
		echo "$(YELLOW)Usage: make superset-backup-named NAME=my_backup$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating Superset backup: $(NAME)...$(NC)"
	@chmod +x scripts/backup_superset.sh
	@./scripts/backup_superset.sh $(NAME)
	@echo "$(GREEN)✓ Backup complete: $(NAME)$(NC)"

superset-backup-daily: ## Create daily backup
	@echo "$(BLUE)Creating daily Superset backup...$(NC)"
	@chmod +x scripts/backup_superset.sh
	@./scripts/backup_superset.sh daily_$(shell date +%Y%m%d)
	@echo "$(GREEN)✓ Daily backup complete$(NC)"

superset-backup-weekly: ## Create weekly backup
	@echo "$(BLUE)Creating weekly Superset backup...$(NC)"
	@chmod +x scripts/backup_superset.sh
	@./scripts/backup_superset.sh weekly_$(shell date +%Y_week%U)
	@echo "$(GREEN)✓ Weekly backup complete$(NC)"

superset-backup-pre-upgrade: ## Create backup before upgrade
	@echo "$(BLUE)Creating pre-upgrade Superset backup...$(NC)"
	@chmod +x scripts/backup_superset.sh
	@./scripts/backup_superset.sh pre_upgrade_$(shell date +%Y%m%d_%H%M%S)
	@echo "$(GREEN)✓ Pre-upgrade backup complete$(NC)"

superset-restore: ## Restore Superset from backup (usage: make superset-restore BACKUP=backup_name)
	@chmod +x scripts/restore_superset.sh
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(YELLOW)Available backups:$(NC)"; \
		./scripts/restore_superset.sh; \
		echo ""; \
		echo "$(BLUE)Usage: make superset-restore BACKUP=backup_name$(NC)"; \
	else \
		echo "$(BLUE)Restoring Superset from: $(BACKUP)...$(NC)"; \
		./scripts/restore_superset.sh $(BACKUP); \
		echo "$(GREEN)✓ Restore complete$(NC)"; \
	fi

superset-list-backups: ## List all Superset backups with details
	@echo "$(BLUE)Available Superset backups:$(NC)"
	@echo ""
	@if [ -d "backups/superset" ] && [ -n "$$(ls -A backups/superset/*.tar.gz 2>/dev/null)" ]; then \
		ls -lht backups/superset/*.tar.gz | awk '{printf "  %-40s %5s %s %s %s\n", $$9, $$5, $$6, $$7, $$8}'; \
		echo ""; \
		echo "$(YELLOW)Total size: $$(du -sh backups/superset 2>/dev/null | cut -f1)$(NC)"; \
		echo ""; \
		echo "$(BLUE)To restore: make superset-restore BACKUP=<backup_name>$(NC)"; \
	else \
		echo "$(YELLOW)  No backups found$(NC)"; \
		echo ""; \
		echo "$(BLUE)Create a backup: make superset-backup$(NC)"; \
	fi

superset-backup-info: ## Show backup information (usage: make superset-backup-info BACKUP=backup_name)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)Error: BACKUP parameter required$(NC)"; \
		echo "$(YELLOW)Usage: make superset-backup-info BACKUP=backup_name$(NC)"; \
		exit 1; \
	fi
	@if [ -f "backups/superset/$(BACKUP).tar.gz" ]; then \
		echo "$(BLUE)Backup Information: $(BACKUP)$(NC)"; \
		echo ""; \
		echo "File: backups/superset/$(BACKUP).tar.gz"; \
		echo "Size: $$(du -h backups/superset/$(BACKUP).tar.gz | cut -f1)"; \
		echo "Date: $$(stat -c %y backups/superset/$(BACKUP).tar.gz 2>/dev/null || stat -f %Sm backups/superset/$(BACKUP).tar.gz)"; \
		echo ""; \
		echo "$(BLUE)Contents:$(NC)"; \
		tar tzf backups/superset/$(BACKUP).tar.gz | head -20; \
		echo ""; \
		echo "$(BLUE)To restore: make superset-restore BACKUP=$(BACKUP)$(NC)"; \
	else \
		echo "$(RED)Backup not found: $(BACKUP)$(NC)"; \
		echo ""; \
		$(MAKE) superset-list-backups; \
	fi

superset-cleanup-backups: ## Remove old backups (keeps last 7)
	@echo "$(BLUE)Cleaning up old Superset backups...$(NC)"
	@if [ -d "backups/superset" ]; then \
		cd backups/superset && ls -t backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm -f; \
		remaining=$$(ls -1 backup_*.tar.gz 2>/dev/null | wc -l); \
		echo "$(GREEN)✓ Cleanup complete. $$remaining backup(s) remaining$(NC)"; \
	else \
		echo "$(YELLOW)No backups directory found$(NC)"; \
	fi

##@ Data Management

loaddata: ## Load fixture data (usage: make loaddata FIXTURE=fixture_name)
	@echo "$(BLUE)Loading fixture: $(FIXTURE)...$(NC)"
	. venv/bin/activate && python manage.py loaddata $(FIXTURE)
	@echo "$(GREEN)✓ Fixture loaded$(NC)"

dumpdata: ## Dump data to fixture (usage: make dumpdata APP=app_name MODEL=model_name)
	@echo "$(BLUE)Dumping data...$(NC)"
	. venv/bin/activate && python manage.py dumpdata $(APP).$(MODEL) --indent 2 > fixtures/$(APP)_$(MODEL).json
	@echo "$(GREEN)✓ Data dumped to fixtures/$(APP)_$(MODEL).json$(NC)"

flush: ## Flush database (WARNING: deletes all data)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		. venv/bin/activate && python manage.py flush --noinput; \
		echo "$(GREEN)✓ Database flushed$(NC)"; \
	else \
		echo "$(YELLOW)Flush cancelled$(NC)"; \
	fi

##@ User Management

createsuperuser: ## Create Django superuser
	@echo "$(BLUE)Creating superuser...$(NC)"
	. venv/bin/activate && python manage.py createsuperuser

changepassword: ## Change user password (usage: make changepassword USER=username)
	@echo "$(BLUE)Changing password for $(USER)...$(NC)"
	. venv/bin/activate && python manage.py changepassword $(USER)

##@ Static Files

collectstatic: ## Collect static files
	@echo "$(BLUE)Collecting static files...$(NC)"
	. venv/bin/activate && python manage.py collectstatic --noinput
	@echo "$(GREEN)✓ Static files collected$(NC)"

##@ Cleanup

clean: ## Clean up Python cache files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-migrations: ## Remove all migration files (WARNING: use with caution)
	@echo "$(RED)WARNING: This will remove all migration files!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		find . -path "*/migrations/*.py" -not -name "__init__.py" -delete; \
		find . -path "*/migrations/*.pyc" -delete; \
		echo "$(GREEN)✓ Migration files removed$(NC)"; \
	else \
		echo "$(YELLOW)Cleanup cancelled$(NC)"; \
	fi

##@ Production

prod-build: ## Build production Docker images
	@echo "$(BLUE)Building production images...$(NC)"
	docker-compose -f docker-compose.superset.yml build --no-cache
	@echo "$(GREEN)✓ Production images built$(NC)"

prod-up: ## Start production containers
	@echo "$(BLUE)Starting production containers...$(NC)"
	docker-compose -f docker-compose.superset.yml up -d
	@echo "$(GREEN)✓ Production containers started$(NC)"

prod-logs: ## Show production logs
	docker-compose -f docker-compose.superset.yml logs -f

##@ Backup & Restore

backup-all: ## Backup both Django and Superset
	@echo "$(BLUE)Creating complete backup...$(NC)"
	@$(MAKE) superset-backup
	@echo "$(GREEN)✓ Complete backup finished$(NC)"

backup-db: ## Backup Django database with timestamp
	@echo "$(BLUE)Backing up Django database...$(NC)"
	@mkdir -p backups/django
	@docker exec -e PGPASSWORD=postgres onestep_db \
		pg_dump -U postgres -d onestep_dev > backups/django/django_db_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Django database backed up$(NC)"
	@ls -lh backups/django/django_db_*.sql | tail -1

backup-db-named: ## Backup Django database with custom name (usage: make backup-db-named NAME=my_backup)
	@if [ -z "$(NAME)" ]; then \
		echo "$(RED)Error: NAME parameter required$(NC)"; \
		echo "$(YELLOW)Usage: make backup-db-named NAME=my_backup$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Backing up Django database: $(NAME)...$(NC)"
	@mkdir -p backups/django
	@docker exec -e PGPASSWORD=postgres onestep_db \
		pg_dump -U postgres -d onestep_dev > backups/django/$(NAME).sql
	@echo "$(GREEN)✓ Django database backed up: $(NAME)$(NC)"
	@ls -lh backups/django/$(NAME).sql

list-db-backups: ## List all Django database backups
	@echo "$(BLUE)Available Django database backups:$(NC)"
	@echo ""
	@if [ -d "backups/django" ] && [ -n "$$(ls -A backups/django/*.sql 2>/dev/null)" ]; then \
		ls -lht backups/django/*.sql | awk '{printf "  %-50s %5s %s %s %s\n", $$9, $$5, $$6, $$7, $$8}'; \
		echo ""; \
		echo "$(YELLOW)Total size: $$(du -sh backups/django 2>/dev/null | cut -f1)$(NC)"; \
		echo ""; \
		echo "$(BLUE)To restore: make restore-db FILE=<backup_file>$(NC)"; \
	else \
		echo "$(YELLOW)  No backups found$(NC)"; \
		echo ""; \
		echo "$(BLUE)Create a backup: make backup-db$(NC)"; \
	fi

cleanup-db-backups: ## Remove old Django database backups (keeps last 7)
	@echo "$(BLUE)Cleaning up old Django database backups...$(NC)"
	@if [ -d "backups/django" ]; then \
		cd backups/django && ls -t django_db_*.sql 2>/dev/null | tail -n +8 | xargs -r rm -f; \
		remaining=$$(ls -1 django_db_*.sql 2>/dev/null | wc -l); \
		echo "$(GREEN)✓ Cleanup complete. $$remaining backup(s) remaining$(NC)"; \
	else \
		echo "$(YELLOW)No backups directory found$(NC)"; \
	fi

restore-db: ## Restore Django database (usage: make restore-db FILE=backup.sql)
	@echo "$(BLUE)Restoring Django database from $(FILE)...$(NC)"
	@echo "$(RED)WARNING: This will replace the current database!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker exec -i -e PGPASSWORD=postgres onestep_db \
			psql -U postgres < $(FILE); \
		echo "$(GREEN)✓ Database restored$(NC)"; \
	else \
		echo "$(YELLOW)Restore cancelled$(NC)"; \
	fi

##@ Utilities

version: ## Show Django version
	@. venv/bin/activate && python -c "import django; print(f'Django version: {django.get_version()}')"

requirements: ## Update requirements.txt
	@echo "$(BLUE)Updating requirements.txt...$(NC)"
	. venv/bin/activate && pip freeze > requirements.txt
	@echo "$(GREEN)✓ Requirements updated$(NC)"

urls: ## Show all URL patterns
	@echo "$(BLUE)URL patterns:$(NC)"
	. venv/bin/activate && python manage.py show_urls 2>/dev/null || \
		python manage.py shell -c "from django.urls import get_resolver; print('\n'.join([str(p.pattern) for p in get_resolver().url_patterns]))"

info: ## Show system information
	@echo "$(BLUE)System Information:$(NC)"
	@echo "Python version: $$(python3 --version)"
	@echo "Docker version: $$(docker --version)"
	@echo "Docker Compose version: $$(docker-compose --version)"
	@echo ""
	@echo "$(BLUE)Container Status:$(NC)"
	@docker-compose -f docker-compose.superset.yml ps 2>/dev/null || echo "Containers not running"
	@echo ""
	@echo "$(BLUE)Disk Usage:$(NC)"
	@du -sh backups/ 2>/dev/null || echo "No backups directory"

##@ Quick Start

setup: install migrate collectstatic ## Complete initial setup
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "$(YELLOW)Run 'make dev' to start the development server$(NC)"

docker-setup: docker-build docker-up ## Setup and start Docker environment
	@echo "$(GREEN)✓ Docker environment ready!$(NC)"
	@echo "$(YELLOW)Django Admin: http://localhost:8000/admin/$(NC)"
	@echo "$(YELLOW)Superset: http://localhost:8088$(NC)"
	@echo ""
	@echo "$(BLUE)Initialize Superset with: make superset-init$(NC)"

reset: docker-down docker-clean docker-setup ## Complete reset (WARNING: deletes all data)
	@echo "$(GREEN)✓ Environment reset complete$(NC)"
