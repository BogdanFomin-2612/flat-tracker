from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional

# Схема для создания пользователя (регистрация)
# Пользователь обязан передать пароль, который мы потом захешируем
class UserCreate(BaseModel):
    email: EmailStr
    # bcrypt учитывает только первые 72 байта, поэтому длиннее не принимаем
    password: str = Field(..., min_length=8, max_length=72)

# Схема для отправки данных о пользователе обратно клиенту
# Заметь: здесь нет поля password, чтобы оно никогда не утекло через API
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    telegram_chat_id: Optional[int] = None
    is_active: bool
    is_premium: bool
    plan_id: Optional[int] = None
    created_at: datetime

    # Эта настройка говорит Pydantic, что данные придут из базы SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# Схема для авторизации (JWT-токен)
class Token(BaseModel):
    access_token: str
    token_type: str
