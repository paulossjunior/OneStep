# Superset Architecture and Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Docker Host Machine                            │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    Docker Network (onestep_network)               │ │
│  │                                                                   │ │
│  │  ┌──────────────────┐                                            │ │
│  │  │   Django Web     │                                            │ │
│  │  │   Application    │                                            │ │
│  │  │                  │                                            │ │
│  │  │  - REST API      │                                            │ │
│  │  │  - Admin Panel   │                                            │ │
│  │  │  - Business      │                                            │ │
│  │  │    Logic         │                                            │ │
│  │  │                  │                                            │ │
│  │  │  Port: 8000      │                                            │ │
│  │  └────────┬─────────┘                                            │ │
│  │           │                                                       │ │
│  │           │ Read/Write                                           │ │
│  │           ▼                                                       │ │
│  │  ┌──────────────────┐         ┌──────────────────┐              │ │
│  │  │   PostgreSQL     │◀────────│   Apache         │              │ │
│  │  │   Database       │  Read   │   Superset       │              │ │
│  │  │                  │  Only   │                  │              │ │
│  │  │  ┌────────────┐  │         │  - Dashboards    │              │ │
│  │  │  │ onestep_dev│  │         │  - Charts        │              │ │
│  │  │  │ (Django    │  │         │  - SQL Lab       │              │ │
│  │  │  │  Data)     │  │         │  - Data Explorer │              │ │
│  │  │  └────────────┘  │         │                  │              │ │
│  │  │                  │         │  Port: 8088      │              │ │
│  │  │  ┌────────────┐  │         └────────┬─────────┘              │ │
│  │  │  │  superset  │  │                  │                        │ │
│  │  │  │ (Metadata) │  │                  │                        │ │
│  │  │  └────────────┘  │                  │                        │ │
│  │  │                  │                  │ Cache                  │ │
│  │  │  Port: 5432      │                  │ Queries                │ │
│  │  └──────────────────┘                  ▼                        │ │
│  │                              ┌──────────────────┐               │ │
│  │                              │   Redis Cache    │               │ │
│  │                              │                  │               │ │
│  │                              │  - Query Cache   │               │ │
│  │                              │  - Data Cache    │               │ │
│  │                              │  - Celery Queue  │               │ │
│  │                              │                  │               │ │
│  │                              │  Port: 6379      │               │ │
│  │                              └──────────────────┘               │ │
│  │                                                                  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        Docker Volumes                             │ │
│  │                                                                   │ │
│  │  postgres_data    - Database files (persistent)                  │ │
│  │  static_volume    - Django static files                          │ │
│  │  media_volume     - User uploads                                 │ │
│  │  redis_data       - Redis persistence                            │ │
│  │  superset_home    - Superset configuration and logs              │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
    localhost:8000      localhost:8088      localhost:5432
    (Django API)        (Superset UI)       (PostgreSQL)
```

## Data Flow

### 1. Django Application Flow

```
User Request
    │
    ▼
┌─────────────────┐
│  Django Views   │
│  & API          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django ORM     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  onestep_dev    │
└─────────────────┘
```

### 2. Superset Visualization Flow

```
User Opens Dashboard
    │
    ▼
┌─────────────────┐
│  Superset UI    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      Cache Hit?
│  Redis Cache    │◀─────────┐
└────────┬────────┘          │
         │ Cache Miss        │
         ▼                   │
┌─────────────────┐          │
│  SQL Query      │          │
│  Execution      │          │
└────────┬────────┘          │
         │                   │
         ▼                   │
┌─────────────────┐          │
│  PostgreSQL     │          │
│  onestep_dev    │          │
└────────┬────────┘          │
         │                   │
         ▼                   │
┌─────────────────┐          │
│  Store in Cache │──────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Render Chart   │
└─────────────────┘
```

### 3. Async Query Flow (Long-Running Queries)

```
User Submits Query
    │
    ▼
┌─────────────────┐
│  Superset UI    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Celery Task    │
│  Queue (Redis)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Background     │
│  Worker         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  Query          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Store Results  │
│  in Redis       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Notify User    │
│  (WebSocket)    │
└─────────────────┘
```

## Database Schema

### Django Application Tables

```
┌─────────────────────────────────────────────────────────────┐
│                    onestep_dev Database                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Core Tables:                                               │
│  ├── organizational_group_organizationalunit                │
│  ├── organizational_group_campus                            │
│  ├── organizational_group_organization                      │
│  ├── organizational_group_organizationaltype                │
│  ├── organizational_group_knowledgearea                     │
│  ├── initiatives_initiative                                 │
│  ├── initiatives_initiativetype                             │
│  └── people_person                                          │
│                                                             │
│  Relationship Tables:                                       │
│  ├── organizational_group_organizationalunitleadership      │
│  ├── organizational_group_organizationalunit_members        │
│  ├── organizational_group_organizationalunit_initiatives    │
│  ├── initiatives_initiative_team_members                    │
│  └── initiatives_initiative_students                        │
│                                                             │
│  Django System Tables:                                      │
│  ├── django_migrations                                      │
│  ├── django_content_type                                    │
│  ├── django_session                                         │
│  └── auth_*                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Superset Metadata Tables

```
┌─────────────────────────────────────────────────────────────┐
│                    superset Database                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Configuration:                                             │
│  ├── dbs (database connections)                             │
│  ├── tables (datasets)                                      │
│  └── table_columns                                          │
│                                                             │
│  Visualizations:                                            │
│  ├── slices (charts)                                        │
│  ├── dashboards                                             │
│  └── dashboard_slices (chart-dashboard mapping)             │
│                                                             │
│  User Management:                                           │
│  ├── ab_user (users)                                        │
│  ├── ab_role (roles)                                        │
│  └── ab_permission (permissions)                            │
│                                                             │
│  Query History:                                             │
│  ├── query (saved queries)                                  │
│  └── logs (audit logs)                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Network Communication

### Port Mapping

```
Host Machine                Docker Container
─────────────               ────────────────

localhost:8000      ───▶    web:8000 (Django)
localhost:8088      ───▶    superset:8088 (Superset)
localhost:5432      ───▶    db:5432 (PostgreSQL)
(not exposed)       ───▶    redis:6379 (Redis)
```

### Internal DNS Resolution

Within the Docker network, services communicate using container names:

```
web         → db:5432         (Django to PostgreSQL)
superset    → db:5432         (Superset to PostgreSQL)
superset    → redis:6379      (Superset to Redis)
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Security Layers                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Network Isolation                                 │
│  └── Docker network isolates services from host             │
│                                                             │
│  Layer 2: Authentication                                    │
│  ├── Django: Session/JWT authentication                     │
│  └── Superset: Username/password + role-based access        │
│                                                             │
│  Layer 3: Database Access                                   │
│  ├── Django: Full read/write access                         │
│  └── Superset: Read-only recommended (configurable)         │
│                                                             │
│  Layer 4: Application Security                              │
│  ├── CSRF protection                                        │
│  ├── XSS prevention                                         │
│  ├── SQL injection protection (ORM)                         │
│  └── Rate limiting                                          │
│                                                             │
│  Layer 5: Data Security                                     │
│  ├── Row-level security (Superset)                          │
│  ├── Column-level permissions                               │
│  └── Audit logging                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Performance Optimization

### Caching Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Caching Hierarchy                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Level 1: Browser Cache                                     │
│  └── Static assets, chart images                            │
│      TTL: 1 hour                                            │
│                                                             │
│  Level 2: Redis Cache (Superset)                            │
│  ├── Query results                                          │
│  │   TTL: 1 hour (configurable per chart)                  │
│  └── Dashboard metadata                                     │
│      TTL: 5 minutes                                         │
│                                                             │
│  Level 3: PostgreSQL Query Cache                            │
│  └── Frequently accessed data                               │
│      Managed by PostgreSQL                                  │
│                                                             │
│  Level 4: Materialized Views                                │
│  └── Pre-computed aggregations                              │
│      Refresh: On-demand or scheduled                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Query Optimization

```
User Query
    │
    ▼
┌─────────────────┐
│  Check Cache    │──── Hit ────▶ Return Cached Result
└────────┬────────┘
         │ Miss
         ▼
┌─────────────────┐
│  Query          │
│  Optimization   │
│  - Use indexes  │
│  - Limit rows   │
│  - Join         │
│    optimization │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute Query  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cache Result   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Return to User │
└─────────────────┘
```

## Deployment Considerations

### Development Environment (Current)

```
┌─────────────────────────────────────────────────────────────┐
│  Development Setup                                          │
├─────────────────────────────────────────────────────────────┤
│  ✓ All services on single host                              │
│  ✓ SQLite or PostgreSQL                                     │
│  ✓ Debug mode enabled                                       │
│  ✓ Default credentials                                      │
│  ✓ Hot reload enabled                                       │
│  ✓ Detailed logging                                         │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│  Production Setup                                           │
├─────────────────────────────────────────────────────────────┤
│  ✓ Separate database server                                 │
│  ✓ Redis cluster for high availability                      │
│  ✓ Load balancer for Django/Superset                        │
│  ✓ HTTPS with SSL certificates                              │
│  ✓ Strong passwords and secrets                             │
│  ✓ Read-only database user for Superset                     │
│  ✓ Backup and disaster recovery                             │
│  ✓ Monitoring and alerting                                  │
│  ✓ Rate limiting and DDoS protection                        │
└─────────────────────────────────────────────────────────────┘
```

## Monitoring and Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Application Logs:                                          │
│  ├── Django: /app/logs/django.log                           │
│  ├── Superset: /app/superset_home/superset.log             │
│  └── PostgreSQL: Docker logs                                │
│                                                             │
│  Metrics:                                                   │
│  ├── Request count and latency                              │
│  ├── Database query performance                             │
│  ├── Cache hit/miss ratio                                   │
│  └── Resource utilization (CPU, memory, disk)               │
│                                                             │
│  Health Checks:                                             │
│  ├── Django: /admin/ endpoint                               │
│  ├── Superset: /health endpoint                             │
│  ├── PostgreSQL: pg_isready                                 │
│  └── Redis: PING command                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Backup and Recovery

```
┌─────────────────────────────────────────────────────────────┐
│                  Backup Strategy                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Daily Backups:                                             │
│  ├── PostgreSQL dump (onestep_dev)                          │
│  ├── PostgreSQL dump (superset)                             │
│  └── Docker volumes snapshot                                │
│                                                             │
│  Backup Commands:                                           │
│  ├── make backup (Django database)                          │
│  └── docker exec onestep_db pg_dump -U postgres superset    │
│                                                             │
│  Recovery:                                                  │
│  ├── Restore from SQL dump                                  │
│  ├── Recreate containers                                    │
│  └── Restore volumes                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Scaling Considerations

### Horizontal Scaling

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Django      │ │  Django      │ │  Django      │
    │  Instance 1  │ │  Instance 2  │ │  Instance 3  │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │  PostgreSQL  │
                  │  (Primary)   │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  PostgreSQL  │
                  │  (Replica)   │
                  └──────────────┘
```

### Vertical Scaling

```
Resource Allocation:
├── Django: 2 CPU, 4GB RAM
├── Superset: 2 CPU, 4GB RAM
├── PostgreSQL: 4 CPU, 8GB RAM
└── Redis: 1 CPU, 2GB RAM
```

This architecture provides a robust, scalable foundation for data visualization and business intelligence on top of your Django application.
