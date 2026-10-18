import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.future import select

from app.core.config import CORS_ORIGINS, IS_PRODUCTION
from app.core.database import async_session_maker
from app.core.rate_limit import limiter
from app.models.domain import SubscriptionPlan
from app.api.users import router as users_router
from app.api.tasks import router as tasks_router
from app.services.telegram import start_telegram_polling

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базовых тарифов при старте сервера
    async with async_session_maker() as session:
        # Проверяем и создаем тариф "Free"
        result_free = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == "Free"))
        if not result_free.scalars().first():
            free_plan = SubscriptionPlan(name="Free", price=0, max_active_tasks=1, check_interval_minutes=60)
            session.add(free_plan)

        # Проверяем и создаем тариф "Pro"
        result_pro = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == "Pro"))
        if not result_pro.scalars().first():
            pro_plan = SubscriptionPlan(name="Pro", price=299, max_active_tasks=10, check_interval_minutes=5)
            session.add(pro_plan)

        await session.commit()

    # Запуск фонового процесса для Telegram-бота
    polling_task = asyncio.create_task(start_telegram_polling())

    yield

    # Остановка фонового процесса при выключении сервера
    polling_task.cancel()

# В production документация API (/docs, /redoc, /openapi.json) отключена, чтобы не раскрывать структуру API
app = FastAPI(
    title="Sniper Tracker API",
    lifespan=lifespan,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

# Ограничение частоты запросов (лимиты заданы на эндпоинтах через @limiter.limit)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(users_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Sniper Tracker API"}
