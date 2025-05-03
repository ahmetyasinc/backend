from pydantic import BaseModel
from typing import List
from datetime import datetime

class BotsBase(BaseModel):
    strategy_id: int
    api_id: int
    period: str
    stocks: List[str]
    active: bool
    candle_count: int
    active_days: List[str]
    active_hours: str

class BotsCreate(BotsBase):
    pass

class BotsUpdate(BaseModel):
    period: str | None = None
    stocks: List[str] | None = None
    candle_count: int | None = None
    active_days: List[str] | None = None
    active_hours: str | None = None
    active: bool | None = None

class BotsOut(BotsBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
