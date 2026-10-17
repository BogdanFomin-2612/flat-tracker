import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import async_session_maker
from app.models.domain import User, SubscriptionPlan
from app.schemas.user import UserCreate, Token, UserResponse, UserUpdateTelegram
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
        
    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    
    # Автоматически назначаем тариф Free
    plan_result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == "Free"))
    free_plan = plan_result.scalar_one_or_none()
    if free_plan:
        new_user.plan_id = free_plan.id
        
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me/telegram", response_model=UserResponse)
async def update_telegram(
    telegram_data: UserUpdateTelegram,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Прямой апдейт для избежания конфликта сессий
    await db.execute(
        update(User).where(User.id == current_user.id).values(telegram_chat_id=telegram_data.telegram_chat_id)
    )
    await db.commit()
    return current_user

@router.post("/upgrade", status_code=200)
async def upgrade_to_pro(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == "Pro"))
    pro_plan = result.scalar_one_or_none()
    
    if not pro_plan:
        raise HTTPException(status_code=404, detail="Тариф PRO не найден в базе")
        
    # Гарантированная запись нового тарифа в базу данных
    await db.execute(
        update(User).where(User.id == current_user.id).values(plan_id=pro_plan.id)
    )
    await db.commit()
    
    return {"message": "Успешно обновлено до PRO", "plan_id": pro_plan.id}

@router.get("/me/telegram-link")
async def get_telegram_deep_link(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    token = current_user.telegram_connect_token
    
    # Если токена еще нет, генерируем его и обновляем прямым запросом
    if not token:
        token = str(uuid.uuid4())
        await db.execute(
            update(User).where(User.id == current_user.id).values(telegram_connect_token=token)
        )
        await db.commit()

    # Берем имя бота из .env
    bot_username = os.getenv("TELEGRAM_BOT_USERNAME", "flat_radar_app_bot")
    
    # Формируем Deep Link
    deep_link = f"https://t.me/{bot_username}?start={token}"
    
    return {"link": deep_link}