# Production Deployment Checklist

Use this checklist to ensure a smooth production deployment.

## Pre-Deployment

- [ ] Review `PRODUCTION.md` documentation
- [ ] Copy `.env.prod.example` to `.env.prod`
- [ ] Generate secure `SECRET_KEY` (50+ characters)
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Configure `CORS_ALLOWED_ORIGINS` if needed
- [ ] Review security settings in `.env.prod`
- [ ] Ensure Docker and Docker Compose are installed
- [ ] Verify domain DNS is configured

## Build and Deploy

- [ ] Build production images: `make prod-build`
- [ ] Start production services: `make prod-up`
- [ ] Verify containers are running: `docker-compose -f docker-compose.prod.yml ps`
- [ ] Check logs for errors: `make prod-logs`
- [ ] Run migrations: `make prod-migrate`
- [ ] Create superuser: `docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser`
- [ ] Collect static files (done automatically by entrypoint)

## Post-Deployment Verification

- [ ] Access admin interface: `http://your-domain:8000/admin/`
- [ ] Test API endpoints: `http://your-domain:8000/api/`
- [ ] Verify database connectivity
- [ ] Check health checks are passing
- [ ] Review application logs
- [ ] Test user authentication
- [ ] Verify CORS settings if using frontend

## Security Hardening

- [ ] Confirm `DEBUG=0` in production
- [ ] Verify security headers are enabled
- [ ] Ensure database is not exposed to public
- [ ] Review file permissions in containers
- [ ] Set up SSL/TLS certificates (recommended)
- [ ] Configure reverse proxy (nginx/HAProxy)
- [ ] Enable firewall rules
- [ ] Set up monitoring and alerting

## Backup Strategy

- [ ] Test database backup: `make prod-backup`
- [ ] Verify backup file is created in `backups/` directory
- [ ] Test database restore process
- [ ] Set up automated backup schedule (cron job)
- [ ] Configure off-site backup storage
- [ ] Document backup retention policy

## Monitoring Setup

- [ ] Configure log aggregation
- [ ] Set up application monitoring (APM)
- [ ] Configure uptime monitoring
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure resource usage alerts
- [ ] Set up database performance monitoring

## Maintenance Plan

- [ ] Document update procedure
- [ ] Schedule regular security updates
- [ ] Plan for database maintenance windows
- [ ] Set up log rotation
- [ ] Configure automated health checks
- [ ] Document rollback procedure

## Production Optimization

### Image Size Optimization
✅ Multi-stage build implemented
✅ Minimal base image (python:3.11-slim)
✅ Removed build dependencies from final image
✅ Cleaned up Python cache files
✅ Excluded unnecessary files via .dockerignore

### Security Enhancements
✅ Non-root user (appuser, UID 1000)
✅ No source code mount in production
✅ Database not exposed to host
✅ Security headers enabled (HSTS, secure cookies)
✅ Resource limits configured

### Performance Features
✅ Gunicorn with 4 workers, 2 threads
✅ Worker recycling (max 1000 requests)
✅ Graceful shutdown (30s timeout)
✅ Health checks configured
✅ Static files pre-collected

## Quick Commands Reference

```bash
# Start production
make prod-up

# View logs
make prod-logs

# Run migrations
make prod-migrate

# Backup database
make prod-backup

# Restore database
make prod-restore BACKUP_FILE=backups/backup_20240101_120000.sql

# Access shell
make prod-shell

# Stop production
make prod-down
```

## Troubleshooting

### Container won't start
1. Check logs: `make prod-logs`
2. Verify `.env.prod` exists and is configured
3. Check database health: `docker-compose -f docker-compose.prod.yml exec db pg_isready`

### Database connection errors
1. Verify database credentials in `.env.prod`
2. Check database container is running
3. Test connection: `make prod-shell` then `python manage.py dbshell`

### Performance issues
1. Check resource usage: `docker stats`
2. Review Gunicorn logs
3. Consider scaling: `docker-compose -f docker-compose.prod.yml up -d --scale web=3`

## Support Resources

- Production Guide: `PRODUCTION.md`
- Django Documentation: https://docs.djangoproject.com/
- Docker Documentation: https://docs.docker.com/
- Gunicorn Documentation: https://docs.gunicorn.org/
