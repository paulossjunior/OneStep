#!/bin/bash
set -e

echo "Bootstrap: Checking psycopg2 installation..."

# Verify psycopg2 is available (should be installed in Dockerfile)
if python -c "import psycopg2" 2>/dev/null; then
    echo "Bootstrap: psycopg2 is installed and working"
else
    echo "Bootstrap: WARNING - psycopg2 not found"
fi

echo "Bootstrap: Complete"
