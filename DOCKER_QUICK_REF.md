# Docker Quick Reference

One-page cheat sheet for common Docker commands.

## 🚀 Getting Started

```bash
# Start everything
docker compose up

# Start in background
docker compose up -d

# View API docs
open http://localhost:8000/docs
```

## 📋 Essential Commands

```bash
# Start services
docker compose up              # Foreground (see logs)
docker compose up -d           # Background (detached)

# Stop services
docker compose down            # Stop and remove containers
docker compose stop            # Stop but keep containers

# View logs
docker compose logs -f         # All services (live)
docker compose logs -f api     # Just API
docker compose logs -f db      # Just database

# Check status
docker compose ps              # List containers

# Restart
docker compose restart         # Restart all
docker compose restart api     # Restart just API

# Rebuild
docker compose build           # Rebuild images
docker compose up --build      # Rebuild and start
```

## 🗄️ Database

```bash
# Access database shell
docker compose exec db psql -U cms_user -d cms_db

# Backup database
docker compose exec db pg_dump -U cms_user cms_db > backup.sql

# Restore database
docker compose exec -T db psql -U cms_user -d cms_db < backup.sql

# View database logs
docker compose logs -f db
```

## 🔍 Debugging

```bash
# Open shell in API container
docker compose exec api /bin/bash

# Run command in container
docker compose exec api python --version
docker compose exec api pip list

# View container details
docker compose ps
docker inspect cms_api

# Check resource usage
docker stats
```

## 🛠️ Development

```bash
# Start with hot reload (default)
docker compose up

# Rebuild after dependency changes
docker compose build
docker compose up

# Run tests in container
docker compose exec api pytest

# Run migrations
docker compose exec api alembic upgrade head

# Create migration
docker compose exec api alembic revision --autogenerate -m "description"
```

## 🚢 Production

```bash
# Use production config
docker compose -f docker-compose.prod.yml up -d

# View production logs
docker compose -f docker-compose.prod.yml logs -f

# Stop production
docker compose -f docker-compose.prod.yml down
```

## 🧹 Cleanup

```bash
# Stop and remove containers
docker compose down

# Remove containers and volumes (deletes data!)
docker compose down -v

# Remove all unused Docker resources
docker system prune -a

# Remove specific volume
docker volume rm server_postgres_data
```

## 📊 Monitoring

```bash
# Resource usage
docker stats

# Container processes
docker top cms_api

# Last 100 log lines
docker compose logs --tail=100 api

# Logs from last 30 minutes
docker compose logs --since 30m api
```

## 🔐 Environment

```bash
# View environment variables
docker compose exec api env

# Override environment variable
docker compose run -e DEBUG=False api python -c "from app.config import settings; print(settings.DEBUG)"

# Use custom .env file
docker compose --env-file .env.prod up -d
```

## 🔄 Updates

```bash
# Pull latest images
docker compose pull

# Rebuild with latest code
git pull
docker compose build
docker compose up -d

# Update single service
docker compose up -d --no-deps --build api
```

## 🎯 Helper Script (Optional)

For convenience, use the helper script:

```bash
./docker-run.sh up       # Start services
./docker-run.sh stop     # Stop services
./docker-run.sh logs     # View logs
./docker-run.sh shell    # API shell
./docker-run.sh db       # Database shell
./docker-run.sh migrate  # Run migrations
./docker-run.sh build    # Rebuild
./docker-run.sh clean    # Remove all
```

## 🆘 Troubleshooting

| Problem                    | Solution                                                |
| -------------------------- | ------------------------------------------------------- |
| Port 8000 in use           | Change port in docker-compose.yml or stop other service |
| Database won't start       | `docker compose logs db`                                |
| API can't connect to DB    | Wait for DB health check, check DATABASE_URL            |
| Changes not reflecting     | `docker compose build && docker compose up`             |
| Out of disk space          | `docker system prune -a`                                |
| Container keeps restarting | `docker compose logs api`                               |

## 💡 Quick Tips

```bash
# View all running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Remove stopped containers
docker container prune

# View images
docker images

# Remove unused images
docker image prune -a

# View volumes
docker volume ls

# View networks
docker network ls
```

## 📚 More Info

- Full guide: [DOCKER.md](DOCKER.md)
- Docker docs: https://docs.docker.com/
- Docker Compose docs: https://docs.docker.com/compose/
