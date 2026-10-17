from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., example="1-к квартира на Подоле")
    url: str = Field(..., example="https://www.olx.ua/uk/nedvizhimost/kvartiry/arenda-kvartir/kiev/")
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    rooms: Optional[int] = Field(None, ge=1, le=5)
    owner_only: bool = False

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    user_id: int
    check_interval_minutes: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)