from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
import os

# Подтягиваем ключ из .env, задаем алгоритм шифрования
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
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
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt