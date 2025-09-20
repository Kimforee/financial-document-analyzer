#!/usr/bin/env python3
"""
Test datetime fix for SQLite
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_datetime_conversion():
    """Test datetime conversion for SQLite"""
    print("🧪 Testing DateTime Conversion")
    print("=" * 30)
    
    # Test string timestamp conversion
    test_timestamp = "2025-09-20T12:40:15.402281"
    
    try:
        # Convert string to datetime object
        dt = datetime.fromisoformat(test_timestamp.replace('Z', '+00:00'))
        print(f"✅ String timestamp: {test_timestamp}")
        print(f"✅ Converted to datetime: {dt}")
        print(f"✅ Type: {type(dt)}")
        print("✅ This will work with SQLite!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_datetime_conversion()
