import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select

from app.core.database import async_session_maker
from app.models.domain import SubscriptionPlan
from app.api.users import router as users_router
from app.api.tasks import router as tasks_router
from app.services.scraper import RealEstateScraper
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

app = FastAPI(title="Sniper Tracker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Sniper Tracker API"}

@app.get("/test_scraper", tags=["Test"])
async def test_scraper(url: str):
    scraper = RealEstateScraper()
    result = await scraper.check_connection(url)
    return result