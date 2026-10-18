import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.config import ENABLE_TEST_PAYMENTS, TELEGRAM_BOT_USERNAME, TELEGRAM_LINK_TTL_MINUTES
from app.core.database import async_session_maker
from app.core.rate_limit import limiter
from app.models.domain import User, SubscriptionPlan
from app.schemas.user import UserCreate, Token, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")  # защита от массовой регистрации бесплатных аккаунтов
async def register_user(request: Request, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user_data.email.lower()
    result = await db.execute(select(User).where(User.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=email, hashed_password=hashed_password)

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
@limiter.limit("10/minute")  # защита от перебора паролей
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username.lower()))
    user = result.scalars().first()

    # Одинаковый ответ для неверного пароля и заблокированного аккаунта
    if not user or not verify_password(form_data.password, user.hashed_password) or not user.is_active:
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

@router.post("/upgrade", status_code=200)
async def upgrade_to_pro(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Тестовая оплата без денег. Работает только локально с ENABLE_TEST_PAYMENTS=true;
    # в production тариф должен меняться только после подтверждённого платежа
    if not ENABLE_TEST_PAYMENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Оплата пока недоступна")

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
@limiter.limit("10/minute")
async def get_telegram_deep_link(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not TELEGRAM_BOT_USERNAME:
        raise HTTPException(status_code=503, detail="Telegram-бот не настроен")

    now = datetime.now(timezone.utc)
    token = current_user.telegram_connect_token
    expires_at = current_user.telegram_connect_token_expires_at

    # Ссылка одноразовая и живёт ограниченное время: старый или просроченный код заменяем новым
    if not token or not expires_at or expires_at <= now:
        token = secrets.token_urlsafe(24)
        await db.execute(
            update(User).where(User.id == current_user.id).values(
                telegram_connect_token=token,
                telegram_connect_token_expires_at=now + timedelta(minutes=TELEGRAM_LINK_TTL_MINUTES),
            )
        )
        await db.commit()

    return {"link": f"https://t.me/{TELEGRAM_BOT_USERNAME}?start={token}"}
