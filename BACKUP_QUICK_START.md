# Superset Backup & Restore - Quick Start

Quick reference for backing up and restoring Apache Superset.

## 🚀 Quick Commands

### Create Backup

```bash
# Simple backup (automatic timestamp)
make superset-backup

# Named backup
make superset-backup-named NAME=my_backup

# Daily backup
make superset-backup-daily
```

### Restore Backup

```bash
# List available backups
make superset-list-backups

# Restore specific backup
make superset-restore BACKUP=backup_20241110_143022
```

### Manage Backups

```bash
# View backup details
make superset-backup-info BACKUP=backup_name

# Clean up old backups (keeps last 7)
make superset-cleanup-backups
```

## 📋 Common Workflows

### Before Making Changes

```bash
# 1. Create backup
make superset-backup-named NAME=before_changes

# 2. Make your changes in Superset...

# 3. If something goes wrong:
make superset-restore BACKUP=before_changes
```

### Before Upgrade

```bash
# 1. Create pre-upgrade backup
make superset-backup-pre-upgrade

# 2. Upgrade Superset
make superset-upgrade

# 3. If upgrade fails:
make superset-list-backups
make superset-restore BACKUP=pre_upgrade_20241110_143022
```

### Daily Maintenance

```bash
# Create daily backup
make superset-backup-daily

# Clean up old backups
make superset-cleanup-backups
```

## ⚠️ Important Notes

- **Restoring deletes current data** - Always backup before restore
- **Backups are stored in** `backups/superset/`
- **Automatic cleanup** keeps last 7 backups
- **Containers must be running** - Use `make docker-up` if needed

## 🔧 Troubleshooting

### Containers not running?
```bash
make docker-up
```

### Check backup status?
```bash
make superset-list-backups
```

### View logs?
```bash
make docker-logs-superset
```

## 📚 Full Documentation

- [Makefile Reference](docs/MAKEFILE_REFERENCE.md) - All Makefile commands
- [Backup & Restore Guide](docs/SUPERSET_BACKUP_RESTORE.md) - Detailed procedures
- [Scripts README](scripts/README.md) - Direct script usage

## 🆘 Need Help?

```bash
# Show all available commands
make help

# Check system status
make info
```
