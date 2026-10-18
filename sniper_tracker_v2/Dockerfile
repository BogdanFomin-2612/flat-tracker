# Используем официальный легкий образ Python
FROM python:3.11-slim

# Запрещаем Python писать .pyc файлы на диск и буферизовать stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Приложение работает не от root: при уязвимости в коде у атакующего будет меньше прав в контейнере
RUN useradd --create-home --uid 1000 app
COPY --chown=app:app . .
USER app

# Production-запуск: без --reload. --proxy-headers нужен, чтобы за reverse-proxy видеть реальный IP клиента
# (на нём держится ограничение частоты запросов). API наружу не публикуется, доступен только через прокси.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*"]
