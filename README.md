# Financial Document Analyzer - Debug Assignment
# Requires Python 3.11+

## Project Overview
A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents.
<img width="952" height="755" alt="image" src="https://github.com/user-attachments/assets/8d5e5c0e-9f4e-4899-a0d8-3f4980afb5e1" />
<img width="1067" height="583" alt="image" src="https://github.com/user-attachments/assets/fd5841b4-c0a6-4ff7-bfe5-9a2d616be7dc" />

* Setup instructions
* API docs with curl examples
* Bugs summary (linked to `BUGFIXES.md`)
* Note about agents & tasks not being used originally
* LLM + decorator fixes
* Prompt inefficiencies fixed

---

# 📑 Financial Document Analyzer

An AI-powered system that analyzes corporate reports, financial statements, and investment documents using **CrewAI agents**.
It extracts financial insights, performs risk assessments, verifies document validity, and generates investment recommendations.

---

## 🚀 Features

* Upload or analyze default financial documents (PDF format)
* Multi-agent CrewAI pipeline:

  * **Financial Analyst** — extracts & summarizes key insights
  * **Verifier** — checks document validity
  * **Investment Advisor** — suggests opportunities
  * **Risk Assessor** — highlights risks
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

## ⚙️ Setup

### 1. Clone repo

```bash
git clone https://github.com/<your-username>/financial-document-analyzer.git
cd financial-document-analyzer
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install --no-cache-dir -r requirements.txt
```

### 4. Environment variables

Create a `.env` file (see `.env.example`):

```env
# Choose your LLM backend
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
# Or use Ollama (no key needed if running locally)
DATABASE_URL=sqlite:///./analysis.db   # or Supabase/Postgres URL
REDIS_URL=redis://localhost:6379/0     # optional, for queue worker
```

### 5. Run FastAPI server

```bash
uvicorn main:app --reload
```

App will run at:
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
👉 Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API Documentation

### Health check

```bash
curl http://127.0.0.1:8000/
```

Response:

```json
{"message": "Financial Document Analyzer API is running"}
```

---

### Analyze document (upload a PDF)

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@data/sample.pdf" \
  -F "query=Summarize key financial highlights"
```

Response:

```json
{
  "status": "success",
  "query": "Summarize key financial highlights",
  "analysis": "... AI generated output ...",
  "file_processed": "sample.pdf",
  "file_source": "uploaded"
}
```

---

### Analyze default document

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "query=Summarize key financial highlights"
```

Response:

```json
{
  "status": "success",
  "query": "Summarize key financial highlights",
  "analysis": "...",
  "file_processed": "sample.pdf",
  "file_source": "default"
}
```
---

## 🎁 Bonus Features (Optional)

* **Queue Worker Model**: Celery + Redis for concurrent requests
* **Database Integration**: Store results in SQLite/Postgres/Supabase
* **Extensible Agents**: Easily add more roles/tools

---

## 📌 Notes

* Requires Python 3.11+
* Works with Gemini (`gemini-2.0-flash`) or local Ollama models (lighter ones like `phi3:mini` recommended if RAM is limited).
* API is stateless; for production you should run with Postgres + Celery worker for scaling.

---

## 🧑‍💻 Bugs Fixed Documentation

Detailed bug list with explanations is available in [BUGFIXES.md](./BUGFIXES.md).

---
