# Getting Started with OneStep

Quick guide to get the OneStep application up and running.

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose (optional but recommended)
- **PostgreSQL** 15+ (if not using Docker)

## Quick Start (Full Stack with Docker)

### 1. Start Everything

```bash
# From project root
docker-compose up
```

This will start:
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL database

### 2. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

### 3. Create Superuser (First Time Only)

```bash
# In another terminal
docker-compose exec backend python manage.py createsuperuser
```

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:5173

## Project Structure

```
onestep/
├── backend/           # Django REST API
│   ├── apps/         # Django applications
│   ├── onestep/      # Project settings
│   └── manage.py     # Django management
│
├── frontend/          # Vue 3 + TypeScript SPA
│   ├── src/          # Source code
│   │   ├── core/     # Core functionality
│   │   ├── modules/  # Feature modules
│   │   └── router/   # Routing
│   └── package.json  # Dependencies
│
└── documentation/     # Project documentation
    ├── specs/        # Technical specifications
    ├── api/          # API documentation
    └── guides/       # User guides
```

## Development Workflow

### Backend Development

```bash
cd backend

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test

# Create new app
python manage.py startapp app_name apps/app_name

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

### Backend (.env.dev)

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/onestep
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env.development)

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_TITLE=OneStep - Development
VITE_APP_VERSION=1.0.0
VITE_ENABLE_DEVTOOLS=true
```

## Common Issues

### Port Already in Use

**Backend (8000)**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

**Frontend (5173)**:
```bash
# Find process using port 5173
lsof -i :5173
# Kill the process
kill -9 <PID>
```

### Database Connection Error

Make sure PostgreSQL is running:
```bash
# Check status
docker-compose ps

# Restart database
docker-compose restart db
```

### Frontend Build Errors

```bash
cd frontend

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Backend Migration Issues

```bash
cd backend

# Reset migrations (development only!)
python manage.py migrate --fake app_name zero
python manage.py migrate app_name

# Or reset database (development only!)
docker-compose down -v
docker-compose up
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.initiatives

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests

```bash
cd frontend

# Unit tests
npm run test:unit

# E2E tests
npm run test:e2e
```

## API Documentation

Once the backend is running, access:

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Default Credentials

After creating a superuser, use those credentials to log in.

For development, you can create a test user:

```bash
cd backend
python manage.py shell

from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
```

## Next Steps

1. **Explore the Admin Panel**: http://localhost:8000/admin
2. **Check API Documentation**: http://localhost:8000/api/schema/swagger-ui/
3. **Read the Specs**: See `documentation/specs/`
4. **Start Development**: Begin with Phase 2 - Initiatives Module

## Useful Commands

### Docker

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose up --build

# Remove volumes (reset database)
docker-compose down -v
```

### Git

```bash
# Create feature branch
git checkout -b feature/your-feature

# Commit changes
git add .
git commit -m "feat: your feature description"

# Push to remote
git push origin feature/your-feature
```

## Documentation

- **Main README**: [README.md](README.md)
- **Backend Guide**: [backend/README.md](backend/README.md)
- **Frontend Guide**: [frontend/README.md](frontend/README.md)
- **Documentation Index**: [documentation/README.md](documentation/README.md)
- **Phase 1 Complete**: [frontend/PHASE1_COMPLETE.md](frontend/PHASE1_COMPLETE.md)

## Support

For issues or questions:
1. Check the documentation in `/documentation`
2. Review the specs in `/documentation/specs`
3. Check existing issues
4. Create a new issue with details

## License

This project is part of the OneStep platform.

---

**Happy Coding!** 🚀
