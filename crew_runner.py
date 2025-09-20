"""
Crew runner module for handling crew execution logic
"""
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, investment_analysis, risk_assessment, verification


class CrewRunner:
    """Handles crew execution and result processing"""
    
    def __init__(self):
        self.agents = [financial_analyst, verifier, investment_advisor, risk_assessor]
        self.tasks = [analyze_financial_document, investment_analysis, risk_assessment, verification]
    
    def run_crew(self, query: str, file_path: str = "data/sample.pdf") -> Dict[str, Any]:
        """
        Run the financial analysis crew
        
        Args:
            query: The analysis query
            file_path: Path to the financial document
            
        Returns:
            Dictionary containing analysis results and metadata
        """
        start_time = time.time()
        
        try:
            # Create and run the crew
            financial_crew = Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
            )
            
            # Execute the crew
            result = financial_crew.kickoff({'query': query})
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'result': str(result),
                'processing_time': processing_time,
                'query': query,
                'file_path': file_path,
                'completed_at': datetime.utcnow().isoformat(),
                'agents_used': [agent.role for agent in self.agents],
                'tasks_executed': [task.description for task in self.tasks]
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'status': 'error',
                'error_message': str(e),
                'processing_time': processing_time,
                'query': query,
                'file_path': file_path,
                'failed_at': datetime.utcnow().isoformat()
            }
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file exists and is accessible
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            return os.path.exists(file_path) and os.path.isfile(file_path)
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information
        """
        try:
            if not self.validate_file(file_path):
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


# Global crew runner instance
crew_runner = CrewRunner()
