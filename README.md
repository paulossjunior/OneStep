# OneStep - Initiative Management System

OneStep is a Django REST API for managing organizational initiatives including programs, projects, and events.

## Project Structure

```
onestep/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── onestep/              # Main project package
│   ├── settings.py       # Django settings
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI configuration
├── apps/                 # Django applications (domain-driven)
│   ├── core/            # Shared utilities and base classes
│   ├── people/          # Person domain
│   └── initiatives/     # Initiative domain
└── venv/                # Virtual environment
```

## Setup Instructions

### Docker Setup (Recommended)

The easiest way to get started is using Docker Compose, which provides a consistent development environment with PostgreSQL.

1. **Prerequisites:**
   - Docker and Docker Compose installed on your system
   - No other services running on port 8000 (Django) or 5432 (PostgreSQL)

2. **Quick Start:**
   ```bash
   # Start all services (Django + PostgreSQL)
   make up
   
   # The application will be available at http://localhost:8000
   # Database migrations run automatically on startup
   ```

3. **Create a superuser:**
   ```bash
   make createsuperuser
   ```

4. **View logs:**
   ```bash
   make logs
   ```

5. **Stop services:**
   ```bash
   make down
   ```

### Manual Setup (Without Docker)

If you prefer to run the application without Docker:

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Django checks:**
   ```bash
   python manage.py check
   ```

4. **Create database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Docker Commands Reference

All Docker operations can be performed using the Makefile commands:

| Command | Description |
|---------|-------------|
| `make up` | Start all services (Django + PostgreSQL) |
| `make down` | Stop all services gracefully |
| `make build` | Build or rebuild Docker containers |
| `make logs` | View logs from all services |
| `make shell` | Open a shell inside the Django container |
| `make migrate` | Run database migrations |
| `make createsuperuser` | Create a Django admin superuser |
| `make test` | Run the test suite in the container |
| `make clean` | Stop services and remove volumes (⚠️ deletes data) |

### Advanced Docker Commands

For more control, you can use Docker Compose directly:

```bash
# Start services in detached mode
docker-compose up -d

# View logs for specific service
docker-compose logs -f web
docker-compose logs -f db

# Execute Django management commands
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Access Django shell
docker-compose exec web python manage.py shell

# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d onestep_dev

# Rebuild containers after dependency changes
docker-compose up --build

# Stop and remove containers, networks, volumes
docker-compose down -v
```

## API Documentation

OneStep provides interactive API documentation using Swagger UI and ReDoc, making it easy to explore and test API endpoints.

### Documentation Endpoints

- **Swagger UI:** http://localhost:8000/api/docs/ - Interactive API testing interface
- **ReDoc:** http://localhost:8000/api/redoc/ - Clean, responsive documentation
- **OpenAPI Schema:** http://localhost:8000/api/schema/ - Raw OpenAPI 3.0 specification (JSON)

### Using the Interactive Documentation

#### Accessing Swagger UI

1. Start the development server (see Setup Instructions above)
2. Navigate to http://localhost:8000/api/docs/
3. Browse available endpoints organized by domain (initiatives, people, core)
4. Click on any endpoint to see detailed information including:
   - Request parameters and body schema
   - Response schema and examples
   - Authentication requirements

#### Testing Endpoints with "Try it out"

The Swagger UI allows you to test API endpoints directly from your browser:

1. **For Public Endpoints:**
   - Click on an endpoint to expand it
   - Click the "Try it out" button
   - Fill in any required parameters
   - Click "Execute" to send the request
   - View the response below

2. **For Protected Endpoints (Requires Authentication):**
   
   Most endpoints require JWT authentication. Follow these steps:
   
   **Step 1: Obtain a JWT Token**
   - Use the `/api/token/` endpoint to get an access token
   - You'll need valid credentials (username and password)
   - Example using curl:
     ```bash
     curl -X POST http://localhost:8000/api/token/ \
       -H "Content-Type: application/json" \
       -d '{"username": "your_username", "password": "your_password"}'
     ```
   - The response will contain an `access` token and a `refresh` token
   
   **Step 2: Authorize in Swagger UI**
   - Click the "Authorize" button at the top of the Swagger UI page
   - In the "Value" field, enter: `Bearer YOUR_ACCESS_TOKEN`
     - Replace `YOUR_ACCESS_TOKEN` with the actual token from Step 1
     - Make sure to include the word "Bearer" followed by a space
   - Click "Authorize" then "Close"
   
   **Step 3: Test Protected Endpoints**
   - Now you can use "Try it out" on any protected endpoint
   - The authorization header will be automatically included in requests
   - Your session will remain authorized until you click "Logout" or refresh the page

   **Token Refresh:**
   - Access tokens expire after a set time period
   - Use the `/api/token/refresh/` endpoint with your refresh token to get a new access token
   - Example:
     ```bash
     curl -X POST http://localhost:8000/api/token/refresh/ \
       -H "Content-Type: application/json" \
       -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
     ```

#### Alternative: ReDoc Interface

For a cleaner, read-only documentation experience:
- Navigate to http://localhost:8000/api/redoc/
- Browse the same API documentation in a responsive, three-panel layout
- ReDoc is ideal for reading documentation but doesn't support "Try it out" functionality

### API Endpoints

- **Admin Interface:** http://localhost:8000/admin/
- **API Root:** http://localhost:8000/api/
- **People API:** http://localhost:8000/api/people/
- **Initiatives API:** http://localhost:8000/api/initiatives/
- **JWT Token:** http://localhost:8000/api/token/
- **JWT Refresh:** http://localhost:8000/api/token/refresh/

## Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Comprehensive development workflow guide
  - Hot-reload development
  - Database management
  - Testing workflow
  - Debugging tips
  - Backup and restore procedures
- **[PRODUCTION.md](PRODUCTION.md)** - Production deployment checklist
- **[docker/production-checklist.md](docker/production-checklist.md)** - Detailed production setup guide

## Core Features

- **Initiative Management:** Create and manage programs, projects, and events
- **Team Management:** Assign coordinators and team members to initiatives
- **Hierarchical Structure:** Support for parent-child initiative relationships
- **REST API:** Full CRUD operations via REST endpoints
- **Django Admin:** Administrative interface for data management

## Technology Stack

- **Django 4.2.7** - Web framework
- **Django REST Framework 3.14.0** - API development
- **PostgreSQL 15** - Database (Docker setup)
- **SQLite** - Database (manual setup fallback)
- **Python 3.11** - Programming language
- **Docker & Docker Compose** - Containerization
- **Gunicorn** - WSGI server (production)

## Environment Configuration

### Docker Environment Variables

The Docker setup uses environment variables for configuration. Two environment files are provided:

- **`.env.dev`** - Development configuration (used by default)
- **`.env.example`** - Template for creating custom configurations

Key environment variables:

```bash
# Django settings
DEBUG=1                          # Enable debug mode (1=on, 0=off)
SECRET_KEY=your-secret-key       # Django secret key

# Database configuration
POSTGRES_DB=onestep_dev          # Database name
POSTGRES_USER=postgres           # Database user
POSTGRES_PASSWORD=postgres       # Database password
DB_HOST=db                       # Database host (Docker service name)
DB_PORT=5432                     # Database port
```

To customize your environment:
1. Copy `.env.example` to `.env`
2. Update values as needed
3. Restart services with `make down && make up`

## Troubleshooting

### Common Issues and Solutions

#### Port Already in Use

**Problem:** Error message about port 8000 or 5432 already in use.

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :5432

# Stop the conflicting service or change ports in docker-compose.yml
```

#### Database Connection Errors

**Problem:** Django can't connect to PostgreSQL.

**Solution:**
```bash
# Check if database container is running
docker-compose ps

# View database logs
make logs

# Restart services
make down
make up
```

#### Migrations Not Applied

**Problem:** Database tables don't exist or are outdated.

**Solution:**
```bash
# Run migrations manually
make migrate

# Or rebuild containers
make build
make up
```

#### Permission Denied Errors

**Problem:** Permission errors when accessing files or volumes.

**Solution:**
```bash
# Fix volume permissions
docker-compose down
docker volume rm onestep_postgres_data
make up
```

#### Container Won't Start

**Problem:** Container exits immediately or won't start.

**Solution:**
```bash
# Check container logs for errors
docker-compose logs web

# Rebuild containers from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

#### Code Changes Not Reflected

**Problem:** Changes to Python code don't appear in running container.

**Solution:**
- Code changes should auto-reload in development mode
- If not working, restart services: `make down && make up`
- Check that source code is properly mounted in docker-compose.yml

#### Database Data Lost

**Problem:** Database resets after stopping containers.

**Solution:**
- Use `make down` instead of `docker-compose down -v`
- The `-v` flag removes volumes and deletes data
- To intentionally reset: `make clean` then `make up`

#### Out of Disk Space

**Problem:** Docker running out of space.

**Solution:**
```bash
# Clean up unused Docker resources
docker system prune -a

# Remove specific volumes
docker volume ls
docker volume rm <volume_name>
```

### Getting Help

If you encounter issues not covered here:

1. Check container logs: `make logs`
2. Verify environment variables in `.env.dev`
3. Ensure Docker and Docker Compose are up to date
4. Try rebuilding containers: `make build`
5. Check Docker daemon is running: `docker ps`

## Development Status

This project is currently in development. The basic Django project structure has been set up with:

- ✅ Django project configuration
- ✅ Domain-driven app structure (core, people, initiatives)
- ✅ REST Framework configuration
- ✅ URL routing setup
- ✅ Docker containerization with PostgreSQL
- ✅ Development and production Docker configurations
- ✅ Makefile commands for easy management
- ✅ Interactive API documentation (Swagger UI & ReDoc)
- ⏳ Models implementation (in progress)
- ⏳ API endpoints (in progress)
- ⏳ Admin interface (in progress)

## Next Steps

1. Implement Person model with validation
2. Implement Initiative model with relationships
3. Create API serializers and views
4. Configure Django Admin interface
5. Add authentication and permissions
6. Write tests