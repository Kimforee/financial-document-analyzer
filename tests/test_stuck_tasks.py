#!/usr/bin/env python3
"""
Test processing stuck tasks
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_stuck_tasks():
    """Test finding and processing stuck tasks"""
    print("🧪 Testing Stuck Tasks Processing")
    print("=" * 40)
    
    try:
        from models import SessionLocal, AnalysisResult
        from single_call_runner import single_call_runner
        
        db = SessionLocal()
        
        # Get all pending and processing tasks (stuck tasks)
        stuck_tasks = db.query(AnalysisResult).filter(
            AnalysisResult.status.in_(['pending', 'processing'])
        ).all()
        
        print(f"📋 Found {len(stuck_tasks)} stuck tasks")
        
        for i, task in enumerate(stuck_tasks[:2], 1):  # Process only first 2 for testing
            print(f"\n🔄 Processing task {i}")
            print(f"   ID: {task.id}")
            print(f"   Status: {task.status}")
            print(f"   Query: {task.query}")
            
            try:
                # Update status to processing
                task.status = 'processing'
                db.commit()
                
                # Run the analysis with single call
                result = single_call_runner.run_analysis(
                    query=task.query,
                    file_path=task.file_path
                )
                
                if result.get('status') == 'success':
                    # Update task with results
                    task.status = 'completed'
                    task.analysis_result = result.get('result', '')
                    task.completed_at = result.get('completed_at')
                    task.processing_time = result.get('processing_time', 0)
                    
                    print(f"   ✅ Completed successfully")
                    print(f"   ⏱️  Processing time: {result.get('processing_time', 0):.2f}s")
                    print(f"   🔢 API calls made: {result.get('api_calls_made', 'unknown')}")
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
        
        print(f"\n🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_stuck_tasks()
