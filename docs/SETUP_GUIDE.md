# Financial Document Analyzer - Setup Guide

## 📋 Prerequisites

- Python 3.8 or higher
- Redis server
- Git (for cloning the repository)

## 🚀 Quick Setup (Recommended)

### 1. Clone and Navigate
```bash
git clone https://github.com/Kimforee/financial-document-analyzer.git
cd financial-document-analyzer-debug
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Quick Database Fix
```bash
python fix_database.py
```

### 5. Start All Services
```bash
bash scripts/start_services.sh
```

## 🔧 Manual Setup (Step by Step)

### Step 1: Environment Setup

#### Option A: Use SQLite (Easiest)
```bash
# Create .env file
cat > .env << EOF
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
```

#### Option B: Use Supabase (Production)
```bash
# Create .env file with Supabase
cat > .env << EOF
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.rfasmwqcncaxplrvgpzu.supabase.co:5432/postgres
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
```

### Step 2: Install Redis

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### Windows:
Download from: https://github.com/microsoftarchive/redis/releases

### Step 3: Initialize Database
```bash
python setup/init_db.py
```

### Step 4: Start Services

#### Option A: Start All at Once
```bash
bash scripts/start_services.sh
```

#### Option B: Start Individually
```bash
# Terminal 1: Start Redis (if not already running)
redis-server

# Terminal 2: Start Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 3: Start FastAPI Server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔑 API Keys Setup

### 1. Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add it to your `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_gemini_key_here
   ```

### 2. Get Serper API Key (Optional)
1. Go to [Serper.dev](https://serper.dev/)
2. Sign up and get your API key
3. Add it to your `.env` file:
   ```env
   SERPER_API_KEY=your_actual_serper_key_here
   ```

## 🧪 Test Your Setup

### 1. Health Check
```bash
curl http://localhost:8000/health/simple
```

Expected response:
```json
{"status": "healthy", "message": "Financial Document Analyzer is running"}
```

### 2. Submit Test Analysis
```bash
curl -X POST http://localhost:8000/analyze-default \
  -d "query=Test analysis" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

### 3. Check Analysis Status
```bash
# Get analysis ID from previous response, then:
curl http://localhost:8000/status/{analysis_id}
```

## 📁 Project Structure

```
financial-document-analyzer-debug/
├── main.py                 # FastAPI application
├── models.py              # Database models
├── celery_app.py          # Celery configuration
├── worker_tasks.py        # Background tasks
├── crew_runner.py         # CrewAI execution
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── fix_database.py        # Database fix script
├── scripts/
│   ├── start_services.sh  # Start all services
│   └── process_pending.py # Process pending tasks
├── setup/
│   ├── init_db.py         # Database initialization
│   ├── setup_secure.py    # Secure setup
│   └── env_template.txt   # Environment template
├── tests/
│   └── test_api.py        # API tests
├── docs/
│   ├── SETUP_GUIDE.md     # This file
│   └── QUICK_START.md     # Quick start guide
├── data/                  # Input files
├── output/                # Analysis results
└── logs/                  # Application logs
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Fix: Use SQLite instead
python fix_database.py
```

#### 2. Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it:
redis-server
```

#### 3. Celery Worker Not Processing Tasks
```bash
# Check if worker is running
ps aux | grep celery

# Start worker manually
celery -A celery_app worker --loglevel=info
```

#### 4. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 5. Permission Denied on Scripts
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Debug Mode

#### Enable Debug Logging
```bash
# Set in .env file
DEBUG=True

# Or set environment variable
export DEBUG=True
```

#### Check Logs
```bash
# Check application logs
tail -f logs/app.log

# Check Celery logs
celery -A celery_app worker --loglevel=debug
```

## 🔄 Development Workflow

### 1. Make Changes
Edit your code files

### 2. Test Changes
```bash
# Run tests
python tests/test_api.py

# Test specific endpoint
curl http://localhost:8000/health
```

### 3. Restart Services (if needed)
```bash
# Stop all services (Ctrl+C)
# Then restart
bash scripts/start_services.sh
```

## 📊 Monitoring

### Check Service Status
```bash
# Redis
redis-cli ping

# Database
python -c "from models import engine; print('DB OK' if engine.connect() else 'DB Error')"

# Celery
celery -A celery_app inspect active
```

### View Analysis Results
```bash
# List all analyses
curl http://localhost:8000/analyses

# Check specific analysis
curl http://localhost:8000/status/{analysis_id}
```

## 🚀 Production Deployment

### 1. Use Production Database
- Set up PostgreSQL or Supabase
- Update `DATABASE_URL` in `.env`

### 2. Use Production Redis
- Set up Redis server
- Update `REDIS_URL` in `.env`

### 3. Set Production Environment Variables
```env
DEBUG=False
SECRET_KEY=your_secure_secret_key
```

### 4. Use Process Manager
```bash
# Install PM2 (Node.js process manager)
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'financial-analyzer-api',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: '/path/to/your/project',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'financial-analyzer-worker',
      script: 'celery',
      args: '-A celery_app worker --loglevel=info',
      cwd: '/path/to/your/project',
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python fix_database.py` for database issues
3. Check logs in the `logs/` directory
4. Verify all services are running with the monitoring commands

## 🎉 Success!

Once everything is running, you should see:
- ✅ FastAPI server on http://localhost:8000
- ✅ Celery worker processing tasks
- ✅ Database storing analysis results
- ✅ Redis handling task queue

You can now use the API endpoints to analyze financial documents!
