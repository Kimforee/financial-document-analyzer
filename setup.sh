#!/bin/bash

# Financial Document Analyzer - Quick Setup Script
# This script sets up the entire project for you

set -e  # Exit on any error

echo "🚀 Financial Document Analyzer - Quick Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python is installed
print_info "Checking Python installation..."

# Try different Python commands
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
else
    print_error "Python is not installed or not in PATH. Please install Python 3.8 or higher."
    print_info "Windows users: Make sure to add Python to PATH during installation"
    print_info "Or try running: py --version"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Python $PYTHON_VERSION found using '$PYTHON_CMD'"

# Check if pip is installed
PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    print_error "pip is not installed. Please install pip."
    print_info "Windows users: pip should come with Python installation"
    exit 1
fi
print_status "pip found using '$PIP_CMD'"

# Create virtual environment
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Install dependencies
print_info "Installing Python dependencies..."

# Detect OS and use appropriate requirements file
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    print_info "Windows detected, using Windows-compatible requirements..."
    $PIP_CMD install -r requirements-windows.txt
else
    print_info "Using standard requirements..."
    $PIP_CMD install -r requirements.txt
fi
print_status "Dependencies installed"

# Check if Redis is running
print_info "Checking Redis status..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_status "Redis is running"
    else
        print_warning "Redis is not running. Starting Redis..."
        if command -v redis-server &> /dev/null; then
            redis-server --daemonize yes
            sleep 2
            if redis-cli ping &> /dev/null; then
                print_status "Redis started successfully"
            else
                print_error "Failed to start Redis. Please start it manually: redis-server"
                exit 1
            fi
        else
            print_error "Redis is not installed. Please install Redis:"
            print_info "Ubuntu/Debian: sudo apt install redis-server"
            print_info "macOS: brew install redis"
            exit 1
        fi
    fi
else
    print_error "Redis is not installed. Please install Redis:"
    print_info "Ubuntu/Debian: sudo apt install redis-server"
    print_info "macOS: brew install redis"
    exit 1
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p data output logs
print_status "Directories created"

# Create .env file with SQLite configuration
print_info "Setting up database configuration..."
cat > .env << 'EOF'
# Financial Document Analyzer - Environment Configuration
DATABASE_URL=sqlite:///./financial_analyzer.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
DEBUG=True
SECRET_KEY=your_secret_key_here
OUTPUT_DIR=output
DATA_DIR=data
EOF
print_status "Environment file created"

# Initialize database
print_info "Initializing database..."
$PYTHON_CMD setup/init_db.py
print_status "Database initialized"

# Make scripts executable
print_info "Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true
chmod +x setup/*.py 2>/dev/null || true
chmod +x tests/*.py 2>/dev/null || true
print_status "Scripts made executable"

# Test the setup
print_info "Testing setup..."
$PYTHON_CMD -c "
from models import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✅ Database connection test passed')
except Exception as e:
    print(f'❌ Database connection test failed: {e}')
    exit(1)
"

print_status "Setup completed successfully!"

echo ""
echo "🎉 Setup Complete! Next steps:"
echo "================================"
echo ""
echo "1. Start all services:"
echo "   bash scripts/start_services.sh"
echo ""
echo "2. Or start individually:"
echo "   # Terminal 1: Start Celery worker"
echo "   celery -A celery_app worker --loglevel=info"
echo ""
echo "   # Terminal 2: Start FastAPI server"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/health/simple"
echo ""
echo "4. Submit an analysis:"
echo "   curl -X POST http://localhost:8000/analyze-default -d 'query=Test analysis'"
echo ""
echo "📚 Documentation:"
echo "   - Setup Guide: docs/SETUP_GUIDE.md"
echo "   - Quick Start: docs/QUICK_START.md"
echo "   - Troubleshooting: docs/TROUBLESHOOTING.md"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Process pending tasks: python scripts/process_pending.py"
echo "   - Run tests: python tests/test_api.py"
echo ""
print_status "Happy analyzing! 🚀"