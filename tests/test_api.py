#!/usr/bin/env python3
"""
Simple API testing script for the Financial Document Analyzer
"""
import requests
import json
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"  # Change this to your server URL

def test_health():
    """Test health check"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health/simple")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def submit_analysis():
    """Submit an analysis and return the analysis ID"""
    print("\n📊 Submitting analysis...")
    try:
        data = {"query": "Analyze this financial document for key insights"}
        response = requests.post(f"{BASE_URL}/analyze-default", data=data)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result['analysis_id']
            print(f"✅ Analysis submitted successfully!")
            print(f"   Analysis ID: {analysis_id}")
            print(f"   Status: {result['status']}")
            print(f"   Query: {result['query']}")
            return analysis_id
        else:
            print(f"❌ Analysis submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Analysis submission error: {e}")
        return None

def check_status(analysis_id):
    """Check the status of an analysis"""
    print(f"\n⏳ Checking status for analysis {analysis_id}...")
    try:
        response = requests.get(f"{BASE_URL}/status/{analysis_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status check successful:")
            print(f"   Status: {data['status']}")
            print(f"   Query: {data['query']}")
            print(f"   File: {data['file_name']}")
            print(f"   Created: {data['created_at']}")
            if data['completed_at']:
                print(f"   Completed: {data['completed_at']}")
            if data['processing_time']:
                print(f"   Processing time: {data['processing_time']}s")
            return data['status']
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def list_analyses():
    """List all analyses to see IDs"""
    print("\n📋 Listing all analyses...")
    try:
        response = requests.get(f"{BASE_URL}/analyses")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_count']} analyses:")
            
            for i, analysis in enumerate(data['analyses'][:5]):  # Show first 5
                print(f"\n   {i+1}. Analysis ID: {analysis['analysis_id']}")
                print(f"      Status: {analysis['status']}")
                print(f"      Query: {analysis['query'][:50]}...")
                print(f"      Created: {analysis['created_at']}")
                if analysis['completed_at']:
                    print(f"      Completed: {analysis['completed_at']}")
            
            if data['total_count'] > 5:
                print(f"\n   ... and {data['total_count'] - 5} more analyses")
            
            return data['analyses']
        else:
            print(f"❌ List analyses failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ List analyses error: {e}")
        return []

def get_result(analysis_id):
    """Get the result of a completed analysis"""
    print(f"\n📄 Getting result for analysis {analysis_id}...")
    try:
        response = requests.get(f"{BASE_URL}/result/{analysis_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Results retrieved successfully!")
            print(f"   Status: {data['status']}")
            print(f"   Query: {data['query']}")
            print(f"   Processing time: {data['processing_time']}s")
            print(f"   Output file: {data['output_file_path']}")
            print(f"\n   Analysis Result:")
            print(f"   {'='*50}")
            print(data['analysis_result'][:500] + "..." if len(data['analysis_result']) > 500 else data['analysis_result'])
            print(f"   {'='*50}")
            return True
        else:
            print(f"❌ Result retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Result retrieval error: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 Financial Document Analyzer - API Testing")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Please start the server first.")
        print("   Run: uvicorn main:app --host 127.0.0.1 --port 8000")
        return
    
    # Test 2: List existing analyses
    analyses = list_analyses()
    
    # Test 3: Submit new analysis
    analysis_id = submit_analysis()
    if not analysis_id:
        print("\n❌ Could not submit analysis")
        return
    
    # Test 4: Check status
    status = check_status(analysis_id)
    if not status:
        print("\n❌ Could not check status")
        return
    
    # Test 5: If completed, get result
    if status == 'completed':
        get_result(analysis_id)
    else:
        print(f"\n⏳ Analysis is {status}. You can check again later with:")
        print(f"   curl http://127.0.0.1:8000/status/{analysis_id}")
        print(f"   curl http://127.0.0.1:8000/result/{analysis_id}")
    
    print(f"\n🎉 Testing completed!")
    print(f"\n📋 To see all analyses: curl http://127.0.0.1:8000/analyses")
    print(f"🔍 To check status: curl http://127.0.0.1:8000/status/{analysis_id}")
    print(f"📄 To get result: curl http://127.0.0.1:8000/result/{analysis_id}")

if __name__ == "__main__":
    main()
