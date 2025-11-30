# Superset Quick Reference

## Common Commands

### Start/Stop Services

```bash
# Start all services
docker-compose -f docker-compose.superset.yml up -d

# Stop all services
docker-compose -f docker-compose.superset.yml down

# Restart Superset only
docker-compose -f docker-compose.superset.yml restart superset

# View logs
docker-compose -f docker-compose.superset.yml logs -f superset
```

### Access Points

- **Superset UI**: http://localhost:8088
- **Django Admin**: http://localhost:8000/admin
- **Django API**: http://localhost:8000/api
- **PostgreSQL**: localhost:5432

### Default Credentials

**Superset:**
- Username: `admin`
- Password: `admin`

**Database:**
- Host: `db` (from containers) or `localhost` (from host)
- Port: `5432`
- Database: `onestep_dev`
- Username: `postgres`
- Password: `postgres`

## Database Connection String

```
postgresql://postgres:postgres@db:5432/onestep_dev
```

## Useful SQL Queries

### Count All Records

```sql
SELECT 
    'Organizational Units' as entity, COUNT(*) as count 
FROM organizational_group_organizationalunit
UNION ALL
SELECT 'Initiatives', COUNT(*) FROM initiatives_initiative
UNION ALL
SELECT 'People', COUNT(*) FROM people_person
UNION ALL
SELECT 'Campuses', COUNT(*) FROM organizational_group_campus;
```

### Active Leaders

```sql
SELECT 
    p.name,
    ou.name as unit_name,
    oul.start_date
FROM organizational_group_organizationalunitleadership oul
JOIN people_person p ON oul.person_id = p.id
JOIN organizational_group_organizationalunit ou ON oul.unit_id = ou.id
WHERE oul.is_active = true
ORDER BY oul.start_date DESC;
```

### Initiative Summary

```sql
SELECT 
    it.name as type,
    COUNT(*) as total,
    COUNT(CASE WHEN i.end_date > CURRENT_DATE THEN 1 END) as active,
    COUNT(CASE WHEN i.end_date <= CURRENT_DATE THEN 1 END) as completed
FROM initiatives_initiative i
JOIN initiatives_initiativetype it ON i.type_id = it.id
GROUP BY it.name;
```

## Chart Type Recommendations

| Data Type | Recommended Chart |
|-----------|------------------|
| Counts by category | Bar Chart, Pie Chart |
| Trends over time | Line Chart, Area Chart |
| Comparisons | Bar Chart, Table |
| Distributions | Histogram, Box Plot |
| Relationships | Scatter Plot, Bubble Chart |
| Hierarchies | Treemap, Sunburst |
| Geographic | Map (requires coordinates) |
| KPIs | Big Number, Gauge |

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Save dashboard | `Ctrl/Cmd + S` |
| Run query | `Ctrl/Cmd + Enter` |
| Format SQL | `Ctrl/Cmd + Shift + F` |
| Toggle fullscreen | `F11` |

## Troubleshooting Checklist

- [ ] All containers running? `docker-compose ps`
- [ ] Database accessible? `docker exec -it onestep_db psql -U postgres -d onestep_dev -c '\dt'`
- [ ] Redis running? `docker exec superset_redis redis-cli ping`
- [ ] Superset logs clean? `docker logs superset --tail 50`
- [ ] Browser cache cleared?
- [ ] Correct database connection string?

## Performance Tips

1. **Use caching**: Set cache timeout on charts (3600 seconds = 1 hour)
2. **Limit rows**: Add `LIMIT` to queries or use pagination
3. **Create indexes**: Add indexes on frequently filtered columns
4. **Use views**: Create database views for complex queries
5. **Async queries**: Enable for long-running queries

## Common Errors

### "Database connection failed"
- Check database is running
- Verify connection string
- Use `db` as hostname (not `localhost`)

### "Query timeout"
- Increase timeout in database settings
- Optimize query with indexes
- Use async query execution

### "Permission denied"
- Check database user permissions
- Verify table access rights
- Review row-level security filters

## Export Options

- **CSV**: Download query results
- **JSON**: API export for programmatic access
- **Dashboard PDF**: Requires additional setup
- **Chart PNG**: Right-click chart → Download

## Best Practices

1. **Name conventions**: Use clear, descriptive names
2. **Documentation**: Add descriptions to datasets and charts
3. **Colors**: Use consistent color schemes
4. **Filters**: Add dashboard-level filters for interactivity
5. **Refresh**: Set appropriate cache timeouts
6. **Security**: Use row-level security for sensitive data
7. **Testing**: Test queries in SQL Lab before creating charts
