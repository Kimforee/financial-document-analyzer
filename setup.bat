@echo off
REM Financial Document Analyzer - Windows Setup Script
REM This script sets up the entire project for Windows users

echo 🚀 Financial Document Analyzer - Windows Setup
echo =============================================

REM Check if Python is installed
echo ℹ️  Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo ✅ Python found

REM Check if pip is installed
echo ℹ️  Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed. Please install pip.
    pause
    exit /b 1
)

echo ✅ pip found

REM Create virtual environment
echo ℹ️  Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo ℹ️  Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Install dependencies
echo ℹ️  Installing Python dependencies...
echo ℹ️  Using Windows-compatible requirements...
pip install -r requirements-windows.txt
echo ✅ Dependencies installed

REM Check if Redis is available (optional for Windows)
echo ℹ️  Checking Redis status...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Redis is not running. For full functionality, install Redis:
    echo    - Download from: https://github.com/microsoftarchive/redis/releases
    echo    - Or use Docker: docker run -d -p 6379:6379 redis:alpine
    echo    - Or use WSL: wsl -d Ubuntu -e bash -c "sudo apt install redis-server"
    echo.
    echo For now, continuing without Redis (some features may not work)
) else (
    echo ✅ Redis is running
)

REM Create necessary directories
echo ℹ️  Creating necessary directories...
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "logs" mkdir logs
echo ✅ Directories created

REM Create .env file with SQLite configuration
echo ℹ️  Setting up database configuration...
(
echo # Financial Document Analyzer - Environment Configuration
echo DATABASE_URL=sqlite:///./financial_analyzer.db
echo REDIS_URL=redis://localhost:6379/0
echo CELERY_BROKER_URL=redis://localhost:6379/0
echo CELERY_RESULT_BACKEND=redis://localhost:6379/0
echo GEMINI_API_KEY=your_gemini_api_key_here
echo SERPER_API_KEY=your_serper_api_key_here
echo DEBUG=True
echo SECRET_KEY=your_secret_key_here
echo OUTPUT_DIR=output
echo DATA_DIR=data
) > .env
echo ✅ Environment file created

REM Initialize database
echo ℹ️  Initializing database...
python setup\init_db.py
echo ✅ Database initialized

REM Test the setup
echo ℹ️  Testing setup...
python -c "from models import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text('SELECT 1')); print('✅ Database connection test passed')"
if %errorlevel% neq 0 (
    echo ❌ Database connection test failed
    pause
    exit /b 1
)

echo ✅ Setup completed successfully!
echo.
echo 🎉 Setup Complete! Next steps:
echo ================================
echo.
echo 1. Start the FastAPI server:
echo    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo 2. In another terminal, start Celery worker (if Redis is running):
echo    celery -A celery_app worker --loglevel=info
echo.
echo 3. Test the API:
echo    curl http://localhost:8000/health/simple
echo.
echo 4. Submit an analysis:
echo    curl -X POST http://localhost:8000/analyze-default -d "query=Test analysis"
echo.
echo 📚 Documentation:
echo    - Setup Guide: docs\SETUP_GUIDE.md
echo    - Quick Start: docs\QUICK_START.md
echo    - Troubleshooting: docs\TROUBLESHOOTING.md
echo.
echo 🔧 Troubleshooting:
echo    - Process pending tasks: python scripts\process_pending.py
echo    - Run tests: python tests\test_api.py
echo.
echo ✅ Happy analyzing! 🚀
pause
