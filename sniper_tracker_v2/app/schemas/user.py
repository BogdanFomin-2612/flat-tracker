from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# Базовая схема, общая для запросов и ответов
class UserBase(BaseModel):
    email: EmailStr
    telegram_chat_id: Optional[int] = None

# Схема для создания пользователя (регистрация)
# Пользователь обязан передать пароль, который мы потом захешируем
class UserCreate(UserBase):
    password: str

# Схема для отправки данных о пользователе обратно клиенту
# Заметь: здесь нет поля password, чтобы оно никогда не утекло через API
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_premium: bool
    created_at: datetime

    # Эта настройка говорит Pydantic, что данные придут из базы SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# Схема для авторизации (JWT-токен)
class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdateTelegram(BaseModel):
    telegram_chat_id: int    