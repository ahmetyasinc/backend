from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class IndicatorCreate(BaseModel):
    name: str
    code: str

class IndicatorUpdate(BaseModel):
    id: int
    name: str
    code: str

class IndicatorRun(BaseModel):
    indicator_id: int
    binance_symbol: str
    interval: str
    end: datetime

class UpdatedIndicatorRun(BaseModel):
    indicator_id: int
    inputs: Dict[str, Any]
    binance_symbol: str
    interval: str
    end: datetime