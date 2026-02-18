# Docker Troubleshooting Guide

## Common Issues and Solutions

### Issue: "role cms_user does not exist"

**Symptoms:**

```
cms_postgres  | FATAL:  role "cms_user" does not exist
```

**Cause:** Old database volume from a previous run without proper initialization.

**Solution:**

```bash
# Stop all containers
docker compose down

# Remove the old volume (this will delete the database data)
docker compose down -v

# Start fresh
docker compose up
```

### Issue: "Name does not resolve" for postgres

**Symptoms:**

```
nc: getaddrinfo for host "postgres" port 5432: Name does not resolve
```

**Cause:** The API is trying to connect to wrong hostname.

**Solution:** The DATABASE_URL should use `db` as the hostname (the service name in docker-compose.yml):

```
DATABASE_URL: postgresql://cms_user:cms_password@db:5432/cms_db
```

### Issue: Version warning

**Symptoms:**

```
WARN[0000] the attribute `version` is obsolete
```

**Solution:** Remove the `version:` line from docker-compose.yml (it's optional in newer Docker Compose versions).

## Quick Reset

If things aren't working, do a complete reset:

```bash
# Stop everything and remove volumes
docker compose down -v

# Remove any orphaned containers
docker container prune

# Start fresh
docker compose up
```

## Check Database Connection

```bash
# Check if database is running
docker compose ps

# Check database logs
docker compose logs db

# Try connecting to database
docker compose exec db psql -U cms_user -d cms_db
```

## Check API Connection

```bash
# Check API logs
docker compose logs api

# Check if API can reach database
docker compose exec api ping db

# Check environment variables
docker compose exec api env | grep DATABASE
```
