#!/bin/bash

# Docker Quick Start Script for Church Management System

echo "🐳 Starting Church Management System with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to use docker compose or docker-compose
docker_compose_cmd() {
    if docker compose version &> /dev/null; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

# Parse command line arguments
COMMAND=${1:-up}

case $COMMAND in
    up|start)
        echo "🚀 Starting services..."
        docker_compose_cmd up -d
        echo ""
        echo "✅ Services started successfully!"
        echo ""
        echo "📖 API Documentation: http://localhost:8000/docs"
        echo "🗄️  Database: PostgreSQL on localhost:5432"
        echo ""
        echo "To view logs: ./docker-run.sh logs"
        echo "To stop: ./docker-run.sh stop"
        ;;
    
    down|stop)
        echo "🛑 Stopping services..."
        docker_compose_cmd down
        echo "✅ Services stopped!"
        ;;
    
    restart)
        echo "🔄 Restarting services..."
        docker_compose_cmd restart
        echo "✅ Services restarted!"
        ;;
    
    logs)
        echo "📋 Showing logs (Ctrl+C to exit)..."
        docker_compose_cmd logs -f
        ;;
    
    build)
        echo "🔨 Building images..."
        docker_compose_cmd build --no-cache
        echo "✅ Build complete!"
        ;;
    
    clean)
        echo "🧹 Cleaning up..."
        docker_compose_cmd down -v
        echo "✅ Cleanup complete! (volumes removed)"
        ;;
    
    shell)
        echo "🐚 Opening shell in API container..."
        docker exec -it cms_api /bin/bash
        ;;
    
    db)
        echo "🗄️  Opening PostgreSQL shell..."
        docker exec -it cms_postgres psql -U cms_user -d cms_db
        ;;
    
    migrate)
        echo "🗄️  Running database migrations..."
        docker exec cms_api alembic upgrade head
        echo "✅ Migrations complete!"
        ;;
    
    status)
        echo "📊 Service status:"
        docker_compose_cmd ps
        ;;
    
    *)
        echo "Church Management System - Docker Commands"
        echo ""
        echo "Usage: ./docker-run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  up, start    - Start all services"
        echo "  down, stop   - Stop all services"
        echo "  restart      - Restart all services"
        echo "  logs         - View logs"
        echo "  build        - Rebuild images"
        echo "  clean        - Stop and remove volumes"
        echo "  shell        - Open shell in API container"
        echo "  db           - Open PostgreSQL shell"
        echo "  migrate      - Run database migrations"
        echo "  status       - Show service status"
        echo ""
        echo "Examples:"
        echo "  ./docker-run.sh up       # Start services"
        echo "  ./docker-run.sh logs     # View logs"
        echo "  ./docker-run.sh stop     # Stop services"
        ;;
esac
