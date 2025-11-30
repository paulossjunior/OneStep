# PostgreSQL Docker Configuration

This directory contains PostgreSQL initialization scripts and configuration files for the Docker setup.

## Initialization Scripts

### init-db.sh

This script runs automatically when the PostgreSQL container is first created. It can be used to:
- Create additional databases
- Set up additional users
- Configure database permissions
- Run initial SQL commands

The script is mounted as read-only in the container at `/docker-entrypoint-initdb.d/init-db.sh`.

## Environment Variables

The PostgreSQL container is configured using the following environment variables:

- `POSTGRES_DB`: Name of the default database (default: `onestep_dev`)
- `POSTGRES_USER`: PostgreSQL superuser name (default: `postgres`)
- `POSTGRES_PASSWORD`: PostgreSQL superuser password (default: `postgres`)

## Data Persistence

Database data is persisted using a Docker named volume `postgres_data`. This ensures that:
- Data survives container restarts
- Data is preserved when containers are removed
- Database state is maintained across deployments

## Performance Tuning

The PostgreSQL container includes:
- UTF-8 encoding by default
- 128MB shared memory allocation for improved performance
- Optimized health checks for faster startup detection

## Health Checks

The container includes a health check that:
- Runs every 10 seconds
- Uses `pg_isready` to verify database availability
- Allows 5 retries before marking as unhealthy
- Has a 10-second start period for initial setup

## Security Considerations

For production deployments:
1. Change default passwords in environment variables
2. Use secrets management for sensitive data
3. Restrict database access to internal Docker network only
4. Enable SSL/TLS for database connections
5. Implement regular backup strategies
