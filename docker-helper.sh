#!/bin/bash

# OneStep Docker Helper Script
# Facilita o gerenciamento dos containers Docker

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Commands
case "$1" in
    start)
        MODE=${2:-dev}
        if [ "$MODE" == "prod" ]; then
            print_header "Starting OneStep Services (PRODUCTION)"
            docker-compose -f docker-compose.prod.yml up -d
            print_success "Production services started!"
            print_info "Frontend: http://localhost"
            print_info "Backend: http://localhost:8000"
            print_info "Admin: http://localhost:8000/admin"
        else
            print_header "Starting OneStep Services (DEVELOPMENT)"
            docker-compose -f docker-compose.dev.yml up -d
            print_success "Development services started!"
            print_info "Frontend: http://localhost:5173"
            print_info "Backend: http://localhost:8000"
            print_info "Admin: http://localhost:8000/admin"
            print_info ""
            print_info "View logs: ./docker-helper.sh logs"
        fi
        ;;
    
    stop)
        MODE=${2:-dev}
        if [ "$MODE" == "prod" ]; then
            print_header "Stopping OneStep Services (PRODUCTION)"
            docker-compose -f docker-compose.prod.yml stop
        else
            print_header "Stopping OneStep Services (DEVELOPMENT)"
            docker-compose -f docker-compose.dev.yml stop
        fi
        print_success "Services stopped!"
        ;;
    
    restart)
        print_header "Restarting OneStep Services"
        docker-compose restart
        print_success "Services restarted!"
        ;;
    
    logs)
        MODE=${3:-dev}
        COMPOSE_FILE="docker-compose.dev.yml"
        if [ "$MODE" == "prod" ]; then
            COMPOSE_FILE="docker-compose.prod.yml"
        fi
        
        if [ -z "$2" ]; then
            docker-compose -f $COMPOSE_FILE logs -f --tail=100
        else
            docker-compose -f $COMPOSE_FILE logs -f --tail=100 "$2"
        fi
        ;;
    
    build)
        MODE=${2:-dev}
        NO_CACHE=""
        if [ "$3" == "--no-cache" ] || [ "$2" == "--no-cache" ]; then
            NO_CACHE="--no-cache"
        fi
        
        if [ "$MODE" == "prod" ]; then
            print_header "Building Docker Images (PRODUCTION)"
            docker-compose -f docker-compose.prod.yml build $NO_CACHE
        else
            print_header "Building Docker Images (DEVELOPMENT)"
            docker-compose -f docker-compose.dev.yml build $NO_CACHE
        fi
        print_success "Build complete!"
        ;;
    
    clean)
        print_header "Cleaning Docker Resources"
        print_warning "This will remove all containers, volumes, and images!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -a -f
            print_success "Cleanup complete!"
        else
            print_info "Cleanup cancelled"
        fi
        ;;
    
    reset)
        print_header "Resetting OneStep"
        print_warning "This will rebuild everything from scratch!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker-compose build --no-cache
            docker-compose up -d
            print_success "Reset complete!"
        else
            print_info "Reset cancelled"
        fi
        ;;
    
    status)
        print_header "OneStep Services Status"
        docker-compose ps
        ;;
    
    shell)
        if [ -z "$2" ]; then
            print_error "Please specify a service: frontend, backend, or db"
            exit 1
        fi
        
        case "$2" in
            frontend)
                docker-compose exec frontend sh
                ;;
            backend)
                docker-compose exec backend bash
                ;;
            db)
                docker-compose exec db psql -U onestep -d onestep
                ;;
            *)
                print_error "Unknown service: $2"
                exit 1
                ;;
        esac
        ;;
    
    migrate)
        print_header "Running Database Migrations"
        docker-compose exec backend python manage.py migrate
        print_success "Migrations complete!"
        ;;
    
    superuser)
        print_header "Creating Superuser"
        docker-compose exec backend python manage.py createsuperuser
        ;;
    
    test)
        if [ "$2" == "frontend" ]; then
            print_header "Running Frontend Tests"
            docker-compose exec frontend npm run test:unit
        elif [ "$2" == "backend" ]; then
            print_header "Running Backend Tests"
            docker-compose exec backend python manage.py test
        else
            print_error "Please specify: frontend or backend"
            exit 1
        fi
        ;;
    
    install)
        if [ "$2" == "frontend" ]; then
            print_header "Installing Frontend Dependencies"
            docker-compose exec frontend npm install
            print_success "Frontend dependencies installed!"
        elif [ "$2" == "backend" ]; then
            print_header "Installing Backend Dependencies"
            docker-compose exec backend pip install -r requirements.txt
            print_success "Backend dependencies installed!"
        else
            print_error "Please specify: frontend or backend"
            exit 1
        fi
        ;;
    
    help|*)
        print_header "OneStep Docker Helper"
        echo ""
        echo "Usage: ./docker-helper.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start [dev|prod]        Start all services (default: dev)"
        echo "  stop [dev|prod]         Stop all services (default: dev)"
        echo "  restart [dev|prod]      Restart all services (default: dev)"
        echo "  logs [service]          View logs (optional: specify service)"
        echo "  build [dev|prod] [--no-cache]  Build Docker images"
        echo "  clean                   Remove all containers, volumes, and images"
        echo "  reset                   Rebuild everything from scratch"
        echo "  status                  Show status of all services"
        echo "  shell <service>         Open shell in service (frontend|backend|db)"
        echo "  migrate                 Run database migrations"
        echo "  superuser               Create Django superuser"
        echo "  test <service>          Run tests (frontend|backend)"
        echo "  install <service>       Install dependencies (frontend|backend)"
        echo "  help                    Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./docker-helper.sh start              # Start in development mode"
        echo "  ./docker-helper.sh start prod         # Start in production mode"
        echo "  ./docker-helper.sh build prod         # Build production images"
        echo "  ./docker-helper.sh logs frontend"
        echo "  ./docker-helper.sh shell backend"
        echo "  ./docker-helper.sh build dev --no-cache"
        echo ""
        ;;
esac
