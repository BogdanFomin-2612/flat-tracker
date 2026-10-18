import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.domain import User
from app.core.security import decode_access_token

# Эта переменная скажет Swagger'у, где находится эндпоинт логина для зеленой кнопки Authorize
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_db():
    async with async_session_maker() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Расшифровывает токен и достает пользователя из базы."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    # Заблокированный пользователь (is_active=False) теряет доступ сразу, даже с действующим токеном
    if user is None or not user.is_active:
        raise credentials_exception
    return user
