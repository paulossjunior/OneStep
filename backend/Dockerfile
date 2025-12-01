# Multi-stage build for Django application

# ============================================
# Development Stage
# ============================================
FROM python:3.11-slim as development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint-dev.sh

# Create directories with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chmod 755 /app/staticfiles /app/media /app/logs

EXPOSE 8000

# Development command (can be overridden)
CMD ["bash", "/app/docker-entrypoint-dev.sh"]

# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.11-slim as builder

# Set environment variables for build optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create and set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --user --no-warn-script-location --compile -r requirements.txt \
    && find /root/.local -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -type f -name '*.pyc' -delete 2>/dev/null || true

# Stage 2: Production - Create minimal runtime image
FROM python:3.11-slim as production

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    DJANGO_SETTINGS_MODULE=onestep.settings \
    PYTHONHASHSEED=random

# Install runtime dependencies only (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security with specific UID/GID
RUN groupadd -g 1000 appuser && \
    useradd -m -u 1000 -g appuser -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy entrypoint script
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh

# Copy application code (excluding unnecessary files via .dockerignore)
COPY --chown=appuser:appuser . .

# Create directories for static files, media files, and logs with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app/staticfiles /app/media /app/logs && \
    chmod 755 /app/staticfiles /app/media && \
    chmod 775 /app/logs

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Remove unnecessary files to reduce image size
RUN find /app -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true && \
    find /app -type f -name '*.pyc' -delete 2>/dev/null || true && \
    find /app -type f -name '*.pyo' -delete 2>/dev/null || true && \
    find /app -type d -name '.git' -exec rm -rf {} + 2>/dev/null || true && \
    find /app -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true && \
    find /app -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true

# Switch to non-root user for security
USER appuser

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Expose port 8000
EXPOSE 8000

# Health check with improved reliability
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/admin/', timeout=5)" || exit 1

# Default command for production - Gunicorn with optimized settings
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "sync", "--timeout", "60", "--graceful-timeout", "30", "--max-requests", "1000", "--max-requests-jitter", "50", "onestep.wsgi:application"]
