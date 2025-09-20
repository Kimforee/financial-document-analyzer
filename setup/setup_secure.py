#!/usr/bin/env python3
"""
Secure environment setup script for the Financial Document Analyzer
"""
import os
import sys
import shutil
from dotenv import load_dotenv

def create_env_from_template():
    """Create .env file from template"""
    template_file = "setup/env_template.txt"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists. Skipping creation.")
        print(f"   If you want to recreate it, delete {env_file} first")
        return False
    
    if not os.path.exists(template_file):
        print(f"❌ Template file {template_file} not found")
        return False
    
    try:
        shutil.copy(template_file, env_file)
        print(f"✅ Created {env_file} from template")
        print(f"📝 Please edit {env_file} and add your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["data", "output", "logs"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'celery',
        'redis',
        'sqlalchemy',
        'python-dotenv',
        'crewai',
        'langchain'
    ]
    
    missing_packages = []
    
    # Map package names to their import names
    package_import_map = {
        'fastapi': 'fastapi',
        'celery': 'celery',
        'redis': 'redis',
        'sqlalchemy': 'sqlalchemy',
        'python-dotenv': 'dotenv',
        'crewai': 'crewai',
        'langchain': 'langchain'
    }
    
    for package in required_packages:
        try:
            import_name = package_import_map.get(package, package)
            __import__(import_name)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def validate_env_file():
    """Validate that .env file has required values"""
    load_dotenv()
    
    required_vars = ['GEMINI_API_KEY', 'SERPER_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing or placeholder values in .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file with actual API keys")
        return False
    
    print("✅ Environment variables look good")
    return True

def main():
    """Main setup function"""
    print("🔧 Financial Document Analyzer - Secure Setup")
    print("=" * 50)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return False
    
    # Create directories
    print("\n📁 Creating directories...")
    if not create_directories():
        print("\n❌ Failed to create directories")
        return False
    
    # Create .env file from template
    print("\n⚙️  Setting up environment...")
    if not create_env_from_template():
        print("\n❌ Failed to create .env file")
        return False
    
    # Validate .env file
    print("\n🔍 Validating environment...")
    validate_env_file()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your actual API keys:")
    print("   - GEMINI_API_KEY: Get from https://makersuite.google.com/app/apikey")
    print("   - SERPER_API_KEY: Get from https://serper.dev/")
    print("2. Choose your database:")
    print("   - SQLite (default): No changes needed")
    print("   - Supabase: Uncomment and update DATABASE_URL")
    print("3. Start the services:")
    print("   - Redis: redis-server")
    print("   - API: uvicorn main:app --host 127.0.0.1 --port 8000")
    print("   - Worker: celery -A celery_app worker --loglevel=info")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
