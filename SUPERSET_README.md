# Apache Superset Integration for OneStep

This document provides a quick overview of the Apache Superset integration with the OneStep Django application.

## What is Superset?

Apache Superset is a modern, enterprise-ready business intelligence web application that allows you to:
- Create interactive dashboards
- Explore data with SQL Lab
- Build visualizations (charts, graphs, maps)
- Share insights with your team

## Quick Start

### 1. Start Services

```bash
make superset-up
```

This command starts:
- PostgreSQL database (shared with Django)
- Django web application
- Redis (for caching)
- Apache Superset

### 2. Access Superset

Wait 2-3 minutes for initialization, then open: **http://localhost:8088**

**Login Credentials:**
- Username: `admin`
- Password: `admin`

⚠️ **Important**: Change these credentials after first login!

### 3. Connect to Database

1. In Superset, go to **Settings** → **Database Connections**
2. Click **+ Database**
3. Select **PostgreSQL**
4. Enter connection string:
   ```
   postgresql://postgres:postgres@db:5432/onestep_dev
   ```
5. Click **Test Connection** → **Connect**

### 4. Create Your First Chart

1. Go to **Data** → **Datasets**
2. Click **+ Dataset**
3. Select your database and a table
4. Click **Add**
5. Click on the dataset to create a chart
6. Choose visualization type and configure
7. Click **Save**

## Available Commands

```bash
make superset-up          # Start all services with Superset
make superset-down        # Stop Superset services
make superset-logs        # View Superset logs
make superset-shell       # Open Superset container shell
make superset-reset       # Reset admin password
make superset-rebuild     # Rebuild Superset container
make superset-logs-all    # View all service logs
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Django App     │────▶│  PostgreSQL DB   │◀────│  Superset       │
│  (Port 8000)    │     │  (Port 5432)     │     │  (Port 8088)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                          │
                               │                          ▼
                               │                   ┌─────────────────┐
                               │                   │  Redis Cache    │
                               │                   │  (Port 6379)    │
                               │                   └─────────────────┘
                               │
                        ┌──────┴──────┐
                        │             │
                   onestep_dev    superset
                   (Django data)  (Superset metadata)
```

## Key Features

### 1. SQL Lab
- Write and execute SQL queries
- Save queries for reuse
- Export results to CSV
- Share queries with team

### 2. Chart Builder
- 50+ visualization types
- Drag-and-drop interface
- Real-time preview
- Custom styling options

### 3. Dashboards
- Combine multiple charts
- Interactive filters
- Auto-refresh capabilities
- Export to PDF/PNG

### 4. Data Exploration
- Browse database schema
- Preview table data
- Search across datasets
- Column statistics

## Example Use Cases

### Executive Dashboard
- Total organizational units by campus
- Active initiatives count
- Recent activity timeline
- Key performance indicators

### Campus Analytics
- Research groups per campus
- Initiative distribution
- Leadership statistics
- Growth trends

### People Management
- Top coordinators by initiative count
- Team size distribution
- Leadership changes over time
- Participation metrics

### Initiative Tracking
- Project timelines (Gantt chart)
- Completion rates
- Resource allocation
- Upcoming deadlines

## Database Tables

### Main Tables
- `organizational_group_organizationalunit` - Research groups
- `organizational_group_campus` - Campus locations
- `initiatives_initiative` - Programs, projects, events
- `people_person` - People (coordinators, leaders, members)

### Relationship Tables
- `organizational_group_organizationalunitleadership` - Leadership history
- `organizational_group_organizationalunit_members` - Unit membership
- `initiatives_initiative_team_members` - Initiative teams

## Configuration Files

- `docker-compose.superset.yml` - Docker services configuration
- `docker/superset/superset_config.py` - Superset settings
- `docker/superset/init-superset.sh` - Initialization script
- `.env.superset` - Environment variables

## Documentation

- **Full Setup Guide**: [docs/SUPERSET_SETUP.md](docs/SUPERSET_SETUP.md)
- **Quick Reference**: [docs/SUPERSET_QUICK_REFERENCE.md](docs/SUPERSET_QUICK_REFERENCE.md)
- **Official Docs**: https://superset.apache.org/docs/intro

## Troubleshooting

### Superset won't start
```bash
# Check logs
make superset-logs

# Restart
make superset-down
make superset-up
```

### Can't connect to database
- Verify database is running: `docker ps`
- Use `db` as hostname (not `localhost`)
- Check credentials match `.env.superset`

### Slow performance
- Enable caching on charts
- Add database indexes
- Use materialized views
- Limit result set size

## Security Notes

### For Development
- Default credentials are acceptable
- Database exposed on localhost:5432

### For Production
1. Change all default passwords
2. Use strong SECRET_KEY values
3. Enable HTTPS
4. Create read-only database user
5. Configure row-level security
6. Restrict network access
7. Enable audit logging

## Maintenance

### Backup Superset Data
```bash
docker exec onestep_db pg_dump -U postgres superset > superset_backup.sql
```

### Update Superset
```bash
docker-compose -f docker-compose.superset.yml pull superset
make superset-rebuild
```

### Clean Up
```bash
# Stop services
make superset-down

# Remove all data (WARNING: destructive)
docker-compose -f docker-compose.superset.yml down -v
```

## Support

For issues or questions:
1. Check the logs: `make superset-logs`
2. Review documentation in `docs/`
3. Visit [Superset GitHub](https://github.com/apache/superset)
4. Join [Superset Slack](https://apache-superset.slack.com/)

## Next Steps

1. ✅ Start services: `make superset-up`
2. ✅ Access Superset: http://localhost:8088
3. ✅ Connect to database
4. ✅ Create your first dataset
5. ✅ Build a chart
6. ✅ Create a dashboard
7. ✅ Share with your team

Happy visualizing! 📊
