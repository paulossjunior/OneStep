#!/bin/bash
# Entrypoint script for Django application
# Waits for database readiness, runs migrations, and collects static files

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting OneStep Django Application...${NC}"

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
    
    # Maximum number of retries
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    # Wait for PostgreSQL to accept connections
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo -e "${RED}Error: PostgreSQL did not become ready in time${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}PostgreSQL is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)${NC}"
        sleep 2
    done
    
    echo -e "${GREEN}PostgreSQL is ready!${NC}"
}

# Function to run database migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    # Check for pending migrations
    if python manage.py showmigrations --plan | grep -q '\[ \]'; then
        python manage.py migrate --noinput
        echo -e "${GREEN}Database migrations completed successfully!${NC}"
    else
        echo -e "${GREEN}No pending migrations found.${NC}"
    fi
}

# Function to collect static files
collect_static() {
    echo -e "${YELLOW}Collecting static files...${NC}"
    
    # Set STATIC_ROOT from environment variable or use default
    STATIC_ROOT=${STATIC_ROOT:-/app/staticfiles}
    export STATIC_ROOT
    echo -e "${YELLOW}Static files will be collected to: ${STATIC_ROOT}${NC}"
    
    # Verify STATIC_ROOT directory exists and is writable
    if [ ! -d "$STATIC_ROOT" ]; then
        echo -e "${YELLOW}Creating static files directory: ${STATIC_ROOT}${NC}"
        if ! mkdir -p "$STATIC_ROOT" 2>/dev/null; then
            echo -e "${RED}Error: Cannot create static files directory at ${STATIC_ROOT}${NC}"
            echo -e "${RED}Check directory permissions and path validity${NC}"
            exit 1
        fi
    fi
    
    if [ ! -w "$STATIC_ROOT" ]; then
        echo -e "${RED}Error: Static files directory is not writable: ${STATIC_ROOT}${NC}"
        echo -e "${RED}Current user: $(whoami), Directory permissions: $(ls -ld "$STATIC_ROOT")${NC}"
        exit 1
    fi
    
    # Capture collectstatic output for better error reporting
    COLLECTSTATIC_OUTPUT=$(mktemp)
    
    # Collect static files without user input
    echo -e "${YELLOW}Running collectstatic command...${NC}"
    if python manage.py collectstatic --noinput --clear > "$COLLECTSTATIC_OUTPUT" 2>&1; then
        # Display collectstatic output
        cat "$COLLECTSTATIC_OUTPUT"
        rm -f "$COLLECTSTATIC_OUTPUT"
        
        echo -e "${GREEN}Static files collected successfully!${NC}"
        
        # Verify static files directory exists (should always pass at this point)
        if [ ! -d "$STATIC_ROOT" ]; then
            echo -e "${RED}Error: Static files directory does not exist at ${STATIC_ROOT}${NC}"
            exit 1
        fi
        
        # Verify static files were actually collected
        FILE_COUNT=$(find "$STATIC_ROOT" -type f 2>/dev/null | wc -l)
        DIR_COUNT=$(find "$STATIC_ROOT" -mindepth 1 -type d 2>/dev/null | wc -l)
        
        if [ "$FILE_COUNT" -eq 0 ]; then
            echo -e "${RED}Error: No static files found in ${STATIC_ROOT}${NC}"
            echo -e "${RED}Static file collection may have failed silently${NC}"
            echo -e "${RED}Directory contents:${NC}"
            ls -la "$STATIC_ROOT" 2>/dev/null || echo "Cannot list directory"
            exit 1
        fi
        
        # Log success with detailed statistics
        echo -e "${GREEN}Static files verification:${NC}"
        echo -e "${GREEN}  - Total files: ${FILE_COUNT}${NC}"
        echo -e "${GREEN}  - Total directories: ${DIR_COUNT}${NC}"
        echo -e "${GREEN}  - Location: ${STATIC_ROOT}${NC}"
        
        # Calculate total size of static files
        TOTAL_SIZE=$(du -sh "$STATIC_ROOT" 2>/dev/null | cut -f1)
        echo -e "${GREEN}  - Total size: ${TOTAL_SIZE}${NC}"
        
        # Check for critical static file directories
        CRITICAL_DIRS=("admin" "rest_framework" "drf_spectacular")
        MISSING_DIRS=()
        FOUND_DIRS=()
        
        for dir in "${CRITICAL_DIRS[@]}"; do
            if [ ! -d "$STATIC_ROOT/$dir" ]; then
                MISSING_DIRS+=("$dir")
            else
                # Count files in each critical directory
                DIR_FILE_COUNT=$(find "$STATIC_ROOT/$dir" -type f 2>/dev/null | wc -l)
                FOUND_DIRS+=("$dir ($DIR_FILE_COUNT files)")
            fi
        done
        
        if [ ${#FOUND_DIRS[@]} -gt 0 ]; then
            echo -e "${GREEN}Critical static file directories found:${NC}"
            for dir in "${FOUND_DIRS[@]}"; do
                echo -e "${GREEN}  ✓ ${dir}${NC}"
            done
        fi
        
        if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
            echo -e "${YELLOW}Warning: Some expected static file directories are missing:${NC}"
            for dir in "${MISSING_DIRS[@]}"; do
                echo -e "${YELLOW}  ✗ ${dir}${NC}"
            done
            echo -e "${YELLOW}This may indicate incomplete static file collection or missing apps${NC}"
            echo -e "${YELLOW}Verify that all required apps are in INSTALLED_APPS${NC}"
        else
            echo -e "${GREEN}All critical static file directories verified successfully!${NC}"
        fi
        
    else
        # Display error output
        echo -e "${RED}Error: Failed to collect static files${NC}"
        echo -e "${RED}collectstatic command output:${NC}"
        cat "$COLLECTSTATIC_OUTPUT"
        rm -f "$COLLECTSTATIC_OUTPUT"
        
        echo -e "${RED}Troubleshooting steps:${NC}"
        echo -e "${RED}  1. Check Django settings (STATIC_ROOT, STATIC_URL, INSTALLED_APPS)${NC}"
        echo -e "${RED}  2. Ensure all required packages are installed (requirements.txt)${NC}"
        echo -e "${RED}  3. Verify directory permissions for ${STATIC_ROOT}${NC}"
        echo -e "${RED}  4. Check for missing dependencies in INSTALLED_APPS${NC}"
        exit 1
    fi
}

# Function to create superuser if needed (optional, for development)
create_superuser_if_needed() {
    if [ "$CREATE_SUPERUSER" = "1" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
        echo -e "${YELLOW}Checking for superuser...${NC}"
        
        python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='${DJANGO_SUPERUSER_EMAIL:-admin@example.com}',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
END
        
        echo -e "${GREEN}Superuser check completed!${NC}"
    fi
}

# Main execution flow
main() {
    # Wait for database to be ready
    wait_for_postgres
    
    # Run database migrations
    run_migrations
    
    # Collect static files
    collect_static
    
    # Create superuser if environment variables are set
    create_superuser_if_needed
    
    echo -e "${GREEN}Initialization complete! Starting application...${NC}"
    
    # Execute the main command (passed as arguments to this script)
    exec "$@"
}

# Run main function with all script arguments
main "$@"
