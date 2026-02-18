#!/bin/bash

# Quick start script for Church Management System

echo "🚀 Starting Church Management System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start the server
echo "✅ Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
uvicorn app.main:app --reload
