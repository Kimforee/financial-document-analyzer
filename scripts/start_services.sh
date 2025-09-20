#!/bin/bash

# Financial Document Analyzer - Service Startup Script
# This script starts all required services for the application

echo "🚀 Starting Financial Document Analyzer Services..."
echo "=================================================="

# Check if Redis is running
echo "🔍 Checking Redis status..."
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running. Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    if pgrep -x "redis-server" > /dev/null; then
        echo "✅ Redis started successfully"
    else
        echo "❌ Failed to start Redis. Please install and start Redis manually."
        exit 1
    fi
else
    echo "✅ Redis is already running"
fi

# Check if database is initialized
echo "🔍 Checking database initialization..."
python setup/init_db.py
if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --detach --pidfile=celery.pid

# Wait a moment for Celery to start
sleep 3

# Check if Celery worker is running
if pgrep -f "celery.*worker" > /dev/null; then
    echo "✅ Celery worker started successfully"
else
    echo "❌ Failed to start Celery worker"
    exit 1
fi

# Start FastAPI server
echo "🌐 Starting FastAPI server..."
echo "=================================================="
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health/simple"
echo "📋 Task List: http://localhost:8000/analyses"
echo "=================================================="
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Stop Celery worker
    if [ -f celery.pid ]; then
        celery -A celery_app control shutdown
        rm -f celery.pid
        echo "✅ Celery worker stopped"
    fi
    
    # Stop Redis if we started it
    if pgrep -x "redis-server" > /dev/null; then
        redis-cli shutdown
        echo "✅ Redis stopped"
    fi
    
    echo "👋 All services stopped. Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start FastAPI server using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
