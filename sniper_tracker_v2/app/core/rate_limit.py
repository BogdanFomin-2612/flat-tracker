from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import REDIS_URL

# Счётчики хранятся в Redis, чтобы лимиты не сбрасывались при перезапуске API.
# IP берётся из соединения; за reverse-proxy uvicorn запускается с --proxy-headers,
# тогда это реальный IP клиента из X-Forwarded-For.
limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)
