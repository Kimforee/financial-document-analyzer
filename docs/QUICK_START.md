# Financial Document Analyzer - Quick Start Guide

## 🚀 How to See Analysis IDs and Test Results

### 1. Start the Server
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```



### 2. Submit an Analysis
```bash
curl -X POST http://127.0.0.1:8000/analyze-default \
  -d "query=Analyze this financial document" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

**Response will include the `analysis_id`:**
```json
{
  "status": "queued",
  "analysis_id": "fd936254-4817-411c-b839-a4ffc2b9420a",
  "task_id": "48d37dc7-3ab9-4be6-ae1e-cf6632e6b6b5",
  "query": "Analyze this financial document",
  "file_processed": "sample.pdf",
  "file_source": "default"
}
```

### 3. See All Analysis IDs
```bash
curl http://127.0.0.1:8000/analyses
```

**This shows all analyses with their IDs:**
```json
{
  "analyses": [
    {
      "analysis_id": "fd936254-4817-411c-b839-a4ffc2b9420a",
      "status": "pending",
      "query": "Analyze this financial document",
      "file_name": "sample.pdf",
      "created_at": "2025-09-20T04:28:49.857658"
    }
  ],
  "total_count": 1
}
```

### 4. Check Status
```bash
curl http://127.0.0.1:8000/status/fd936254-4817-411c-b839-a4ffc2b9420a
```

### 5. Get Results (when completed)
```bash
curl http://127.0.0.1:8000/result/fd936254-4817-411c-b839-a4ffc2b9420a
```

## 🗄️ Supabase Configuration

### Update your .env file:
```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.rfasmwqcncaxplrvgpzu.supabase.co:5432/postgres
```

### Replace `YOUR_ACTUAL_PASSWORD` with your real Supabase password

## 📊 Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Basic API status |
| `/health/simple` | GET | Simple health check |
| `/health` | GET | Full health check |
| `/analyze` | POST | Upload file for analysis |
| `/analyze-default` | POST | Analyze sample file |
| `/analyses` | GET | **List all analyses with IDs** |
| `/status/{id}` | GET | Check analysis status |
| `/result/{id}` | GET | Get analysis results |
| `/tasks` | GET | List tasks (technical) |

## 🔍 Finding Analysis IDs

### Method 1: From Response
When you submit an analysis, the response includes the `analysis_id`.

### Method 2: List All Analyses
```bash
curl http://127.0.0.1:8000/analyses
```

### Method 3: Filter by Status
```bash
# See only completed analyses
curl "http://127.0.0.1:8000/analyses?status=completed"

# See only pending analyses
curl "http://127.0.0.1:8000/analyses?status=pending"
```

## 🧪 Quick Test

1. **Start server**: `uvicorn main:app --host 127.0.0.1 --port 8000`
2. **Submit analysis**: `curl -X POST http://127.0.0.1:8000/analyze-default -d "query=Test"`
3. **Get analysis ID**: `curl http://127.0.0.1:8000/analyses`
4. **Check status**: `curl http://127.0.0.1:8000/status/{analysis_id}`
5. **Get results**: `curl http://127.0.0.1:8000/result/{analysis_id}`

## 📝 Example Workflow

```bash
# 1. Submit analysis
curl -X POST http://127.0.0.1:8000/analyze-default -d "query=Analyze key financial metrics"

# Response: {"analysis_id": "abc123...", "status": "queued"}

# 2. Check status
curl http://127.0.0.1:8000/status/abc123...

# Response: {"status": "completed", "processing_time": 45.2}

# 3. Get results
curl http://127.0.0.1:8000/result/abc123...

# Response: {"analysis_result": "Detailed analysis...", "output_file_path": "output/..."}
```

## 🐛 Troubleshooting

- **Server not starting**: Check if port 8000 is available
- **Database errors**: Make sure Supabase connection string is correct
- **No analyses showing**: Submit an analysis first
- **Status stuck on pending**: Celery worker might not be running
