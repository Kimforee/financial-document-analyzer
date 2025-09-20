"""
Celery application configuration for the Financial Document Analyzer
"""
import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "financial_analyzer",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['worker_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_routes={
        'worker_tasks.analyze_document_task': {'queue': 'analysis'},
        'worker_tasks.investment_analysis_task': {'queue': 'analysis'},
        'worker_tasks.risk_assessment_task': {'queue': 'analysis'},
    },
    task_default_queue='default',
    task_default_exchange='default',
    task_default_exchange_type='direct',
    task_default_routing_key='default',
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-old-results': {
        'task': 'worker_tasks.cleanup_old_results',
        'schedule': 3600.0,  # Run every hour
    },
}

celery_app.conf.timezone = 'UTC'

if __name__ == '__main__':
    celery_app.start()
