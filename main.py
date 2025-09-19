from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import Optional
import os
import uuid
import asyncio

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document

app = FastAPI(title="Financial Document Analyzer")

def run_crew(query: str, file_path: str="data/sample.pdf"):
    """To run the whole crew"""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document],
        process=Process.sequential,
    )
    
    result = financial_crew.kickoff({'query': query})
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_financial_document_with_file(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze uploaded financial document and provide comprehensive investment recommendations"""
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query=="" or query is None:
            query = "Analyze this financial document for investment insights"
            
        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)
        
        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename,
            "file_source": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

@app.post("/analyze-default")
async def analyze_default_financial_document(
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze the default sample financial document and provide comprehensive investment recommendations"""
    
    try:
        # Validate query
        if query=="" or query is None:
            query = "Analyze this financial document for investment insights"
            
        # Use default sample file
        default_file_path = "data/sample.pdf"
        
        # Check if default file exists
        if not os.path.exists(default_file_path):
            raise HTTPException(status_code=404, detail=f"Default sample file not found at {default_file_path}")
            
        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=default_file_path)
        
        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": "sample.pdf",
            "file_source": "default"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)