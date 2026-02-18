# Docker Setup Guide

Complete guide for running the Church Management System with Docker.

## 🐳 Quick Start

### Prerequisites

- Docker Desktop (includes Docker and Docker Compose)
- Download from: https://docs.docker.com/get-docker/

### Start Everything

```bash
docker compose up
```

That's it! The API will be available at:

- **API Docs:** http://localhost:8000/docs
- **API:** http://localhost:8000
- **Database:** PostgreSQL on localhost:5432

### Run in Background

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

## 📋 What Gets Started

When you run `docker compose up`, Docker Compose starts:

1. **PostgreSQL Database** (postgres:15-alpine)
   - Container: `cms_postgres`
   - Port: 5432
   - Database: `cms_db`
   - User: `cms_user`
   - Password: `cms_password`

2. **FastAPI Application** (Python 3.11)
   - Container: `cms_api`
   - Port: 8000
   - Auto-runs migrations
   - Hot reload enabled (development)

## 🎯 Common Commands

### Basic Operations

```bash
# Start services (foreground - see logs)
docker compose up

# Start services (background)
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs (live)
docker compose logs -f

# View logs for specific service
docker compose logs -f api

# Check status
docker compose ps

# Rebuild images
docker compose build

# Rebuild and start
docker compose up --build
```

### Helper Script (Optional)

For convenience, you can also use the helper script:

```bash
./docker-run.sh up       # Start services
./docker-run.sh logs     # View logs
./docker-run.sh stop     # Stop services
./docker-run.sh shell    # Open API container shell
./docker-run.sh db       # Open database shell
./docker-run.sh migrate  # Run migrations
./docker-run.sh build    # Rebuild images
./docker-run.sh clean    # Remove everything
```

## 🗄️ Database Access

### From Host Machine

```bash
# Using psql
psql -h localhost -U cms_user -d cms_db
# Password: cms_password

# Or using Docker exec
docker compose exec db psql -U cms_user -d cms_db
```

### From API Container

```bash
# Open shell in API container
docker compose exec api /bin/bash

# Then use psql
psql -h db -U cms_user -d cms_db
```

### Connection String

```
postgresql://cms_user:cms_password@localhost:5432/cms_db
```

## 🔧 Configuration

### Development (Default)

Uses `docker-compose.yml`:

- Hot reload enabled
- Debug mode on
- Code mounted as volume (changes reflect immediately)
- PostgreSQL data persisted in Docker volume

### Production

Uses `docker-compose.prod.yml`:

- Multiple workers (4)
- Debug mode off
- No code mounting
- Environment variables from `.env` file

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Environment Variables

### Development (.env)

```env
DATABASE_URL=postgresql://cms_user:cms_password@db:5432/cms_db
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### Production (.env.docker)

Copy and customize:

```bash
cp .env.docker .env
# Edit .env with your production values
```

Required changes for production:

- Change `POSTGRES_PASSWORD`
- Set `DEBUG=False`
- Update `CORS_ORIGINS` with your domain
- Use strong passwords

## 🚀 Deployment Scenarios

### Local Development

```bash
# Start with hot reload
docker compose up

# Make code changes - they reflect immediately
# Database data persists between restarts
```

### Production Deployment

```bash
# 1. Copy and configure environment
cp .env.docker .env
nano .env  # Update passwords and settings

# 2. Start with production config
docker-compose -f docker-compose.prod.yml up -d

# 3. Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### CI/CD Pipeline

```bash
# Build
docker build -t cms-api:latest .

# Run migrations
docker run --rm cms-api:latest alembic upgrade head

# Start
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  cms-api:latest
```

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Database Connection Failed

```bash
# Check if database is healthy
docker-compose ps

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Container Won't Start

```bash
# View logs
docker-compose logs api

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Reset Everything

```bash
# Stop and remove everything including data
./docker-run.sh clean

# Or manually
docker-compose down -v
docker system prune -a
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Just API
docker-compose logs -f api

# Just database
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 api
```

### Container Stats

```bash
# Resource usage
docker stats

# Specific container
docker stats cms_api
```

### Health Checks

```bash
# Check health status
docker-compose ps

# API health endpoint
curl http://localhost:8000/health

# Database health
docker exec cms_postgres pg_isready -U cms_user
```

## 🗃️ Data Management

### Backup Database

```bash
# Backup to file
docker exec cms_postgres pg_dump -U cms_user cms_db > backup.sql

# Or using helper script
docker exec cms_postgres pg_dump -U cms_user cms_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# From SQL file
docker exec -i cms_postgres psql -U cms_user -d cms_db < backup.sql

# From compressed file
gunzip -c backup.sql.gz | docker exec -i cms_postgres psql -U cms_user -d cms_db
```

### Access Database Files

```bash
# Database volume location
docker volume inspect server_postgres_data

# Copy data out
docker cp cms_postgres:/var/lib/postgresql/data ./db_backup
```

## 🔐 Security Best Practices

### For Production

1. **Change Default Passwords**

   ```bash
   # Generate strong password
   openssl rand -base64 32
   ```

2. **Use Environment Variables**

   ```bash
   # Don't commit .env to git
   echo ".env" >> .gitignore
   ```

3. **Limit Network Exposure**

   ```yaml
   # In docker-compose.prod.yml
   db:
     ports: [] # Don't expose database port
   ```

4. **Use Secrets Management**

   ```bash
   # Docker secrets (Swarm mode)
   docker secret create db_password password.txt
   ```

5. **Regular Updates**
   ```bash
   # Update base images
   docker-compose pull
   docker-compose up -d
   ```

## 🎓 Advanced Usage

### Custom Network

```yaml
networks:
  cms_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Multiple Environments

```bash
# Development
docker-compose up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling

```bash
# Run multiple API instances
docker-compose up -d --scale api=3

# With load balancer (nginx)
# Add nginx service to docker-compose.yml
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect server_postgres_data

# Remove unused volumes
docker volume prune
```

## 📦 Building Custom Images

### Build Arguments

```dockerfile
# In Dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim
```

```bash
# Build with custom Python version
docker build --build-arg PYTHON_VERSION=3.12 -t cms-api:py312 .
```

### Multi-stage Builds

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
```

## 🚢 Docker Hub / Registry

### Push to Registry

```bash
# Tag image
docker tag cms-api:latest yourusername/cms-api:latest

# Push to Docker Hub
docker push yourusername/cms-api:latest

# Pull on another machine
docker pull yourusername/cms-api:latest
```

## 💡 Tips & Tricks

1. **Fast Rebuilds**: Use `.dockerignore` to exclude unnecessary files
2. **Layer Caching**: Put frequently changing code last in Dockerfile
3. **Small Images**: Use alpine variants when possible
4. **Health Checks**: Always define health checks for services
5. **Logs**: Use `docker-compose logs -f` to debug issues
6. **Clean Up**: Regularly run `docker system prune` to free space

## 🎉 Summary

Docker makes it incredibly easy to run the CMS:

```bash
# Development
./docker-run.sh up        # Start everything
./docker-run.sh logs      # Watch logs
./docker-run.sh stop      # Stop when done

# Production
cp .env.docker .env       # Configure
docker-compose -f docker-compose.prod.yml up -d
```

No Python installation needed, no database setup required - just Docker!
