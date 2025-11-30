# Apache Superset Integration Guide

This guide explains how to set up and use Apache Superset with the OneStep Django application for data visualization and business intelligence.

## Overview

Apache Superset is an open-source data exploration and visualization platform that connects to your OneStep PostgreSQL database to create interactive dashboards and charts.

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

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM
- Ports 8000, 8088, 5432, and 6379 available

## Quick Start

### 1. Start the Services

```bash
# Start all services (Django, PostgreSQL, Redis, Superset)
docker-compose -f docker-compose.superset.yml up -d

# Check service status
docker-compose -f docker-compose.superset.yml ps

# View logs
docker-compose -f docker-compose.superset.yml logs -f superset
```

### 2. Wait for Initialization

The first startup takes 2-3 minutes as Superset:
- Creates its metadata database
- Initializes the schema
- Creates the admin user
- Starts the web server

Watch the logs until you see:
```
superset | Superset initialization complete!
superset | [INFO] Booting worker with pid: ...
```

### 3. Access Superset

Open your browser and navigate to: **http://localhost:8088**

**Default Credentials:**
- Username: `admin`
- Password: `admin`

⚠️ **Change these credentials in production!**

## Connecting to OneStep Database

### Step 1: Add Database Connection

1. Log in to Superset
2. Click **Settings** → **Database Connections**
3. Click **+ Database** button
4. Select **PostgreSQL** as the database type

### Step 2: Configure Connection

**Option A: Using the Connection String**

```
postgresql://postgres:postgres@db:5432/onestep_dev
```

**Option B: Using the Form**

- **Host**: `db`
- **Port**: `5432`
- **Database**: `onestep_dev`
- **Username**: `postgres`
- **Password**: `postgres`
- **Display Name**: `OneStep Database`

### Step 3: Test Connection

1. Click **Test Connection**
2. If successful, click **Connect**

### Step 4: Configure Advanced Settings (Optional)

Under **Advanced** tab:
- **Expose database in SQL Lab**: ✓ (Enable)
- **Allow CREATE TABLE AS**: ✓ (Enable)
- **Allow CREATE VIEW AS**: ✓ (Enable)
- **Allow DML**: ✗ (Disable for safety)

## Creating Your First Dashboard

### 1. Add a Dataset

1. Go to **Data** → **Datasets**
2. Click **+ Dataset**
3. Select:
   - **Database**: OneStep Database
   - **Schema**: public
   - **Table**: Choose a table (e.g., `organizational_group_organizationalunit`)
4. Click **Add**

### 2. Create a Chart

1. Click on your dataset
2. Choose a visualization type (e.g., **Table**, **Bar Chart**, **Pie Chart**)
3. Configure:
   - **Metrics**: Count, Sum, Average, etc.
   - **Dimensions**: Group by fields
   - **Filters**: Add conditions
4. Click **Update Chart**
5. Click **Save** and give it a name

### 3. Build a Dashboard

1. Go to **Dashboards**
2. Click **+ Dashboard**
3. Give it a name (e.g., "Organizational Overview")
4. Click **Edit Dashboard**
5. Drag and drop your charts
6. Resize and arrange as needed
7. Click **Save**

## Example Queries and Visualizations

### Query 1: Research Groups by Campus

```sql
SELECT 
    c.name as campus_name,
    COUNT(ou.id) as group_count
FROM organizational_group_campus c
LEFT JOIN organizational_group_organizationalunit ou ON ou.campus_id = c.id
GROUP BY c.name
ORDER BY group_count DESC;
```

**Visualization**: Bar Chart or Pie Chart

### Query 2: Initiatives by Type

```sql
SELECT 
    it.name as initiative_type,
    COUNT(i.id) as count,
    COUNT(DISTINCT i.coordinator_id) as unique_coordinators
FROM initiatives_initiative i
JOIN initiatives_initiativetype it ON i.type_id = it.id
GROUP BY it.name;
```

**Visualization**: Pie Chart or Table

### Query 3: Top Coordinators by Initiative Count

```sql
SELECT 
    p.name as coordinator_name,
    COUNT(i.id) as initiative_count,
    STRING_AGG(DISTINCT it.name, ', ') as initiative_types
FROM people_person p
JOIN initiatives_initiative i ON i.coordinator_id = p.id
JOIN initiatives_initiativetype it ON i.type_id = it.id
GROUP BY p.name
ORDER BY initiative_count DESC
LIMIT 10;
```

**Visualization**: Table or Bar Chart

### Query 4: Initiative Timeline

```sql
SELECT 
    i.name as initiative_name,
    i.start_date,
    i.end_date,
    it.name as type,
    p.name as coordinator
FROM initiatives_initiative i
JOIN initiatives_initiativetype it ON i.type_id = it.id
JOIN people_person p ON i.coordinator_id = p.id
WHERE i.start_date IS NOT NULL
ORDER BY i.start_date DESC;
```

**Visualization**: Gantt Chart or Timeline

### Query 5: Organizational Unit Membership

```sql
SELECT 
    ou.name as unit_name,
    ou.short_name,
    c.name as campus,
    COUNT(DISTINCT oul.person_id) as leader_count,
    COUNT(DISTINCT m.person_id) as member_count
FROM organizational_group_organizationalunit ou
JOIN organizational_group_campus c ON ou.campus_id = c.id
LEFT JOIN organizational_group_organizationalunitleadership oul 
    ON oul.unit_id = ou.id AND oul.is_active = true
LEFT JOIN organizational_group_organizationalunit_members m 
    ON m.organizationalunit_id = ou.id
GROUP BY ou.name, ou.short_name, c.name
ORDER BY member_count DESC;
```

**Visualization**: Table with conditional formatting

## Available Tables

### Core Tables

- `organizational_group_organizationalunit` - Research groups/units
- `organizational_group_campus` - Campus locations
- `organizational_group_organizationaltype` - Unit types
- `organizational_group_organization` - Parent organizations
- `organizational_group_knowledgearea` - Knowledge areas
- `initiatives_initiative` - Programs, projects, events
- `initiatives_initiativetype` - Initiative types
- `people_person` - People (coordinators, leaders, members)

### Relationship Tables

- `organizational_group_organizationalunitleadership` - Unit leadership history
- `organizational_group_organizationalunit_members` - Unit membership
- `organizational_group_organizationalunit_initiatives` - Unit-initiative associations
- `initiatives_initiative_team_members` - Initiative team members
- `initiatives_initiative_students` - Initiative student participants

## Dashboard Examples

### 1. Executive Overview Dashboard

**Charts:**
- Total counts (KPI cards): Units, Initiatives, People
- Research groups by campus (Pie chart)
- Initiatives by type (Bar chart)
- Recent initiatives (Table)
- Active vs completed initiatives (Line chart over time)

### 2. Campus Analytics Dashboard

**Charts:**
- Campus comparison (Multi-bar chart)
- Unit distribution by type per campus (Stacked bar)
- Top campuses by initiative count (Bar chart)
- Campus growth over time (Line chart)

### 3. People & Leadership Dashboard

**Charts:**
- Top coordinators (Table with metrics)
- Leadership distribution (Treemap)
- Team size distribution (Histogram)
- People involvement over time (Area chart)

### 4. Initiative Tracking Dashboard

**Charts:**
- Initiative timeline (Gantt chart)
- Initiatives by status (Funnel chart)
- Average initiative duration (KPI card)
- Initiative completion rate (Gauge chart)
- Upcoming deadlines (Table)

## Performance Optimization

### 1. Enable Caching

Superset uses Redis for caching. Configure cache timeout in charts:
- Go to chart settings
- Set **Cache Timeout**: 3600 (1 hour)

### 2. Create Database Views

For complex queries, create PostgreSQL views:

```sql
-- Connect to your database
docker exec -it onestep_db psql -U postgres -d onestep_dev

-- Create a view
CREATE VIEW v_unit_summary AS
SELECT 
    ou.id,
    ou.name,
    ou.short_name,
    c.name as campus_name,
    ot.name as type_name,
    COUNT(DISTINCT oul.person_id) as leader_count,
    COUNT(DISTINCT m.person_id) as member_count,
    COUNT(DISTINCT i.id) as initiative_count
FROM organizational_group_organizationalunit ou
JOIN organizational_group_campus c ON ou.campus_id = c.id
LEFT JOIN organizational_group_organizationaltype ot ON ou.type_id = ot.id
LEFT JOIN organizational_group_organizationalunitleadership oul 
    ON oul.unit_id = ou.id AND oul.is_active = true
LEFT JOIN organizational_group_organizationalunit_members m 
    ON m.organizationalunit_id = ou.id
LEFT JOIN organizational_group_organizationalunit_initiatives ui 
    ON ui.organizationalunit_id = ou.id
LEFT JOIN initiatives_initiative i ON i.id = ui.initiative_id
GROUP BY ou.id, ou.name, ou.short_name, c.name, ot.name;
```

Then add the view as a dataset in Superset.

### 3. Use Async Queries

For long-running queries:
1. Enable async query execution in database settings
2. Queries will run in the background
3. Results are cached for faster subsequent access

## Security Best Practices

### 1. Change Default Credentials

```bash
# Access Superset container
docker exec -it superset bash

# Change admin password
superset fab reset-password --username admin
```

### 2. Configure Row-Level Security

1. Go to **Settings** → **Row Level Security**
2. Create filters to restrict data access by user role
3. Apply filters to datasets

### 3. Limit Database Permissions

Create a read-only database user for Superset:

```sql
-- Connect to PostgreSQL
docker exec -it onestep_db psql -U postgres -d onestep_dev

-- Create read-only user
CREATE USER superset_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE onestep_dev TO superset_readonly;
GRANT USAGE ON SCHEMA public TO superset_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_readonly;
```

Update Superset connection to use this user.

### 4. Enable HTTPS

For production, configure HTTPS:
- Use a reverse proxy (Nginx, Traefik)
- Obtain SSL certificates (Let's Encrypt)
- Update `SUPERSET_WEBSERVER_PROTOCOL = 'https'` in config

## Troubleshooting

### Issue: Superset won't start

**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.superset.yml logs superset

# Restart services
docker-compose -f docker-compose.superset.yml restart superset

# Rebuild if needed
docker-compose -f docker-compose.superset.yml up -d --build superset
```

### Issue: Cannot connect to database

**Solution:**
- Verify database is running: `docker-compose -f docker-compose.superset.yml ps`
- Check connection string uses `db` as hostname (not `localhost`)
- Ensure database name matches: `onestep_dev`

### Issue: Charts not loading

**Solution:**
- Clear browser cache
- Check Redis is running: `docker-compose -f docker-compose.superset.yml ps redis`
- Restart Redis: `docker-compose -f docker-compose.superset.yml restart redis`

### Issue: Slow query performance

**Solution:**
- Add database indexes on frequently queried columns
- Use materialized views for complex aggregations
- Enable query result caching
- Limit result set size

## Maintenance

### Backup Superset Metadata

```bash
# Backup Superset database
docker exec onestep_db pg_dump -U postgres superset > superset_backup.sql

# Restore
docker exec -i onestep_db psql -U postgres superset < superset_backup.sql
```

### Update Superset

```bash
# Pull latest image
docker-compose -f docker-compose.superset.yml pull superset

# Restart with new image
docker-compose -f docker-compose.superset.yml up -d superset

# Run database migrations
docker exec superset superset db upgrade
```

### Clean Up

```bash
# Stop all services
docker-compose -f docker-compose.superset.yml down

# Remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.superset.yml down -v
```

## Additional Resources

- [Superset Documentation](https://superset.apache.org/docs/intro)
- [Superset GitHub](https://github.com/apache/superset)
- [SQL Lab Guide](https://superset.apache.org/docs/creating-charts-dashboards/creating-your-first-dashboard)
- [Chart Types](https://superset.apache.org/docs/creating-charts-dashboards/exploring-data)

## Support

For issues specific to OneStep integration:
1. Check the logs: `docker-compose -f docker-compose.superset.yml logs`
2. Verify database connectivity
3. Review Superset configuration in `docker/superset/superset_config.py`

For Superset-specific issues:
- Visit [Superset Slack](https://apache-superset.slack.com/)
- Check [GitHub Issues](https://github.com/apache/superset/issues)
