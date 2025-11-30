# Production Deployment Guide

This guide covers deploying the OneStep Django application in a production environment using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name configured (for HTTPS)
- SSL/TLS certificates (recommended: Let's Encrypt)

## Production Setup

### 1. Environment Configuration

Copy the production environment template:

```bash
cp .env.prod.example .env.prod
```

Edit `.env.prod` and update all values:

**Critical Settings:**
- `SECRET_KEY`: Generate a strong random key (50+ characters)
- `POSTGRES_PASSWORD`: Use a strong, unique password
- `ALLOWED_HOSTS`: Set to your domain(s)
- `CORS_ALLOWED_ORIGINS`: Set to your frontend domain(s)

**Generate a secure SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Build Production Images

Build the optimized production Docker images:

```bash
docker-compose -f docker-compose.prod.yml build
```

### 3. Start Production Services

Start all services in production mode:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Create Superuser

Create an admin user for Django admin:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 5. Verify Deployment

Check service health:

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs web
```

Access the application:
- Admin: `http://your-domain:8000/admin/`
- API: `http://your-domain:8000/api/`

## Production Features

### Security Enhancements

1. **Non-root User**: Application runs as `appuser` (UID 1000)
2. **No Source Code Mount**: Code is baked into the image
3. **Database Isolation**: PostgreSQL not exposed to host
4. **Security Headers**: HSTS, secure cookies enabled
5. **Resource Limits**: CPU and memory constraints configured

### Performance Optimizations

1. **Multi-stage Build**: Reduced image size (~200MB smaller)
2. **Gunicorn WSGI Server**: 4 workers with 2 threads each
3. **Worker Recycling**: Max 1000 requests per worker
4. **Static File Serving**: Pre-collected static files
5. **Database Connection Pooling**: Configured in Django settings

### High Availability

1. **Health Checks**: Automatic container restart on failure
2. **Graceful Shutdown**: 30-second graceful timeout
3. **Restart Policy**: Always restart on failure
4. **Volume Persistence**: Data survives container restarts

## Maintenance Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Web service only
docker-compose -f docker-compose.prod.yml logs -f web

# Database service only
docker-compose -f docker-compose.prod.yml logs -f db
```

### Database Migrations

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Collect Static Files

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Database Backup

```bash
# Backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T db psql -U $POSTGRES_USER $POSTGRES_DB < backup.sql
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

## Monitoring

### Resource Usage

```bash
# Container stats
docker stats onestep_web_prod onestep_db_prod

# Disk usage
docker system df
```

### Application Logs

Logs are stored in the `logs_volume_prod` volume:
- Gunicorn access logs: `/app/logs/gunicorn-access.log`
- Gunicorn error logs: `/app/logs/gunicorn-error.log`
- Django logs: `/app/logs/django.log`

Access logs:
```bash
docker-compose -f docker-compose.prod.yml exec web tail -f /app/logs/gunicorn-access.log
```

## Scaling

### Horizontal Scaling

Scale web service to multiple instances:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

**Note**: You'll need a load balancer (nginx, HAProxy) in front of multiple web instances.

### Vertical Scaling

Adjust resource limits in `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs web
```

Common issues:
- Database not ready: Wait for health check to pass
- Missing environment variables: Check `.env.prod`
- Port already in use: Change `WEB_PORT` in `.env.prod`

### Database Connection Errors

Verify database is healthy:
```bash
docker-compose -f docker-compose.prod.yml exec db pg_isready -U $POSTGRES_USER
```

Test connection from web container:
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### Performance Issues

1. Check resource usage: `docker stats`
2. Review Gunicorn logs for slow requests
3. Analyze database query performance
4. Consider increasing worker count or resources

## Security Checklist

- [ ] `SECRET_KEY` is unique and not committed to version control
- [ ] `DEBUG=0` in production
- [ ] Strong database password set
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL/TLS certificates configured (if using HTTPS)
- [ ] Security headers enabled (HSTS, secure cookies)
- [ ] Database not exposed to public internet
- [ ] Regular security updates applied
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured

## Reverse Proxy Setup (Optional)

For HTTPS and better performance, use nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

## Support

For issues or questions:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Review this documentation
3. Check Django documentation: https://docs.djangoproject.com/
4. Check Docker documentation: https://docs.docker.com/
