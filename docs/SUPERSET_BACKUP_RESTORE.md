# Superset Backup and Restore Guide

This guide explains how to backup and restore your Apache Superset instance, including all dashboards, charts, datasets, and configurations.

## Overview

The backup system includes:
- **Superset metadata database** - All dashboards, charts, datasets, users, permissions
- **Superset home directory** - User uploads, thumbnails, cached data
- **Configuration files** - superset_config.py, init scripts, Dockerfile
- **Exported assets** - Dashboard and datasource exports in portable format

## Prerequisites

- Docker and Docker Compose installed
- Superset containers running (`docker-compose -f docker-compose.superset.yml up -d`)
- Sufficient disk space for backups (typically 100MB - 1GB depending on usage)

## Backup Process

### Quick Backup

To create a backup with an automatic timestamp:

```bash
./scripts/backup_superset.sh
```

This creates a backup named `backup_YYYYMMDD_HHMMSS.tar.gz` in the `backups/superset/` directory.

### Named Backup

To create a backup with a custom name:

```bash
./scripts/backup_superset.sh my_backup_name
```

This creates `my_backup_name.tar.gz` in the `backups/superset/` directory.

### What Gets Backed Up

1. **Superset Database** (`superset_db.sql`)
   - All dashboards and their configurations
   - All charts and visualizations
   - All datasets and database connections
   - User accounts and permissions
   - Saved queries and query history

2. **Superset Home Directory** (`superset_home.tar.gz`)
   - User-uploaded files
   - Dashboard thumbnails
   - Cached query results
   - Temporary files

3. **Configuration Files** (`config/`)
   - `superset_config.py` - Main configuration
   - `init-superset.sh` - Initialization script
   - `Dockerfile` - Container build configuration
   - `env.superset.template` - Environment variables (passwords removed)

4. **Exported Assets** (`assets/`)
   - `dashboards.zip` - Portable dashboard exports
   - `datasources.yaml` - Database connection configurations

5. **Backup Metadata** (`backup_info.txt`)
   - Backup timestamp and system information
   - Restore instructions

### Backup Retention

The backup script automatically keeps the last 7 backups and removes older ones. You can modify this in the script by changing the `keep_count` variable.

### Scheduled Backups

To schedule automatic backups, add a cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/onestep && ./scripts/backup_superset.sh daily_backup >> /var/log/superset_backup.log 2>&1

# Add weekly backup on Sundays at 3 AM
0 3 * * 0 cd /path/to/onestep && ./scripts/backup_superset.sh weekly_backup >> /var/log/superset_backup.log 2>&1
```

## Restore Process

### List Available Backups

To see all available backups:

```bash
./scripts/restore_superset.sh
```

This displays all backup files in the `backups/superset/` directory.

### Restore from Backup

To restore from a specific backup:

```bash
./scripts/restore_superset.sh backup_20241110_143022
```

Or with a custom backup name:

```bash
./scripts/restore_superset.sh my_backup_name
```

### Restore Process Steps

The restore script will:

1. **Verify prerequisites** - Check Docker and containers are running
2. **Confirm action** - Ask for confirmation (this is destructive!)
3. **Extract backup** - Unpack the backup archive
4. **Stop Superset** - Temporarily stop the Superset container
5. **Restore database** - Drop and recreate the Superset database
6. **Restore home directory** - Replace Superset home with backup
7. **Start Superset** - Restart the container
8. **Upgrade schema** - Run database migrations if needed
9. **Cleanup** - Remove temporary files

### Important Notes

⚠️ **WARNING**: Restoring a backup will:
- **Delete all current Superset data**
- **Replace all dashboards and charts**
- **Reset all user accounts and permissions**
- **Remove any changes made since the backup**

Always create a backup before restoring to preserve current state if needed.

## Backup Best Practices

### 1. Regular Backups

Create backups:
- **Before major changes** - New dashboards, configuration changes
- **Daily** - For production environments with active development
- **Weekly** - For stable production environments
- **Before upgrades** - Always backup before upgrading Superset

### 2. Test Restores

Periodically test your backups by:
1. Creating a test environment
2. Restoring a backup
3. Verifying all dashboards and data are accessible

### 3. Off-site Storage

For production environments:
- Copy backups to remote storage (S3, Google Cloud Storage, etc.)
- Use encryption for sensitive data
- Maintain multiple backup locations

Example: Copy to S3
```bash
# After backup
aws s3 cp backups/superset/backup_20241110_143022.tar.gz \
  s3://my-bucket/superset-backups/
```

### 4. Monitor Backup Size

Keep track of backup sizes to:
- Ensure sufficient disk space
- Identify unusual growth patterns
- Plan storage requirements

```bash
# Check backup sizes
du -h backups/superset/*.tar.gz
```

## Troubleshooting

### Backup Fails

**Problem**: "Container 'superset' is not running"

**Solution**: Start the containers:
```bash
docker-compose -f docker-compose.superset.yml up -d
```

**Problem**: "Permission denied"

**Solution**: Make scripts executable:
```bash
chmod +x scripts/backup_superset.sh scripts/restore_superset.sh
```

### Restore Fails

**Problem**: "Database restore failed"

**Solution**: 
1. Check database container logs: `docker logs onestep_db`
2. Verify database credentials in `.env.superset`
3. Ensure sufficient disk space

**Problem**: "Superset won't start after restore"

**Solution**:
1. Check Superset logs: `docker logs superset`
2. Try manual database upgrade:
   ```bash
   docker exec superset superset db upgrade
   ```
3. Restart the container:
   ```bash
   docker restart superset
   ```

### Backup Too Large

**Problem**: Backups are consuming too much disk space

**Solution**:
1. Clean up old query results:
   ```bash
   docker exec superset superset cleanup-thumbnails
   ```
2. Reduce backup retention (edit `keep_count` in backup script)
3. Archive old backups to remote storage

## Manual Backup (Alternative)

If you prefer manual backups:

### Database Only

```bash
docker exec -e PGPASSWORD=postgres onestep_db \
  pg_dump -U postgres -d superset > superset_backup.sql
```

### Superset Home Only

```bash
docker exec superset tar czf - /app/superset_home > superset_home.tar.gz
```

## Recovery Scenarios

### Scenario 1: Accidental Dashboard Deletion

1. Create a backup of current state (optional)
2. Restore from most recent backup
3. Export the recovered dashboard
4. Restore current state backup
5. Import the recovered dashboard

### Scenario 2: Configuration Error

1. Restore from backup before the configuration change
2. Review and fix the configuration
3. Apply changes carefully

### Scenario 3: Database Corruption

1. Stop Superset: `docker stop superset`
2. Restore database from backup
3. Start Superset: `docker start superset`
4. Verify data integrity

### Scenario 4: Complete System Failure

1. Rebuild infrastructure
2. Deploy Superset containers
3. Restore from most recent backup
4. Verify all services are operational

## Backup Storage Recommendations

### Development Environment
- Local backups: 7 days retention
- Location: `backups/superset/`

### Staging Environment
- Local backups: 14 days retention
- Remote backups: 30 days retention
- Automated daily backups

### Production Environment
- Local backups: 30 days retention
- Remote backups: 90 days retention
- Automated daily backups
- Weekly full system backups
- Monthly archive backups (1 year retention)

## Security Considerations

### Backup Security

1. **Encrypt backups** containing sensitive data:
   ```bash
   gpg --encrypt --recipient your@email.com backup.tar.gz
   ```

2. **Secure backup storage**:
   - Use encrypted storage volumes
   - Restrict access permissions
   - Use secure transfer protocols (SFTP, S3 with encryption)

3. **Sanitize backups** for non-production use:
   - Remove production credentials
   - Anonymize sensitive data
   - Remove user personal information

### Access Control

- Limit backup script execution to authorized users
- Use separate credentials for backup operations
- Audit backup and restore operations
- Monitor backup access logs

## Automation Examples

### Backup Before Deployment

```bash
#!/bin/bash
# pre-deploy.sh

echo "Creating pre-deployment backup..."
./scripts/backup_superset.sh pre_deploy_$(date +%Y%m%d_%H%M%S)

if [ $? -eq 0 ]; then
    echo "Backup successful, proceeding with deployment..."
    # Your deployment commands here
else
    echo "Backup failed, aborting deployment!"
    exit 1
fi
```

### Backup with Notification

```bash
#!/bin/bash
# backup-with-notification.sh

./scripts/backup_superset.sh

if [ $? -eq 0 ]; then
    # Send success notification (example with curl to Slack)
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"Superset backup completed successfully"}' \
      YOUR_SLACK_WEBHOOK_URL
else
    # Send failure notification
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"Superset backup FAILED!"}' \
      YOUR_SLACK_WEBHOOK_URL
fi
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker logs superset` and `docker logs onestep_db`
3. Consult the main Superset documentation: https://superset.apache.org/docs/
4. Check the project README and other documentation in `docs/`

## Related Documentation

- [Superset Setup Guide](SUPERSET_SETUP.md)
- [Superset Architecture](SUPERSET_ARCHITECTURE.md)
- [Superset Quick Reference](SUPERSET_QUICK_REFERENCE.md)
