from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Literal, Optional

from app.services.olx_search import CITIES

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150, example="1-к квартира на Подоле")
    city: Optional[str] = Field(None, example="kiev") # None = вся Украина
    deal_type: Literal["rent", "sale"] = "rent"
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    rooms: Optional[int] = Field(None, ge=1, le=5)
    owner_only: bool = False

class TaskCreate(TaskBase):
    # Ссылку на OLX собирает только сервер. Свой url передать нельзя: иначе парсер можно заставить
    # ходить по внутренним адресам (redis, база, метаданные облака) — SSRF
    model_config = ConfigDict(extra="forbid")

    @field_validator("city")
    @classmethod
    def city_must_be_known(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in CITIES:
            raise ValueError("Неизвестный город")
        return value or None

class TaskResponse(TaskBase):
    id: int
    user_id: int
    url: str
    # Для задач, созданных до появления поля, в БД будет NULL
    deal_type: Optional[str] = None
    check_interval_minutes: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
