"""
Single Call Runner - Makes only 1 API call per task
"""
import os
import time
from datetime import datetime
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SingleCallRunner:
    """Makes only 1 API call per analysis task"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def run_analysis(self, query: str, file_path: str = "data/sample.pdf") -> Dict[str, Any]:
        """
        Run analysis with only 1 API call
        
        Args:
            query: The analysis query
            file_path: Path to the financial document
            
        Returns:
            Dictionary containing analysis results
        """
        start_time = time.time()
        
        try:
            # Read the document
            if not os.path.exists(file_path):
                return {
                    'status': 'error',
                    'error_message': f'File not found: {file_path}',
                    'processing_time': time.time() - start_time,
                    'api_calls_made': 0
                }
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                document_content = f.read()
            
            # Create comprehensive prompt for single API call
            prompt = f"""
            You are a financial analyst. Analyze the following financial document and provide a comprehensive response.

            USER QUERY: {query}

            FINANCIAL DOCUMENT:
            {document_content[:50000]}  # Limit to avoid token limits

            Please provide a complete analysis including:
            1. Direct answer to the user's query
            2. Key financial highlights and metrics
            3. Investment insights and recommendations
            4. Risk assessment and concerns
            5. Overall financial health summary

            Format your response as a structured financial analysis report.
            """
            
            # Make ONLY 1 API call
            print(f"Making 1 API call to Gemini for query: {query}")
            response = self.model.generate_content(prompt)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'result': response.text,
                'processing_time': processing_time,
                'query': query,
                'file_path': file_path,
                'completed_at': datetime.utcnow().isoformat(),
                'api_calls_made': 1,
                'method': 'single_call'
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'status': 'error',
                'error_message': str(e),
                'processing_time': processing_time,
                'query': query,
                'file_path': file_path,
                'failed_at': datetime.utcnow().isoformat(),
                'api_calls_made': 0
            }

# Global single call instance
single_call_runner = SingleCallRunner()
