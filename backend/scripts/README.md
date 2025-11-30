# Scripts Directory

This directory contains utility scripts for managing the OneStep application and Superset.

## Available Scripts

### Superset Backup & Restore

#### `backup_superset.sh`
Creates a complete backup of your Superset instance.

**Usage:**
```bash
# Automatic timestamp backup
./scripts/backup_superset.sh

# Named backup
./scripts/backup_superset.sh my_backup_name
```

**What it backs up:**
- Superset metadata database (dashboards, charts, datasets)
- Superset home directory (uploads, thumbnails)
- Configuration files
- Exported assets (dashboards, datasources)

**Output:** `backups/superset/<backup_name>.tar.gz`

---

#### `restore_superset.sh`
Restores Superset from a backup.

**Usage:**
```bash
# List available backups
./scripts/restore_superset.sh

# Restore specific backup
./scripts/restore_superset.sh backup_20241110_143022
```

**⚠️ WARNING:** This will replace all current Superset data!

---

## Quick Commands

### Backup Operations

```bash
# Create backup before making changes
./scripts/backup_superset.sh before_changes

# Create daily backup
./scripts/backup_superset.sh daily_$(date +%Y%m%d)

# Create backup before upgrade
./scripts/backup_superset.sh pre_upgrade_v2.0
```

### Restore Operations

```bash
# See available backups
./scripts/restore_superset.sh

# Restore from specific backup
./scripts/restore_superset.sh backup_20241110_143022

# Restore from named backup
./scripts/restore_superset.sh before_changes
```

### Backup Management

```bash
# List all backups with sizes
ls -lh backups/superset/

# Check total backup size
du -sh backups/superset/

# Remove old backups manually (keep last 5)
cd backups/superset && ls -t *.tar.gz | tail -n +6 | xargs rm -f
```

## Scheduled Backups

### Using Cron

Add to crontab (`crontab -e`):

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/onestep && ./scripts/backup_superset.sh daily_backup

# Weekly backup on Sundays at 3 AM
0 3 * * 0 cd /path/to/onestep && ./scripts/backup_superset.sh weekly_backup

# Monthly backup on 1st day at 4 AM
0 4 1 * * cd /path/to/onestep && ./scripts/backup_superset.sh monthly_backup
```

## Prerequisites

- Docker and Docker Compose installed
- Containers running: `docker-compose -f docker-compose.superset.yml up -d`
- Sufficient disk space for backups

## Troubleshooting

### Scripts not executable
```bash
chmod +x scripts/*.sh
```

### Containers not running
```bash
docker-compose -f docker-compose.superset.yml up -d
```

### Check backup integrity
```bash
tar tzf backups/superset/backup_name.tar.gz
```

### View backup contents
```bash
tar xzf backups/superset/backup_name.tar.gz -C /tmp/
ls -la /tmp/backup_name/
```

## Documentation

For detailed information, see:
- [Superset Backup & Restore Guide](../docs/SUPERSET_BACKUP_RESTORE.md)
- [Superset Setup Guide](../docs/SUPERSET_SETUP.md)

## Support

If you encounter issues:
1. Check Docker logs: `docker logs superset` or `docker logs onestep_db`
2. Verify environment variables in `.env.superset`
3. Ensure sufficient disk space: `df -h`
4. Review the detailed documentation in `docs/`
