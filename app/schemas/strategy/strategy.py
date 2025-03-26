from pydantic import BaseModel
from datetime import datetime

class StrategyCreate(BaseModel):
    name: str
    code: str

class StrategyUpdate(BaseModel):
    id: int
    name: str
    code: str

class StrategyRun(BaseModel):
    strategy_id: int
    strategy_id: list[int]
    binance_symbol: str
    interval: str
    end: datetime