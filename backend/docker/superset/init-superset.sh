#!/bin/bash
set -e

echo "Starting Superset initialization..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "postgres" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - checking for superset database..."

# Create superset database if it doesn't exist
PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "postgres" -tc "SELECT 1 FROM pg_database WHERE datname = 'superset'" | grep -q 1 || \
PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "postgres" -c "CREATE DATABASE superset"

echo "Superset database ready"

# Initialize Superset database
echo "Initializing Superset database..."
superset db upgrade

# Create admin user if it doesn't exist
echo "Creating admin user..."
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
    --firstname "${SUPERSET_ADMIN_FIRSTNAME:-Admin}" \
    --lastname "${SUPERSET_ADMIN_LASTNAME:-User}" \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@superset.com}" \
    --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || echo "Admin user already exists"

# Initialize Superset
echo "Initializing Superset..."
superset init

echo "Superset initialization complete!"
