
---

# 🐛 Bugfix Log — Financial Document Analyzer

This document lists the major bugs we encountered after resolving dependency conflicts in `requirements.txt`, and how we fixed them.

---

## 1. **Import Errors in `agents.py`**

* **Error**:

  ```
  ImportError: cannot import name 'Agent' from 'crewai.agents'
  ```
* **Cause**: New versions of CrewAI moved `Agent` and `LLM` classes to top-level imports.
* **Fix**:

  ```python
  from crewai import Agent, LLM
  ```

---

## 2. **LangChain Module Errors**

* **Errors**:

  ```
  ModuleNotFoundError: No module named 'langchain_openai'
  ModuleNotFoundError: No module named 'langchain_community'
  ```
* **Cause**: Old langchain modules were renamed.
* **Fix**: Removed unused imports and switched to CrewAI’s built-in `LLM`.

---

## 3. **Missing `crewai_tools`**

* **Error**:

  ```
  ModuleNotFoundError: No module named 'crewai_tools'
  ```
* **Cause**: Wrong import path.
* **Fix**: Use correct import:

  ```python
  from crewai_tools import tool
  ```

---

## 4. **Agent Tool Validation**

* **Error**:

  ```
  ValueError: Function must have a docstring
  ```
* **Cause**: CrewAI requires tools decorated with `@tool` to have docstrings.
* **Fix**: Added proper docstrings to all tool functions in `tools.py`.

---

## 5. **CrewAI Max RPM Limit**

* **Log**:

  ```
  [INFO]: Max RPM reached, waiting for next minute to start.
  ```
* **Cause**: Agents were defined with `max_rpm=1`, throttling requests.
* **Fix**: Removed or increased `max_rpm` in agent definitions.

---

## Final Result

* FastAPI server runs at: `http://127.0.0.1:8000/`
* `/` → Health check
* `/analyze` → Upload + analyze PDF
* `/analyze-default` → Analyze `sample.pdf`
* Agents now use **Gemini** successfully to process financial documents.
