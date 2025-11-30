# Makefile Command Reference

Complete reference for all Makefile commands in the OneStep project.

## Quick Start

```bash
# Show all available commands
make help

# Initial setup
make setup

# Start development server
make dev

# Start Docker environment
make docker-setup
```

## Superset Backup & Restore Commands

### Backup Commands

#### `make superset-backup`
Create a timestamped backup of Superset.

```bash
make superset-backup
```

**Output:** `backups/superset/backup_YYYYMMDD_HHMMSS.tar.gz`

---

#### `make superset-backup-named NAME=<name>`
Create a backup with a custom name.

```bash
make superset-backup-named NAME=before_upgrade
make superset-backup-named NAME=production_snapshot
```

**Output:** `backups/superset/<name>.tar.gz`

---

#### `make superset-backup-daily`
Create a daily backup with date in filename.

```bash
make superset-backup-daily
```

**Output:** `backups/superset/daily_YYYYMMDD.tar.gz`

---

#### `make superset-backup-weekly`
Create a weekly backup with week number.

```bash
make superset-backup-weekly
```

**Output:** `backups/superset/weekly_YYYY_weekWW.tar.gz`

---

#### `make superset-backup-pre-upgrade`
Create a backup before upgrading Superset.

```bash
make superset-backup-pre-upgrade
```

**Output:** `backups/superset/pre_upgrade_YYYYMMDD_HHMMSS.tar.gz`

---

### Restore Commands

#### `make superset-restore BACKUP=<name>`
Restore Superset from a specific backup.

```bash
# List available backups first
make superset-restore

# Restore from specific backup
make superset-restore BACKUP=backup_20241110_143022
make superset-restore BACKUP=before_upgrade
```

**⚠️ WARNING:** This will replace all current Superset data!

---

### Backup Management Commands

#### `make superset-list-backups`
List all available Superset backups with details.

```bash
make superset-list-backups
```

Shows:
- Backup filename
- File size
- Creation date
- Total backup directory size

---

#### `make superset-backup-info BACKUP=<name>`
Show detailed information about a specific backup.

```bash
make superset-backup-info BACKUP=backup_20241110_143022
```

Shows:
- File path and size
- Creation date
- Backup contents (first 20 files)
- Restore command

---

#### `make superset-cleanup-backups`
Remove old backups (keeps last 7).

```bash
make superset-cleanup-backups
```

Automatically removes backups older than the 7 most recent ones.

---

## Complete Backup Examples

### Daily Backup Workflow

```bash
# Create daily backup
make superset-backup-daily

# List all backups
make superset-list-backups

# View backup details
make superset-backup-info BACKUP=daily_20241110
```

### Before Making Changes

```bash
# Create backup before changes
make superset-backup-named NAME=before_dashboard_update

# Make your changes in Superset...

# If something goes wrong, restore
make superset-restore BACKUP=before_dashboard_update
```

### Weekly Maintenance

```bash
# Create weekly backup
make superset-backup-weekly

# Clean up old backups
make superset-cleanup-backups

# Verify remaining backups
make superset-list-backups
```

### Before Upgrade

```bash
# Create pre-upgrade backup
make superset-backup-pre-upgrade

# Upgrade Superset
make superset-upgrade

# If upgrade fails, restore
make superset-restore BACKUP=pre_upgrade_20241110_143022
```

## Other Useful Commands

### Docker Operations

```bash
# Start all containers
make docker-up

# Stop all containers
make docker-down

# Restart containers
make docker-restart

# View logs
make docker-logs
make docker-logs-superset
make docker-logs-db

# Show container status
make docker-ps
```

### Superset Management

```bash
# Initialize Superset (first time)
make superset-init

# Upgrade Superset database
make superset-upgrade

# Open Superset shell
make superset-shell
```

### Database Operations

```bash
# Run migrations
make migrate

# Create migrations
make makemigrations

# Show migration status
make showmigrations

# Open database shell
make dbshell
```

### Development

```bash
# Start development server
make dev

# Open Django shell
make shell

# Run tests
make test

# Run tests with coverage
make test-coverage

# Check code quality
make lint
make format
make check
```

### Complete Backup (Django + Superset)

```bash
# Backup everything
make backup-all

# Backup Django database only
make backup-db

# Restore Django database
make restore-db FILE=backups/django_db_20241110.sql
```

## Automation Examples

### Cron Jobs

Add to crontab (`crontab -e`):

```bash
# Daily Superset backup at 2 AM
0 2 * * * cd /path/to/onestep && make superset-backup-daily >> /var/log/superset_backup.log 2>&1

# Weekly backup on Sundays at 3 AM
0 3 * * 0 cd /path/to/onestep && make superset-backup-weekly >> /var/log/superset_backup.log 2>&1

# Monthly cleanup on 1st day at 4 AM
0 4 1 * * cd /path/to/onestep && make superset-cleanup-backups >> /var/log/superset_cleanup.log 2>&1
```

### Pre-Deployment Script

```bash
#!/bin/bash
# deploy.sh

echo "Creating pre-deployment backup..."
make superset-backup-named NAME=pre_deploy_$(date +%Y%m%d_%H%M%S)

if [ $? -eq 0 ]; then
    echo "Backup successful, proceeding with deployment..."
    # Your deployment commands here
else
    echo "Backup failed, aborting deployment!"
    exit 1
fi
```

## Troubleshooting

### Scripts Not Executable

```bash
# Make scripts executable
chmod +x scripts/backup_superset.sh scripts/restore_superset.sh

# Or let Makefile handle it (automatic)
make superset-backup
```

### Containers Not Running

```bash
# Check container status
make docker-ps

# Start containers if needed
make docker-up

# Check logs for errors
make docker-logs-superset
make docker-logs-db
```

### Backup Directory Not Found

```bash
# Create backup directory
mkdir -p backups/superset

# Run backup
make superset-backup
```

### Restore Fails

```bash
# Check available backups
make superset-list-backups

# Verify backup integrity
make superset-backup-info BACKUP=backup_name

# Check container logs
make docker-logs-superset
make docker-logs-db
```

### Disk Space Issues

```bash
# Check backup sizes
make superset-list-backups

# Clean up old backups
make superset-cleanup-backups

# Check disk usage
df -h
du -sh backups/
```

## Best Practices

### 1. Regular Backups

```bash
# Before any major changes
make superset-backup-named NAME=before_changes

# Daily automated backups
make superset-backup-daily

# Weekly full backups
make superset-backup-weekly
```

### 2. Test Restores

```bash
# Periodically test restore process
make superset-backup-named NAME=test_backup
make superset-restore BACKUP=test_backup
```

### 3. Monitor Backup Size

```bash
# Check backup sizes regularly
make superset-list-backups

# Clean up when needed
make superset-cleanup-backups
```

### 4. Document Backups

```bash
# Use descriptive names
make superset-backup-named NAME=before_dashboard_redesign
make superset-backup-named NAME=production_stable_v1.0

# Check backup info
make superset-backup-info BACKUP=production_stable_v1.0
```

## Quick Reference Card

| Command | Description |
|---------|-------------|
| `make superset-backup` | Create timestamped backup |
| `make superset-backup-named NAME=x` | Create named backup |
| `make superset-backup-daily` | Create daily backup |
| `make superset-backup-weekly` | Create weekly backup |
| `make superset-backup-pre-upgrade` | Create pre-upgrade backup |
| `make superset-restore BACKUP=x` | Restore from backup |
| `make superset-list-backups` | List all backups |
| `make superset-backup-info BACKUP=x` | Show backup details |
| `make superset-cleanup-backups` | Remove old backups |
| `make backup-all` | Backup Django + Superset |

## Related Documentation

- [Superset Backup & Restore Guide](SUPERSET_BACKUP_RESTORE.md) - Detailed backup/restore procedures
- [Superset Setup Guide](SUPERSET_SETUP.md) - Initial Superset configuration
- [Superset Architecture](SUPERSET_ARCHITECTURE.md) - System architecture overview
- [Scripts README](../scripts/README.md) - Direct script usage

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs: `make docker-logs-superset`
3. Consult the detailed documentation in `docs/`
4. Check script output for error messages
