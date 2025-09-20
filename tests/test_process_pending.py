#!/usr/bin/env python3
"""
Test the updated process_pending.py script
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_single_call():
    """Test single call runner directly"""
    print("🧪 Testing Single Call Runner")
    print("=" * 30)
    
    try:
        from single_call_runner import single_call_runner
        
        result = single_call_runner.run_analysis(
            query="Test single call processing",
            file_path="data/sample.pdf"
        )
        
        print(f"Status: {result['status']}")
        print(f"API calls made: {result.get('api_calls_made', 'unknown')}")
        print(f"Processing time: {result.get('processing_time', 0):.2f}s")
        
        if result['status'] == 'success':
            print("✅ Single call system works!")
        else:
            print(f"❌ Error: {result.get('error_message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing single call: {e}")

if __name__ == "__main__":
    test_single_call()
