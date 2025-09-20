# Financial Document Analyzer - Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Database Connection Issues

#### Problem: `Database connection failed: Network is unreachable`
```bash
❌ Database connection failed: (psycopg2.OperationalError) connection to server at "db.rfasmwqcncaxplrvgpzu.supabase.co" (2406:da1a:6b0:f619:feab:1f41:71ed:1c79), port 5432 failed: Network is unreachable
```

**Solution:**
```bash
# Use the database fix script
python fix_database.py

# Or manually set SQLite in .env
echo "DATABASE_URL=sqlite:///./financial_analyzer.db" > .env
```

#### Problem: `sqlite3.OperationalError: no such table: analysis_results`
```bash
❌ sqlite3.OperationalError: no such table: analysis_results
```

**Solution:**
```bash
# Initialize the database
python setup/init_db.py
```

### 2. Redis Connection Issues

#### Problem: `Redis connection failed`
```bash
❌ Redis connection failed: Error 111 connecting to localhost:6379. Connection refused.
```

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not running, start Redis
redis-server

# On Ubuntu/Debian
sudo systemctl start redis-server

# On macOS
brew services start redis
```

#### Problem: `Redis is not installed`
```bash
❌ redis-server: command not found
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# macOS
brew install redis

# Windows
# Download from: https://github.com/microsoftarchive/redis/releases
```

### 3. Celery Worker Issues

#### Problem: Tasks stuck in "pending" status
```json
{
  "analysis_id": "abc123...",
  "status": "pending",
  "query": "Test analysis"
}
```

**Solution:**
```bash
# Check if Celery worker is running
ps aux | grep celery

# Start Celery worker
celery -A celery_app worker --loglevel=info

# Or use the start script
bash scripts/start_services.sh
```

#### Problem: `ModuleNotFoundError: No module named 'celery'`
```bash
❌ ModuleNotFoundError: No module named 'celery'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Port Already in Use

#### Problem: `Address already in use`
```bash
❌ OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 5. Permission Issues

#### Problem: `Permission denied`
```bash
❌ bash: ./scripts/start_services.sh: Permission denied
```

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py
chmod +x setup/*.py
chmod +x tests/*.py

# Or run with bash
bash scripts/start_services.sh
```

### 6. API Key Issues

#### Problem: `API key not found`
```bash
❌ GEMINI_API_KEY not found in environment variables
```

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Create .env file
python setup/setup_secure.py

# Or manually create
cat > .env << EOF
GEMINI_API_KEY=your_actual_key_here
SERPER_API_KEY=your_actual_key_here
DATABASE_URL=sqlite:///./financial_analyzer.db
REDIS_URL=redis://localhost:6379/0
EOF
```

### 7. File Upload Issues

#### Problem: `File not found`
```bash
❌ File not found: data/sample.pdf
```

**Solution:**
```bash
# Create data directory
mkdir -p data

# Add sample file
# Download a sample PDF or use your own file
```

## 🔍 Debugging Commands

### Check Service Status
```bash
# Check Redis
redis-cli ping

# Check Database
python -c "from models import engine; print('DB OK' if engine.connect() else 'DB Error')"

# Check Celery
celery -A celery_app inspect active

# Check API
curl http://localhost:8000/health/simple
```

### View Logs
```bash
# Application logs
tail -f logs/app.log

# Celery logs
celery -A celery_app worker --loglevel=debug

# Redis logs
redis-cli monitor
```

### Test Individual Components
```bash
# Test database
python -c "
from models import init_database, create_tables
init_database()
create_tables()
print('Database OK')
"

# Test Celery
python -c "
from celery_app import celery_app
print('Celery OK')
"

# Test API
python tests/test_api.py
```

## 🛠️ Advanced Troubleshooting

### Reset Everything
```bash
# Stop all services
pkill -f celery
pkill -f uvicorn
pkill -f redis-server

# Remove database
rm -f financial_analyzer.db

# Remove logs
rm -rf logs/*

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Restart everything
bash setup.sh
```

### Check System Resources
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check running processes
ps aux | grep -E "(celery|uvicorn|redis)"
```

### Network Issues
```bash
# Check if ports are open
netstat -tlnp | grep -E "(8000|6379)"

# Test connectivity
telnet localhost 8000
telnet localhost 6379
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this guide** - Your issue might be listed above
2. **Run debug commands** - Gather information about your system
3. **Check logs** - Look for error messages
4. **Try the reset** - Sometimes a clean start helps

### Information to Provide

When asking for help, include:

1. **Error message** - Copy the exact error
2. **System info** - OS, Python version, etc.
3. **Steps to reproduce** - What did you do before the error?
4. **Debug output** - Results of debug commands
5. **Log files** - Relevant log entries

### Debug Information Script
```bash
# Run this to gather debug info
cat > debug_info.sh << 'EOF'
#!/bin/bash
echo "=== System Information ==="
uname -a
python3 --version
pip list | grep -E "(celery|redis|sqlalchemy|fastapi)"

echo -e "\n=== Service Status ==="
redis-cli ping 2>/dev/null || echo "Redis: Not running"
ps aux | grep celery | grep -v grep || echo "Celery: Not running"
ps aux | grep uvicorn | grep -v grep || echo "FastAPI: Not running"

echo -e "\n=== Port Status ==="
netstat -tlnp | grep -E "(8000|6379)" || echo "No services on ports 8000/6379"

echo -e "\n=== Database Status ==="
python3 -c "from models import engine; print('DB: OK' if engine.connect() else 'DB: Error')" 2>/dev/null || echo "DB: Error"

echo -e "\n=== Environment ==="
ls -la .env 2>/dev/null || echo ".env file not found"
EOF

chmod +x debug_info.sh
./debug_info.sh
```

## 🎯 Quick Fixes

### Most Common Solutions

1. **Everything not working**: `bash setup.sh`
2. **Database issues**: `python fix_database.py`
3. **Redis issues**: `redis-server`
4. **Celery issues**: `celery -A celery_app worker --loglevel=info`
5. **Permission issues**: `chmod +x scripts/*.sh`
6. **Port issues**: `lsof -i :8000 && kill -9 <PID>`

### One-Line Fixes

```bash
# Complete reset and restart
pkill -f -E "(celery|uvicorn|redis)" && rm -f financial_analyzer.db && bash setup.sh

# Fix database and restart
python fix_database.py && bash scripts/start_services.sh

# Fix permissions and restart
chmod +x scripts/*.sh && bash scripts/start_services.sh
```

Remember: Most issues are solved by ensuring all services are running and the database is properly initialized! 🚀
