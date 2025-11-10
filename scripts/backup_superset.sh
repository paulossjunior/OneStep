#!/bin/bash

################################################################################
# Superset Backup Script
#
# This script backs up all Superset data including:
# - Superset metadata database (dashboards, charts, datasets, etc.)
# - Superset configuration files
# - Superset home directory (contains user uploads, thumbnails, etc.)
#
# Usage:
#   ./scripts/backup_superset.sh [backup_name]
#
# Example:
#   ./scripts/backup_superset.sh daily_backup
#   ./scripts/backup_superset.sh  # Uses timestamp as backup name
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups/superset"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="${1:-backup_${TIMESTAMP}}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Docker container names
DB_CONTAINER="onestep_db"
SUPERSET_CONTAINER="superset"

# Database configuration (from .env.superset or defaults)
if [ -f "${PROJECT_ROOT}/.env.superset" ]; then
    source "${PROJECT_ROOT}/.env.superset"
fi

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
SUPERSET_DB="superset"

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_docker_running() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

check_container_running() {
    local container=$1
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        print_error "Container '${container}' is not running."
        print_info "Start containers with: docker-compose -f docker-compose.superset.yml up -d"
        exit 1
    fi
}

create_backup_directory() {
    mkdir -p "${BACKUP_PATH}"
    print_success "Created backup directory: ${BACKUP_PATH}"
}

backup_superset_database() {
    print_header "Backing up Superset Database"
    
    local db_backup_file="${BACKUP_PATH}/superset_db.sql"
    
    print_info "Dumping Superset database..."
    docker exec -e PGPASSWORD="${POSTGRES_PASSWORD}" "${DB_CONTAINER}" \
        pg_dump -U "${POSTGRES_USER}" -d "${SUPERSET_DB}" \
        --clean --if-exists --create \
        > "${db_backup_file}"
    
    if [ $? -eq 0 ]; then
        local size=$(du -h "${db_backup_file}" | cut -f1)
        print_success "Database backup completed (${size})"
    else
        print_error "Database backup failed"
        exit 1
    fi
}

backup_superset_home() {
    print_header "Backing up Superset Home Directory"
    
    local home_backup_file="${BACKUP_PATH}/superset_home.tar.gz"
    
    print_info "Creating archive of Superset home directory..."
    docker exec "${SUPERSET_CONTAINER}" \
        tar czf /tmp/superset_home.tar.gz -C /app superset_home
    
    docker cp "${SUPERSET_CONTAINER}:/tmp/superset_home.tar.gz" "${home_backup_file}"
    
    docker exec "${SUPERSET_CONTAINER}" rm /tmp/superset_home.tar.gz
    
    if [ $? -eq 0 ]; then
        local size=$(du -h "${home_backup_file}" | cut -f1)
        print_success "Superset home backup completed (${size})"
    else
        print_error "Superset home backup failed"
        exit 1
    fi
}

backup_superset_config() {
    print_header "Backing up Superset Configuration"
    
    local config_dir="${BACKUP_PATH}/config"
    mkdir -p "${config_dir}"
    
    # Backup superset_config.py
    if [ -f "${PROJECT_ROOT}/docker/superset/superset_config.py" ]; then
        cp "${PROJECT_ROOT}/docker/superset/superset_config.py" "${config_dir}/"
        print_success "Backed up superset_config.py"
    fi
    
    # Backup init script
    if [ -f "${PROJECT_ROOT}/docker/superset/init-superset.sh" ]; then
        cp "${PROJECT_ROOT}/docker/superset/init-superset.sh" "${config_dir}/"
        print_success "Backed up init-superset.sh"
    fi
    
    # Backup Dockerfile
    if [ -f "${PROJECT_ROOT}/docker/superset/Dockerfile" ]; then
        cp "${PROJECT_ROOT}/docker/superset/Dockerfile" "${config_dir}/"
        print_success "Backed up Dockerfile"
    fi
    
    # Backup environment variables (sanitized)
    if [ -f "${PROJECT_ROOT}/.env.superset" ]; then
        # Remove sensitive data before backing up
        grep -v "PASSWORD\|SECRET\|KEY" "${PROJECT_ROOT}/.env.superset" > "${config_dir}/env.superset.template" || true
        print_success "Backed up environment template (passwords removed)"
    fi
}

export_superset_assets() {
    print_header "Exporting Superset Assets"
    
    local assets_dir="${BACKUP_PATH}/assets"
    mkdir -p "${assets_dir}"
    
    print_info "Exporting dashboards, charts, and datasets..."
    
    # Export all dashboards
    docker exec "${SUPERSET_CONTAINER}" \
        superset export-dashboards -f /tmp/dashboards.zip || true
    
    if docker exec "${SUPERSET_CONTAINER}" test -f /tmp/dashboards.zip; then
        docker cp "${SUPERSET_CONTAINER}:/tmp/dashboards.zip" "${assets_dir}/"
        docker exec "${SUPERSET_CONTAINER}" rm /tmp/dashboards.zip
        print_success "Exported dashboards"
    else
        print_warning "No dashboards to export or export failed"
    fi
    
    # Export databases configuration
    docker exec "${SUPERSET_CONTAINER}" \
        superset export-datasources -f /tmp/datasources.yaml || true
    
    if docker exec "${SUPERSET_CONTAINER}" test -f /tmp/datasources.yaml; then
        docker cp "${SUPERSET_CONTAINER}:/tmp/datasources.yaml" "${assets_dir}/"
        docker exec "${SUPERSET_CONTAINER}" rm /tmp/datasources.yaml
        print_success "Exported datasources"
    else
        print_warning "No datasources to export or export failed"
    fi
}

create_backup_metadata() {
    print_header "Creating Backup Metadata"
    
    local metadata_file="${BACKUP_PATH}/backup_info.txt"
    
    cat > "${metadata_file}" << EOF
Superset Backup Information
===========================

Backup Name: ${BACKUP_NAME}
Backup Date: $(date)
Backup Path: ${BACKUP_PATH}

System Information:
- Hostname: $(hostname)
- User: $(whoami)
- Docker Version: $(docker --version)

Container Information:
- Database Container: ${DB_CONTAINER}
- Superset Container: ${SUPERSET_CONTAINER}

Database Information:
- Database Name: ${SUPERSET_DB}
- Database User: ${POSTGRES_USER}

Backup Contents:
- superset_db.sql: Superset metadata database dump
- superset_home.tar.gz: Superset home directory (uploads, thumbnails, etc.)
- config/: Configuration files
- assets/: Exported dashboards and datasources (if any)

Restore Instructions:
See scripts/restore_superset.sh for restoration procedure.

EOF
    
    print_success "Created backup metadata"
}

compress_backup() {
    print_header "Compressing Backup"
    
    local archive_name="${BACKUP_NAME}.tar.gz"
    local archive_path="${BACKUP_DIR}/${archive_name}"
    
    print_info "Creating compressed archive..."
    tar czf "${archive_path}" -C "${BACKUP_DIR}" "${BACKUP_NAME}"
    
    if [ $? -eq 0 ]; then
        local size=$(du -h "${archive_path}" | cut -f1)
        print_success "Backup compressed: ${archive_path} (${size})"
        
        # Remove uncompressed backup directory
        rm -rf "${BACKUP_PATH}"
        print_info "Removed uncompressed backup directory"
    else
        print_error "Compression failed"
        exit 1
    fi
}

cleanup_old_backups() {
    print_header "Cleaning Up Old Backups"
    
    # Keep only the last 7 backups
    local keep_count=7
    
    print_info "Keeping the last ${keep_count} backups..."
    
    cd "${BACKUP_DIR}"
    ls -t backup_*.tar.gz 2>/dev/null | tail -n +$((keep_count + 1)) | xargs -r rm -f
    
    local remaining=$(ls -1 backup_*.tar.gz 2>/dev/null | wc -l)
    print_success "Cleanup complete. ${remaining} backup(s) remaining."
}

print_summary() {
    print_header "Backup Summary"
    
    echo ""
    print_success "Superset backup completed successfully!"
    echo ""
    print_info "Backup Details:"
    echo "  Name: ${BACKUP_NAME}"
    echo "  Location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    echo "  Size: $(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"
    echo ""
    print_info "To restore this backup, run:"
    echo "  ./scripts/restore_superset.sh ${BACKUP_NAME}"
    echo ""
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "Superset Backup Script"
    echo ""
    
    # Pre-flight checks
    print_info "Running pre-flight checks..."
    check_docker_running
    check_container_running "${DB_CONTAINER}"
    check_container_running "${SUPERSET_CONTAINER}"
    print_success "All checks passed"
    echo ""
    
    # Create backup directory
    create_backup_directory
    echo ""
    
    # Perform backups
    backup_superset_database
    echo ""
    
    backup_superset_home
    echo ""
    
    backup_superset_config
    echo ""
    
    export_superset_assets
    echo ""
    
    # Create metadata
    create_backup_metadata
    echo ""
    
    # Compress backup
    compress_backup
    echo ""
    
    # Cleanup old backups
    cleanup_old_backups
    echo ""
    
    # Print summary
    print_summary
}

# Run main function
main
