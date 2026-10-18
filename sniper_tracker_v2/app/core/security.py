from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext

from app.core.config import SECRET_KEY

ALGORITHM = "HS256"
# Время жизни токена (сделаем 7 дней, чтобы пользователям не приходилось логиниться каждый день)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# Настройка passlib для использования алгоритма bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с хешем из базы."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширует пароль перед сохранением в БД."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Генерирует JWT-токен."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Проверяет подпись и срок действия токена. Бросает jwt.PyJWTError, если токен невалиден."""
    # Алгоритм задан жёстко: токены с alg=none или другим алгоритмом отклоняются
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]})
