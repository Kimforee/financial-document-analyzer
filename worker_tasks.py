"""
Celery worker tasks for the Financial Document Analyzer
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from celery import current_task
from sqlalchemy.orm import Session

from celery_app import celery_app
from models import AnalysisResult, TaskQueue, SessionLocal, create_tables
from single_call_runner import single_call_runner
# from crew_runner import crew_runner

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get file information
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    try:
        if not os.path.exists(file_path):
            return {'error': 'File not found or not accessible'}
        
        stat = os.stat(file_path)
        return {
            'file_name': os.path.basename(file_path),
            'file_size': stat.st_size,
            'file_type': os.path.splitext(file_path)[1].lower(),
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except Exception as e:
        return {'error': f'Error getting file info: {str(e)}'}


@celery_app.task(bind=True, name='worker_tasks.analyze_document_task')
def analyze_document_task(self, analysis_id: str, query: str, file_path: str, file_source: str = "uploaded") -> Dict[str, Any]:
    """
    Celery task for analyzing financial documents
    
    Args:
        analysis_id: UUID of the analysis record
        query: Analysis query
        file_path: Path to the financial document
        file_source: Source of the file ('uploaded' or 'default')
        
    Returns:
        Dictionary containing analysis results
    """
    db = SessionLocal()
    task_record = None
    
    try:
        # Update task status to running
        task_record = db.query(TaskQueue).filter(
            TaskQueue.celery_task_id == self.request.id
        ).first()
        
        if task_record:
            task_record.status = 'running'
            task_record.started_at = datetime.utcnow()
            db.commit()
        
        # Update analysis result status
        analysis_record = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if analysis_record:
            analysis_record.status = 'processing'
            db.commit()
        
        # Run single call analysis (only 1 API call)
        result = single_call_runner.run_analysis(query=query, file_path=file_path)

        # Run the crew analysis
        # result = crew_runner.run_crew(query=query, file_path=file_path)
        
        # Save analysis result to file
        output_file_path = save_analysis_to_file(analysis_id, result, query)
        
        # Update analysis record with results
        if analysis_record:
            # Handle different result formats
            if isinstance(result, dict):
                analysis_record.analysis_result = result.get('result', str(result))
                analysis_record.status = 'completed' if result.get('status') == 'success' else 'completed'  # Default to completed for now
                analysis_record.processing_time = result.get('processing_time', 0)
                analysis_record.error_message = result.get('error_message')
            else:
                # If result is not a dict, treat it as successful
                analysis_record.analysis_result = str(result)
                analysis_record.status = 'completed'
                analysis_record.processing_time = 0
                analysis_record.error_message = None
            
            analysis_record.completed_at = datetime.utcnow()
            analysis_record.output_file_path = output_file_path
            
            db.commit()
        
        # Update task record
        if task_record:
            if isinstance(result, dict):
                task_record.status = 'completed' if result.get('status') == 'success' else 'completed'
                task_record.error_message = result.get('error_message')
            else:
                task_record.status = 'completed'
                task_record.error_message = None
            
            task_record.completed_at = datetime.utcnow()
            db.commit()
        
        return result
        
    except Exception as e:
        # Handle errors
        error_msg = f"Task failed: {str(e)}"
        
        # Rollback any pending changes
        db.rollback()
        
        # Update analysis record with error
        analysis_record = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if analysis_record:
            analysis_record.status = 'failed'
            analysis_record.completed_at = datetime.utcnow()
            analysis_record.error_message = error_msg
            db.commit()
        
        # Update task record with error
        if task_record:
            task_record.status = 'failed'
            task_record.completed_at = datetime.utcnow()
            task_record.error_message = error_msg
            db.commit()
        
        # Retry the task if it hasn't exceeded max retries
        if self.request.retries < 3:
            raise self.retry(countdown=60, max_retries=3)
        
        return {
            'status': 'error',
            'error_message': error_msg,
            'analysis_id': analysis_id
        }
    
    finally:
        db.close()


@celery_app.task(name='worker_tasks.investment_analysis_task')
def investment_analysis_task(analysis_id: str, financial_data: str) -> Dict[str, Any]:
    """
    Celery task for investment analysis
    
    Args:
        analysis_id: UUID of the analysis record
        financial_data: Financial document data
        
    Returns:
        Dictionary containing investment analysis results
    """
    # This would contain specific investment analysis logic
    # For now, return a placeholder
    return {
        'status': 'success',
        'investment_analysis': 'Investment analysis completed',
        'analysis_id': analysis_id
    }


@celery_app.task(name='worker_tasks.risk_assessment_task')
def risk_assessment_task(analysis_id: str, financial_data: str) -> Dict[str, Any]:
    """
    Celery task for risk assessment
    
    Args:
        analysis_id: UUID of the analysis record
        financial_data: Financial document data
        
    Returns:
        Dictionary containing risk assessment results
    """
    # This would contain specific risk assessment logic
    # For now, return a placeholder
    return {
        'status': 'success',
        'risk_assessment': 'Risk assessment completed',
        'analysis_id': analysis_id
    }


@celery_app.task(name='worker_tasks.cleanup_old_results')
def cleanup_old_results() -> Dict[str, Any]:
    """
    Celery task for cleaning up old analysis results
    
    Returns:
        Dictionary containing cleanup results
    """
    db = SessionLocal()
    
    try:
        # Delete results older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_results = db.query(AnalysisResult).filter(
            AnalysisResult.created_at < cutoff_date
        ).all()
        
        count = len(old_results)
        
        for result in old_results:
            # Delete output file if it exists
            if result.output_file_path and os.path.exists(result.output_file_path):
                try:
                    os.remove(result.output_file_path)
                except Exception:
                    pass  # Ignore file deletion errors
            
            db.delete(result)
        
        db.commit()
        
        return {
            'status': 'success',
            'deleted_count': count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'error_message': str(e)
        }
    
    finally:
        db.close()


def save_analysis_to_file(analysis_id: str, result: Dict[str, Any], query: str) -> str:
    """
    Save analysis result to a file
    
    Args:
        analysis_id: UUID of the analysis
        result: Analysis result dictionary
        query: Original query
        
    Returns:
        Path to the saved file
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.getenv("OUTPUT_DIR", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{analysis_id}_{timestamp}.txt"
        file_path = os.path.join(output_dir, filename)
        
        # Prepare content
        if isinstance(result, dict):
            status = result.get('status', 'completed')
            processing_time = result.get('processing_time', 0)
            analysis_result = result.get('result', str(result))
            error_message = result.get('error_message', 'None')
        else:
            status = 'completed'
            processing_time = 0
            analysis_result = str(result)
            error_message = 'None'
        
        content = f"""
Financial Document Analysis Report
==================================

Analysis ID: {analysis_id}
Query: {query}
Generated: {datetime.utcnow().isoformat()}
Status: {status}

Processing Time: {processing_time:.2f} seconds

Analysis Result:
{analysis_result}

Error Message:
{error_message}

Metadata:
- Agents Used: {', '.join(result.get('agents_used', [])) if isinstance(result, dict) else 'N/A'}
- Tasks Executed: {', '.join(result.get('tasks_executed', [])) if isinstance(result, dict) else 'N/A'}
- File Path: {result.get('file_path', 'N/A') if isinstance(result, dict) else 'N/A'}
        """.strip()
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
        
    except Exception as e:
        print(f"Error saving analysis to file: {e}")
        return ""


def create_analysis_record(db: Session, file_name: str, file_path: str, query: str, file_source: str) -> str:
    """
    Create a new analysis record in the database
    
    Args:
        db: Database session
        file_name: Name of the file
        file_path: Path to the file
        query: Analysis query
        file_source: Source of the file
        
    Returns:
        UUID string of the created analysis record
    """
    analysis_id = str(uuid.uuid4())
    
    # Get file info
    # file_info = crew_runner.get_file_info(file_path)
    file_info = get_file_info(file_path)
    
    analysis_record = AnalysisResult(
        id=analysis_id,
        file_name=file_name,
        file_path=file_path,
        query=query,
        file_source=file_source,
        file_size=file_info.get('file_size'),
        file_type=file_info.get('file_type'),
        status='pending'
    )
    
    db.add(analysis_record)
    db.commit()
    
    return analysis_id


def create_task_record(db: Session, analysis_id: str, celery_task_id: str, task_type: str) -> str:
    """
    Create a new task record in the database
    
    Args:
        db: Database session
        analysis_id: UUID string of the analysis record
        celery_task_id: Celery task ID
        task_type: Type of task
        
    Returns:
        UUID string of the created task record
    """
    task_id = str(uuid.uuid4())
    
    task_record = TaskQueue(
        id=task_id,
        celery_task_id=celery_task_id,
        analysis_result_id=analysis_id,
        task_type=task_type,
        status='pending'
    )
    
    db.add(task_record)
    db.commit()
    
    return task_id
