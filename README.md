# Financial Document Analyzer - Debug Assignment
# Requires Python 3.11+

## Project Overview
A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents.
<img width="952" height="755" alt="image" src="https://github.com/user-attachments/assets/8d5e5c0e-9f4e-4899-a0d8-3f4980afb5e1" />
<img width="1067" height="583" alt="image" src="https://github.com/user-attachments/assets/fd5841b4-c0a6-4ff7-bfe5-9a2d616be7dc" />


## Features

* Upload or analyze default financial documents (PDF format)
* Multi-agent CrewAI pipeline:

  * **Financial Analyst** — extracts & summarizes key insights
  * **Verifier** — checks document validity
  * **Investment Advisor** — suggests opportunities
  * **Risk Assessor** — highlights risks  (financial stress, debt, volatility, regulatory, operational, competitive, technology risks)
* Tools for:

  * Reading PDF content
  * Running investment analysis
  * Creating risk assessments
* API endpoint `/analyze` and `/analyze-default` 
* Support for local models (Ollama) or hosted models (Gemini, OpenAI)
  
  Configurable database backend (Supabase/Postgres supported)
  Optional queue/worker model (Celery + Redis) for concurrent tasks

---

## 🐛 Bugs Fixed

We fixed several issues in the original codebase. See [BUGFIXES.md](./BUGFIXES.md) for details.

### Key Problems Solved

1. **Agents and Tasks Missing in Crew**

   * Originally, only `financial_analyst` and one task were used.
   * Fixed: all four agents + all tasks (`analyze_financial_document`, `investment_analysis`, `risk_assessment`, `verification`) are included in the crew configuration.

2. **LLM Object Error**

   * Wrong imports like `from crewai.agents import Agent` and `from crewai.tools import tool`.
   * Fixed:

     ```python
     from crewai import Agent, LLM
     from crewai_tools import tool
     ```

3. **Missing Tool Decorator**

   * Tools defined without proper docstrings/decorators caused runtime errors.
   * Fixed by adding:

     ```python
     @tool("Read financial document data")
     def read_data_tool(...):
         """Reads PDF file and returns text."""
     ```

4. **Inefficient / Incorrect Prompts**

   * Some agent prompts were unrealistic or incomplete.
   * Fixed: refined agent backstories and task descriptions to align with financial analysis while keeping humor optional.

5. **Dependency Conflicts**

   * Major conflicts in `requirements.txt` (protobuf, opentelemetry, chromadb, embedchain, openai, langsmith).
   * Fixed: cleaned and pinned compatible versions, removed unnecessary deps.

---


##  Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# a : Run the complete setup script
bash setup.sh
```

```bash
# b :  Activate the environment
source venv/bin/activate
```

```bash
# c : Run the app after setup is complete 
uvicorn main:app --host 127.0.0.1 --port 8000
```

```bash
# d : If tasks are stuck in the queue free them using this 
python scripts/process_pending.py
```

### Option 2: Manual Setup
1. **Setup Environment**:
```bash
   python setup/setup_secure.py
```

2. **Configure API Keys**:
   Edit `.env` file with your API keys:
   - `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - `SERPER_API_KEY`: Get from [Serper](https://serper.dev/) (Not needed as of now)

3. **Start Services**:
```bash
   # Terminal 1: Start Redis
   redis-server
   
   # Terminal 2: Start API Server
   uvicorn main:app --host 127.0.0.1 --port 8000
   
   # Terminal 3: Start Worker
   celery -A celery_app worker --loglevel=info
   ```

4. **Test the System**:
```bash
   # There are tests as well
   python tests/test_api.py
   ```

###  Documentation
- **Complete Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **Quick Start Guide**: [docs/QUICK_START.md](docs/QUICK_START.md)
- **Troubleshooting Guide**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

##  Project Structure

```
financial-document-analyzer-debug/
├── main.py                 # FastAPI application
├── models.py              # Database models
├── celery_app.py          # Celery configuration
├── worker_tasks.py        # Background tasks
├── crew_runner.py         # Crew execution logic
├── single_call_runner.py  # To execute all the agents in a call so as to limit gemini api usage
├── agents.py              # AI agents
├── tools.py               # Analysis tools
├── setup.sh               # For instant automated set up
├── task.py                # Task definitions
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── setup/                 # Setup scripts
│   ├── setup_secure.py
│   ├── init_db.py
│   └── env_template.txt
├── scripts/               # Utility scripts
│   ├── start_services.sh
│   ├── process_pending.py
│   └── debug_connections.py
├── tests/                 # Test files
│   ├── test_api.py
│   └── test_integration.py#  more tests will be added 
└── docs/                  # Documentation
    ├── README_SETUP.md
    ├── QUICK_START.md
    └── TROUBLESHOOTING.md
```

##  API Endpoints

- `POST /analyze` - Upload and analyze document
- `POST /analyze-default` - Analyze sample document
- `GET /analyses` - List all analyses with IDs
- `GET /status/{id}` - Check analysis status
- `GET /result/{id}` - Get analysis results
- `GET /health` - Health check

##  Development

- **Database**: SQLite (default) or PostgreSQL/Supabase
- **Queue**: Redis + Celery
- **AI**: CrewAI with Gemini
- **API**: FastAPI
- **Storage**: Local files + Database (Sqlite or Supabase(postgres))

##  License

MIT License