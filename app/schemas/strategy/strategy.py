from pydantic import BaseModel
from typing import Dict, Any
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
    
    binance_symbol: str
    interval: str
    end: datetime

class UpdatedStrategyRun(BaseModel):
    strategy_id: int
    inputs: Dict[str, Any]
    binance_symbol: str
    interval: str
    end: datetime