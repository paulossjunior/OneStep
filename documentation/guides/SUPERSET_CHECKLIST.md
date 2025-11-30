# Superset Integration Checklist

Use this checklist to set up and verify your Superset installation.

## Pre-Installation

- [ ] Docker and Docker Compose installed
- [ ] At least 4GB RAM available
- [ ] Ports 8000, 8088, 5432, and 6379 are free
- [ ] Git repository cloned
- [ ] `.env.superset` file reviewed (optional customization)

## Installation

- [ ] Run `make superset-up`
- [ ] Wait 2-3 minutes for initialization
- [ ] Check logs: `make superset-logs`
- [ ] Verify "Superset initialization complete!" message appears
- [ ] All containers running: `docker ps`

## First Access

- [ ] Open browser to http://localhost:8088
- [ ] Login with default credentials (admin/admin)
- [ ] Change admin password (Settings → User → Edit Profile)
- [ ] Explore the interface

## Database Connection

- [ ] Go to Settings → Database Connections
- [ ] Click + Database
- [ ] Select PostgreSQL
- [ ] Enter connection string: `postgresql://postgres:postgres@db:5432/onestep_dev`
- [ ] Click Test Connection
- [ ] Verify success message
- [ ] Click Connect
- [ ] Enable "Expose database in SQL Lab"

## First Dataset

- [ ] Go to Data → Datasets
- [ ] Click + Dataset
- [ ] Select OneStep Database
- [ ] Select schema: public
- [ ] Choose a table (e.g., `organizational_group_organizationalunit`)
- [ ] Click Add
- [ ] Verify dataset appears in list

## First Chart

- [ ] Click on your dataset
- [ ] Choose visualization type (e.g., Table or Bar Chart)
- [ ] Configure metrics (e.g., COUNT(*))
- [ ] Configure dimensions (e.g., campus name)
- [ ] Click Update Chart
- [ ] Verify chart displays data
- [ ] Click Save
- [ ] Give it a name
- [ ] Save to a new dashboard

## First Dashboard

- [ ] Go to Dashboards
- [ ] Find your newly created dashboard
- [ ] Click Edit Dashboard
- [ ] Resize and position your chart
- [ ] Click Save
- [ ] Verify dashboard displays correctly

## SQL Lab Exploration

- [ ] Go to SQL → SQL Lab
- [ ] Select OneStep Database
- [ ] Select schema: public
- [ ] Write a simple query:
  ```sql
  SELECT COUNT(*) as total FROM organizational_group_organizationalunit;
  ```
- [ ] Click Run
- [ ] Verify results appear
- [ ] Try exploring other tables

## Performance Verification

- [ ] Run a query in SQL Lab
- [ ] Note execution time
- [ ] Run same query again
- [ ] Verify faster execution (cache hit)
- [ ] Check Redis is working: `docker exec superset_redis redis-cli ping`

## Security Configuration

- [ ] Admin password changed from default
- [ ] Review user roles (Settings → List Users)
- [ ] Consider creating read-only database user
- [ ] Review database connection permissions
- [ ] Check CORS settings if needed

## Documentation Review

- [ ] Read [SUPERSET_README.md](SUPERSET_README.md)
- [ ] Review [docs/SUPERSET_SETUP.md](docs/SUPERSET_SETUP.md)
- [ ] Bookmark [docs/SUPERSET_QUICK_REFERENCE.md](docs/SUPERSET_QUICK_REFERENCE.md)
- [ ] Review [docs/SUPERSET_ARCHITECTURE.md](docs/SUPERSET_ARCHITECTURE.md)

## Testing

- [ ] Create a test chart
- [ ] Add filters to chart
- [ ] Export chart as CSV
- [ ] Create a test dashboard
- [ ] Add dashboard filters
- [ ] Share dashboard link
- [ ] Test on mobile device

## Backup Setup

- [ ] Test database backup: `docker exec onestep_db pg_dump -U postgres superset > test_backup.sql`
- [ ] Verify backup file created
- [ ] Document backup location
- [ ] Set up automated backups (optional)

## Monitoring

- [ ] Check Django logs: `docker logs onestep_web`
- [ ] Check Superset logs: `make superset-logs`
- [ ] Check PostgreSQL logs: `docker logs onestep_db`
- [ ] Check Redis logs: `docker logs superset_redis`
- [ ] Verify health checks passing

## Common Commands Verified

- [ ] `make superset-up` - Starts services
- [ ] `make superset-down` - Stops services
- [ ] `make superset-logs` - Views logs
- [ ] `make superset-shell` - Opens shell
- [ ] `make superset-reset` - Resets password

## Troubleshooting Tested

- [ ] Restart Superset: `docker-compose -f docker-compose.superset.yml restart superset`
- [ ] Check container status: `docker ps`
- [ ] View all logs: `make superset-logs-all`
- [ ] Access database: `docker exec -it onestep_db psql -U postgres -d onestep_dev`

## Production Readiness (Optional)

- [ ] Change all default passwords
- [ ] Update SECRET_KEY in `.env.superset`
- [ ] Configure HTTPS (reverse proxy)
- [ ] Set up read-only database user
- [ ] Enable row-level security
- [ ] Configure email alerts
- [ ] Set up monitoring/alerting
- [ ] Document disaster recovery plan
- [ ] Test backup and restore procedures
- [ ] Configure automated backups
- [ ] Set up log aggregation
- [ ] Enable audit logging

## Advanced Features (Optional)

- [ ] Configure Celery for async queries
- [ ] Set up email reports
- [ ] Configure Slack notifications
- [ ] Create custom SQL metrics
- [ ] Set up materialized views
- [ ] Configure custom OAuth
- [ ] Enable JavaScript controls (if needed)
- [ ] Set up Mapbox for geospatial viz

## Team Onboarding

- [ ] Create user accounts for team members
- [ ] Assign appropriate roles
- [ ] Share documentation links
- [ ] Conduct training session
- [ ] Create example dashboards
- [ ] Document common queries
- [ ] Set up shared datasets

## Maintenance Schedule

- [ ] Weekly: Review logs for errors
- [ ] Weekly: Check disk space usage
- [ ] Monthly: Update Superset image
- [ ] Monthly: Review and optimize slow queries
- [ ] Quarterly: Review user access and permissions
- [ ] Quarterly: Test backup and restore

## Success Criteria

✅ All services running without errors
✅ Can access Superset UI
✅ Database connection successful
✅ Can create and view charts
✅ Can create and view dashboards
✅ SQL Lab queries execute successfully
✅ Caching is working (Redis)
✅ Documentation reviewed
✅ Team members can access

## Next Steps

Once all items are checked:

1. **Explore Your Data**
   - Browse all available tables
   - Understand data relationships
   - Identify key metrics

2. **Build Dashboards**
   - Executive overview
   - Campus analytics
   - Initiative tracking
   - People management

3. **Share Insights**
   - Share dashboards with team
   - Schedule automated reports
   - Set up alerts for key metrics

4. **Optimize Performance**
   - Add database indexes
   - Create materialized views
   - Configure caching strategies

5. **Continuous Improvement**
   - Gather user feedback
   - Iterate on dashboards
   - Add new visualizations
   - Optimize queries

## Support Resources

- **Documentation**: Check `docs/` folder
- **Logs**: `make superset-logs`
- **Community**: [Apache Superset Slack](https://apache-superset.slack.com/)
- **GitHub**: [Superset Issues](https://github.com/apache/superset/issues)

---

**Congratulations!** 🎉

If you've completed this checklist, your Superset integration is ready to use. Start exploring your data and building insightful dashboards!
