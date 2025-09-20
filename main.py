from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from typing import Optional, Dict, Any
import os
import uuid
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, investment_analysis, risk_assessment, verification
from models import AnalysisResult, UserSession, TaskQueue, get_db, init_database
from worker_tasks import analyze_document_task, create_analysis_record, create_task_record
from celery_app import celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and create tables on startup"""
    # Startup
    init_database()
    yield
    # Shutdown (if needed)
    pass


app = FastAPI(title="Financial Document Analyzer", lifespan=lifespan)

def run_crew(query: str, file_path: str="data/sample.pdf"):
    """To run the whole crew (legacy function for backward compatibility)"""
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
async def analyze_financial_document_with_file(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
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
        
        # Create analysis record in database
        analysis_id = create_analysis_record(
            db=db,
            file_name=file.filename,
            file_path=file_path,
            query=query.strip(),
            file_source="uploaded"
        )
        
        # Queue the analysis task
        task = analyze_document_task.delay(
            analysis_id=analysis_id,
            query=query.strip(),
            file_path=file_path,
            file_source="uploaded"
        )
        
        # Create task record
        create_task_record(
            db=db,
            analysis_id=analysis_id,
            celery_task_id=task.id,
            task_type="document_analysis"
        )
        
        return {
            "status": "queued",
            "message": "Analysis task queued successfully",
            "analysis_id": analysis_id,
            "task_id": task.id,
            "query": query,
            "file_processed": file.filename,
            "file_source": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")
    
    finally:
        # Note: File cleanup is now handled by the worker task
        pass

@app.post("/analyze-default")
async def analyze_default_financial_document(
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
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
        
        # Create analysis record in database
        analysis_id = create_analysis_record(
            db=db,
            file_name="sample.pdf",
            file_path=default_file_path,
            query=query.strip(),
            file_source="default"
        )
        
        # Queue the analysis task
        task = analyze_document_task.delay(
            analysis_id=analysis_id,
            query=query.strip(),
            file_path=default_file_path,
            file_source="default"
        )
        
        # Create task record
        create_task_record(
            db=db,
            analysis_id=analysis_id,
            celery_task_id=task.id,
            task_type="document_analysis"
        )
        
        return {
            "status": "queued",
            "message": "Analysis task queued successfully",
            "analysis_id": analysis_id,
            "task_id": task.id,
            "query": query,
            "file_processed": "sample.pdf",
            "file_source": "default"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")


@app.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """Get the status of an analysis task"""
    try:
        analysis_record = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if not analysis_record:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "analysis_id": analysis_id,
            "status": analysis_record.status,
            "query": analysis_record.query,
            "file_name": analysis_record.file_name,
            "file_source": analysis_record.file_source,
            "created_at": analysis_record.created_at.isoformat(),
            "completed_at": analysis_record.completed_at.isoformat() if analysis_record.completed_at else None,
            "processing_time": analysis_record.processing_time,
            "error_message": analysis_record.error_message,
            "output_file_path": analysis_record.output_file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis status: {str(e)}")


@app.get("/result/{analysis_id}")
async def get_analysis_result(analysis_id: str, db: Session = Depends(get_db)):
    """Get the result of a completed analysis"""
    try:
        analysis_record = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if not analysis_record:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis_record.status != 'completed':
            raise HTTPException(
                status_code=400, 
                detail=f"Analysis not completed. Current status: {analysis_record.status}"
            )
        
        return {
            "analysis_id": analysis_id,
            "status": analysis_record.status,
            "query": analysis_record.query,
            "file_name": analysis_record.file_name,
            "file_source": analysis_record.file_source,
            "analysis_result": analysis_record.analysis_result,
            "created_at": analysis_record.created_at.isoformat(),
            "completed_at": analysis_record.completed_at.isoformat(),
            "processing_time": analysis_record.processing_time,
            "output_file_path": analysis_record.output_file_path,
            "metadata": analysis_record.analysis_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis result: {str(e)}")


@app.get("/tasks")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List analysis tasks with optional filtering"""
    try:
        query = db.query(AnalysisResult)
        
        if status:
            query = query.filter(AnalysisResult.status == status)
        
        total_count = query.count()
        tasks = query.order_by(AnalysisResult.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "tasks": [
                {
                    "analysis_id": str(task.id),
                    "status": task.status,
                    "query": task.query,
                    "file_name": task.file_name,
                    "file_source": task.file_source,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "processing_time": task.processing_time
                }
                for task in tasks
            ],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")


@app.get("/analyses")
async def list_analyses(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all analyses with detailed information - easier to find IDs"""
    try:
        query = db.query(AnalysisResult)
        
        if status:
            query = query.filter(AnalysisResult.status == status)
        
        total_count = query.count()
        analyses = query.order_by(AnalysisResult.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "analyses": [
                {
                    "analysis_id": str(analysis.id),
                    "status": analysis.status,
                    "query": analysis.query,
                    "file_name": analysis.file_name,
                    "file_source": analysis.file_source,
                    "created_at": analysis.created_at.isoformat(),
                    "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                    "processing_time": analysis.processing_time,
                    "error_message": analysis.error_message,
                    "output_file_path": analysis.output_file_path
                }
                for analysis in analyses
            ],
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "message": "Use the analysis_id to check status or get results"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")


@app.get("/health")
async def health_check():
    """Comprehensive health check including database and Celery"""
    db_status = "unknown"
    celery_status = "unknown"
    
    # Check database connection with timeout
    try:
        db = next(get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Celery connection with timeout
    try:
        # Use a simple ping instead of stats which can hang
        celery_app.control.ping(timeout=5)
        celery_status = "healthy"
    except Exception as e:
        celery_status = f"unhealthy: {str(e)}"
    
    # Determine overall status
    overall_status = "healthy" if db_status == "healthy" and celery_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "database": db_status,
        "celery": celery_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/simple")
async def simple_health_check():
    """Simple health check without external dependencies"""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)