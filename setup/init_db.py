#!/usr/bin/env python3
"""
Database initialization script for the Financial Document Analyzer
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import init_database, create_tables, engine
from sqlalchemy import text


def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ["data", "output", "logs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def main():
    """Main initialization function"""
    print("🚀 Initializing Financial Document Analyzer Database...")
    print("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        return False
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Initialize database
    print("\n🗄️  Creating database tables...")
    if init_database():
        print("✅ Database tables created successfully")
    else:
        print("❌ Failed to create database tables")
        return False
    
    print("\n🎉 Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Start Redis server: redis-server")
    print("2. Start Celery worker: celery -A celery_app worker --loglevel=info")
    print("3. Start FastAPI server: uvicorn main:app --host 127.0.0.1 --port 8000")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
