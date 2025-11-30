#!/bin/bash

################################################################################
# Superset Restore Script
#
# This script restores Superset data from a backup created by backup_superset.sh
#
# Usage:
#   ./scripts/restore_superset.sh <backup_name>
#
# Example:
#   ./scripts/restore_superset.sh backup_20241110_143022
#   ./scripts/restore_superset.sh daily_backup
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

usage() {
    echo "Usage: $0 <backup_name>"
    echo ""
    echo "Available backups:"
    if [ -d "${BACKUP_DIR}" ]; then
        ls -1 "${BACKUP_DIR}"/*.tar.gz 2>/dev/null | xargs -n1 basename | sed 's/.tar.gz$//' || echo "  No backups found"
    else
        echo "  No backup directory found"
    fi
    exit 1
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

check_backup_exists() {
    local backup_name=$1
    local backup_file="${BACKUP_DIR}/${backup_name}.tar.gz"
    
    if [ ! -f "${backup_file}" ]; then
        print_error "Backup file not found: ${backup_file}"
        echo ""
        usage
    fi
}

confirm_restore() {
    local backup_name=$1
    
    print_warning "WARNING: This will replace all current Superset data!"
    print_warning "Current dashboards, charts, and configurations will be lost."
    echo ""
    read -p "Are you sure you want to restore from '${backup_name}'? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "Restore cancelled."
        exit 0
    fi
}

extract_backup() {
    local backup_name=$1
    local backup_file="${BACKUP_DIR}/${backup_name}.tar.gz"
    local extract_path="${BACKUP_DIR}/${backup_name}"
    
    print_header "Extracting Backup"
    
    print_info "Extracting ${backup_name}.tar.gz..."
    tar xzf "${backup_file}" -C "${BACKUP_DIR}"
    
    if [ $? -eq 0 ]; then
        print_success "Backup extracted to: ${extract_path}"
        echo "${extract_path}"
    else
        print_error "Failed to extract backup"
        exit 1
    fi
}

stop_superset() {
    print_header "Stopping Superset"
    
    print_info "Stopping Superset container..."
    docker stop "${SUPERSET_CONTAINER}" > /dev/null 2>&1 || true
    print_success "Superset stopped"
}

restore_superset_database() {
    local backup_path=$1
    local db_backup_file="${backup_path}/superset_db.sql"
    
    print_header "Restoring Superset Database"
    
    if [ ! -f "${db_backup_file}" ]; then
        print_error "Database backup file not found: ${db_backup_file}"
        exit 1
    fi
    
    print_info "Dropping existing Superset database..."
    docker exec -e PGPASSWORD="${POSTGRES_PASSWORD}" "${DB_CONTAINER}" \
        psql -U "${POSTGRES_USER}" -c "DROP DATABASE IF EXISTS ${SUPERSET_DB};" || true
    
    print_info "Restoring database from backup..."
    docker exec -i -e PGPASSWORD="${POSTGRES_PASSWORD}" "${DB_CONTAINER}" \
        psql -U "${POSTGRES_USER}" < "${db_backup_file}"
    
    if [ $? -eq 0 ]; then
        print_success "Database restored successfully"
    else
        print_error "Database restore failed"
        exit 1
    fi
}

restore_superset_home() {
    local backup_path=$1
    local home_backup_file="${backup_path}/superset_home.tar.gz"
    
    print_header "Restoring Superset Home Directory"
    
    if [ ! -f "${home_backup_file}" ]; then
        print_warning "Superset home backup not found, skipping..."
        return
    fi
    
    print_info "Copying backup to container..."
    docker cp "${home_backup_file}" "${SUPERSET_CONTAINER}:/tmp/superset_home.tar.gz"
    
    print_info "Removing old Superset home directory..."
    docker exec "${SUPERSET_CONTAINER}" rm -rf /app/superset_home
    
    print_info "Extracting Superset home directory..."
    docker exec "${SUPERSET_CONTAINER}" \
        tar xzf /tmp/superset_home.tar.gz -C /app
    
    docker exec "${SUPERSET_CONTAINER}" rm /tmp/superset_home.tar.gz
    
    if [ $? -eq 0 ]; then
        print_success "Superset home restored successfully"
    else
        print_error "Superset home restore failed"
        exit 1
    fi
}

start_superset() {
    print_header "Starting Superset"
    
    print_info "Starting Superset container..."
    docker start "${SUPERSET_CONTAINER}"
    
    print_info "Waiting for Superset to be ready..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec "${SUPERSET_CONTAINER}" curl -f http://localhost:8088/health > /dev/null 2>&1; then
            print_success "Superset is ready"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    echo ""
    print_warning "Superset may not be fully ready yet. Check logs with: docker logs ${SUPERSET_CONTAINER}"
}

upgrade_superset_db() {
    print_header "Upgrading Superset Database Schema"
    
    print_info "Running database migrations..."
    docker exec "${SUPERSET_CONTAINER}" superset db upgrade
    
    if [ $? -eq 0 ]; then
        print_success "Database schema upgraded"
    else
        print_warning "Database upgrade may have failed. Check logs."
    fi
}

cleanup_extracted_backup() {
    local backup_path=$1
    
    print_header "Cleaning Up"
    
    print_info "Removing extracted backup files..."
    rm -rf "${backup_path}"
    print_success "Cleanup complete"
}

print_summary() {
    local backup_name=$1
    
    print_header "Restore Summary"
    
    echo ""
    print_success "Superset restore completed successfully!"
    echo ""
    print_info "Restored from: ${backup_name}"
    echo ""
    print_info "Access Superset at: http://localhost:8088"
    echo ""
    print_warning "Note: You may need to clear your browser cache if you experience issues."
    echo ""
}

################################################################################
# Main Script
################################################################################

main() {
    # Check arguments
    if [ $# -eq 0 ]; then
        usage
    fi
    
    local backup_name=$1
    
    print_header "Superset Restore Script"
    echo ""
    
    # Pre-flight checks
    print_info "Running pre-flight checks..."
    check_docker_running
    check_container_running "${DB_CONTAINER}"
    check_container_running "${SUPERSET_CONTAINER}"
    check_backup_exists "${backup_name}"
    print_success "All checks passed"
    echo ""
    
    # Confirm restore
    confirm_restore "${backup_name}"
    echo ""
    
    # Extract backup
    local backup_path=$(extract_backup "${backup_name}")
    echo ""
    
    # Stop Superset
    stop_superset
    echo ""
    
    # Restore database
    restore_superset_database "${backup_path}"
    echo ""
    
    # Restore home directory
    restore_superset_home "${backup_path}"
    echo ""
    
    # Start Superset
    start_superset
    echo ""
    
    # Upgrade database schema
    upgrade_superset_db
    echo ""
    
    # Cleanup
    cleanup_extracted_backup "${backup_path}"
    echo ""
    
    # Print summary
    print_summary "${backup_name}"
}

# Run main function
main "$@"
