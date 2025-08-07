# backend/app/tasks/ai_tasks.py
from celery import Celery
from config import settings

celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery.task
def process_note_async(note_data):
    # Local import to avoid circular dependency
    from services.ai_service import AIService
    ai_service = AIService()
    return ai_service._process_note_sync(note_data)

@celery.task
def generate_export_task(user_id, format='markdown'):
    # Local import to avoid potential circular dependencies
    from services.export_service import ExportService
    return ExportService().generate_export(user_id, format)