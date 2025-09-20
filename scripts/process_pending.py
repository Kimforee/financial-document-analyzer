#!/usr/bin/env python3
"""
Process pending analysis tasks manually
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def process_pending_tasks():
    """Process all pending tasks manually"""
    print("🔄 Processing Pending Tasks")
    print("=" * 30)
    
    try:
        from models import SessionLocal, AnalysisResult
        from crew_runner import crew_runner
        
        db = SessionLocal()
        
        # Get all pending tasks
        pending_tasks = db.query(AnalysisResult).filter(
            AnalysisResult.status == 'pending'
        ).all()
        
        if not pending_tasks:
            print("✅ No pending tasks found")
            return
        
        print(f"📋 Found {len(pending_tasks)} pending tasks")
        
        for i, task in enumerate(pending_tasks, 1):
            print(f"\n🔄 Processing task {i}/{len(pending_tasks)}")
            print(f"   ID: {task.id}")
            print(f"   Query: {task.query}")
            print(f"   File: {task.file_name}")
            
            try:
                # Update status to processing
                task.status = 'processing'
                db.commit()
                
                # Run the analysis
                result = crew_runner.run_crew(
                    query=task.query,
                    file_path=task.file_path
                )
                
                if result.get('status') == 'success':
                    # Update task with results
                    task.status = 'completed'
                    task.analysis_result = result.get('result', '')
                    task.completed_at = result.get('completed_at')
                    task.processing_time = result.get('processing_time', 0)
                    
                    # Save output file
                    from worker_tasks import save_analysis_to_file
                    output_path = save_analysis_to_file(str(task.id), result, task.query)
                    task.output_file_path = output_path
                    
                    print(f"   ✅ Completed successfully")
                    print(f"   ⏱️  Processing time: {result.get('processing_time', 0):.2f}s")
                    print(f"   📄 Output file: {output_path}")
                else:
                    # Mark as failed
                    task.status = 'failed'
                    task.error_message = result.get('error_message', 'Unknown error')
                    print(f"   ❌ Failed: {result.get('error_message', 'Unknown error')}")
                
                db.commit()
                
            except Exception as e:
                print(f"   ❌ Error processing task: {e}")
                task.status = 'failed'
                task.error_message = str(e)
                db.commit()
        
        print(f"\n🎉 Processing completed!")
        print(f"   Check results at: http://127.0.0.1:8000/analyses")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

def main():
    """Main function"""
    print("Financial Document Analyzer - Manual Task Processor")
    print("=" * 60)
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health/simple", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("⚠️  API server might not be running")
    except:
        print("⚠️  API server is not running")
        print("   Start it with: uvicorn main:app --host 127.0.0.1 --port 8000")
    
    process_pending_tasks()

if __name__ == "__main__":
    main()
