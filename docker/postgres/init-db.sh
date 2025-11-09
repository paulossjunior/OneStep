#!/bin/bash
# PostgreSQL initialization script
# This script runs when the PostgreSQL container is first created
# It can be used to create additional databases, users, or configure permissions

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Initializing PostgreSQL database...${NC}"

# The main database is created automatically by the postgres image
# using POSTGRES_DB, POSTGRES_USER, and POSTGRES_PASSWORD environment variables

# Additional database setup can be added here if needed
# For example, creating additional databases or users:

# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
#     CREATE DATABASE additional_db;
#     GRANT ALL PRIVILEGES ON DATABASE additional_db TO $POSTGRES_USER;
# EOSQL

echo -e "${GREEN}PostgreSQL initialization complete!${NC}"
