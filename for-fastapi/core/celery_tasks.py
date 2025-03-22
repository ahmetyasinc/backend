from celery import Celery
from .config import settings
import time

celery_app = Celery("fastapi_celery", broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0", backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0")

@celery_app.task
def test_celery(word: str) -> str:
    time.sleep(5)
    return f"test task return {word}"

#asdasd