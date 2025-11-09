# Technology Stack

## Core Technologies
- **Python 3.x** - Primary programming language
- **Django** - Web framework with built-in admin interface
- **Django REST Framework (DRF)** - API development toolkit
- **Django Admin** - Built-in administrative interface

## Build System
- **pip** - Package management
- **virtualenv/venv** - Virtual environment management
- **requirements.txt** - Dependency specification

## Frameworks & Libraries
- **Django** - Web framework with admin interface
- **Django REST Framework** - API serialization, views, and browsable API
- **Django ORM** - Database abstraction layer
- **django-filter** - API filtering capabilities
- **djangorestframework-simplejwt** - JWT authentication
- **django-cors-headers** - CORS handling for API
- **Gunicorn** - WSGI HTTP Server (production)

## Development Tools
- VSCode with Kiro AI assistant integration
- MCP (Model Context Protocol) configuration disabled
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking

## Common Commands

### Development
```bash
python manage.py runserver          # Start development server (admin + API)
python manage.py makemigrations     # Create database migrations
python manage.py migrate            # Apply database migrations
python manage.py createsuperuser    # Create admin user
python manage.py shell              # Django shell
python manage.py collectstatic      # Collect static files
```

### Testing
```bash
python manage.py test               # Run Django tests
pytest                              # Run pytest tests
coverage run --source='.' manage.py test  # Run with coverage
```

### Building
```bash
pip install -r requirements.txt     # Install dependencies
python manage.py check              # Check for issues
black .                             # Format code
flake8 .                            # Lint code
```

### Deployment
```bash
gunicorn myproject.wsgi:application  # Production server
python manage.py collectstatic --noinput  # Static files for production
```