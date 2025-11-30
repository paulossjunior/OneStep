FROM apache/superset:latest

# Switch to root to install system dependencies
USER root

# Install PostgreSQL client and development libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip in the virtual environment and then install psycopg2-binary
RUN python -m ensurepip --upgrade || true && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
    python -m pip install --no-cache-dir psycopg2-binary && \
    python -c "import psycopg2; print(f'psycopg2 version: {psycopg2.__version__}')"

# Ensure proper permissions for superset home directory
RUN mkdir -p /app/superset_home/.cache && \
    chown -R superset:superset /app/superset_home

# Switch back to superset user
USER superset