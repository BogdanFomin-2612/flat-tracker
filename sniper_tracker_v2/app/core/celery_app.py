from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "sniper_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.scraper_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Kiev",
    enable_utc=True,
)

# Умный диспетчер запускается каждую 1 минуту и сам решает, чью задачу парсить
celery_app.conf.beat_schedule = {
    'run-scraper-dispatcher-every-minute': {
        'task': 'check_new_apartments',
        'schedule': 60.0, # 60 секунд = 1 минута
    }
}