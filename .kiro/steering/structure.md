# Project Structure

This workspace follows a minimal structure that can be expanded as the project grows.

## Current Structure
```
.
├── .kiro/
│   └── steering/          # AI assistant steering rules
├── .vscode/
│   └── settings.json      # VSCode configuration
```

## Django Project Organization

### Django Structure
```
project_name/
├── manage.py              # Django management script
├── project_name/          # Main project package
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI configuration
├── apps/                  # Django applications (domain-driven)
│   ├── users/            # User domain
│   ├── orders/           # Order domain
│   ├── products/         # Product domain
│   ├── payments/         # Payment domain
│   └── core/             # Shared utilities and base classes
├── static/               # Static files
├── media/                # User uploads
├── templates/            # HTML templates (if needed)
└── requirements.txt      # Python dependencies
```

### Domain-Driven App Structure
Each domain should be organized as a separate Django application focusing on admin and API:
```
app_name/
├── __init__.py
├── models.py             # Database models
├── admin.py              # Django admin interface
├── serializers.py        # DRF serializers for API
├── views.py              # API views (ViewSets/APIViews)
├── urls.py               # API URL patterns
├── apps.py               # App configuration
├── permissions.py        # API permissions
├── filters.py            # API filtering
├── tests/                # Tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_admin.py
│   ├── test_api.py
│   └── test_serializers.py
└── migrations/           # Database migrations
```

### Configuration
- `.kiro/` - Kiro AI assistant configuration and steering
- `.vscode/` - VSCode editor settings
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed)
- `settings/` - Split settings for different environments

### Documentation
- `README.md` - Project overview and setup instructions
- `docs/` - API documentation and guides
- `CHANGELOG.md` - Version history

## Domain Organization Principles
- **One domain per Django app** - Each business domain gets its own application
- **Domain boundaries** - Keep domain logic isolated within each app
- **Shared utilities** - Common functionality goes in the `core` app
- **Cross-domain communication** - Use well-defined interfaces between domains
- **Domain models** - Each app owns its data models and business logic

## Naming Conventions
- Use snake_case for Python files, functions, and variables
- Use PascalCase for Django model classes
- Use lowercase with underscores for app names (matching domain names)
- Keep URL patterns lowercase with hyphens
- Use descriptive names for API endpoints that reflect domain concepts