from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import Optional
import os
import uuid
import asyncio

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, investment_analysis, risk_assessment, verification

app = FastAPI(title="Financial Document Analyzer")

def run_crew(query: str, file_path: str="data/sample.pdf"):
    """To run the whole crew"""
    financial_crew = Crew(
        agents=[financial_analyst, verifier, investment_advisor, risk_assessor],
        tasks=[analyze_financial_document, investment_analysis, risk_assessment, verification],
        process=Process.sequential,
    )
    
    result = financial_crew.kickoff({'query': query})
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_financial_document(
    file: Optional[UploadFile] = File(None),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document - use uploaded file if provided, otherwise use default from data folder"""
    
    file_path = None
    file_source = "default"
    file_processed = "sample.pdf"
    
    try:
        # Validate query
        if query=="" or query is None:
            query = "Analyze this financial document for investment insights"
        
        # If file is uploaded, save it and use it
        if file is not None:
            file_id = str(uuid.uuid4())
            file_path = f"data/financial_document_{file_id}.pdf"
            
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            file_source = "uploaded"
            file_processed = file.filename
        else:
            # Use default sample file
            file_path = "data/sample.pdf"
            
            # Check if default file exists
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"Default sample file not found at {file_path}")
            
        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)
        
        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file_processed,
            "file_source": file_source
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")
    
    finally:
        # Clean up uploaded file if it was uploaded
        if file is not None and file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)