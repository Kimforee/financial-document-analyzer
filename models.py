"""
Database models for the Financial Document Analyzer
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
import uuid

# Database configuration
# Default to SQLite for local development, can be overridden with Supabase
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")

# Force SQLite if Supabase connection fails
if "postgresql" in DATABASE_URL.lower():
    try:
        import psycopg2
        # Test connection
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
    except Exception as e:
        print(f"⚠️  Supabase connection failed: {e}")
        print("🔄 Falling back to SQLite for local development")
        DATABASE_URL = "sqlite:///./financial_analyzer.db"

# Create engine with better connection handling
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_timeout=30,   # 30 second timeout for getting connection from pool
    max_overflow=0,    # Don't allow overflow connections
    echo=False         # Set to True for SQL debugging
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class AnalysisResult(Base):
    """Model for storing analysis results"""
    __tablename__ = "analysis_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    query = Column(Text, nullable=False)
    analysis_result = Column(Text, nullable=True)
    file_source = Column(String(50), nullable=False)  # 'uploaded' or 'default'
    status = Column(String(50), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    
    # Analysis metadata
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(10), nullable=True)
    
    # Output file paths
    output_file_path = Column(String(500), nullable=True)
    output_format = Column(String(10), default='txt')  # 'txt' or 'doc'
    
    # Additional metadata as JSON
    analysis_metadata = Column(JSON, nullable=True)


class UserSession(Base):
    """Model for storing user session data"""
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Session metadata
    total_requests = Column(Integer, default=0)
    total_analyses = Column(Integer, default=0)


class TaskQueue(Base):
    """Model for tracking Celery tasks"""
    __tablename__ = "task_queue"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    celery_task_id = Column(String(255), unique=True, nullable=False)
    analysis_result_id = Column(String(36), nullable=False)
    task_type = Column(String(50), nullable=False)  # 'document_analysis', 'investment_analysis', etc.
    status = Column(String(50), default='pending')  # 'pending', 'running', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Task metadata
    priority = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize the database with tables"""
    try:
        create_tables()
        print("Database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False
