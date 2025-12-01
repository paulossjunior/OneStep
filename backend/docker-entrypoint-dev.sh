#!/bin/bash
# Development entrypoint for Django

set -e

echo "🚀 Starting OneStep Backend (Development Mode)"
echo "=============================================="

# Wait for database - simple approach
echo "⏳ Waiting for PostgreSQL..."
echo "Sleeping for 10 seconds to ensure database is ready..."
sleep 10
echo "✅ Proceeding with initialization..."

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations complete!"

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files collected!"

# Verify static files
if [ -d "/app/staticfiles/admin" ]; then
    echo "✅ Admin static files found!"
    ls -la /app/staticfiles/ | head -10
else
    echo "⚠️  Warning: Admin static files not found!"
    echo "Attempting to collect again..."
    python manage.py collectstatic --noinput
fi

# Create superuser if needed (optional)
if [ "$CREATE_SUPERUSER" = "1" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME:-admin}').exists():
    User.objects.create_superuser(
        username='${DJANGO_SUPERUSER_USERNAME:-admin}',
        email='${DJANGO_SUPERUSER_EMAIL:-admin@example.com}',
        password='${DJANGO_SUPERUSER_PASSWORD:-admin123}'
    )
    print('✅ Superuser created!')
else:
    print('ℹ️  Superuser already exists')
END
fi

echo "=============================================="
echo "🎉 Initialization complete!"
echo "🌐 Starting Django development server..."
echo "=============================================="

# Start Django development server
exec python manage.py runserver 0.0.0.0:8000
