from pydantic import BaseModel, Field
from typing import List

class StrategyScanRequest(BaseModel):
    strategy_id: int = Field(..., description="ID of the strategy to scan with")
    symbols: List[str] = Field(..., description="List of symbols to scan (e.g., ['BTCUSDT', 'ETHUSDT'])")
    interval: str = Field(..., description="Time interval for the candles (e.g., '1m', '5m', '1h')")
    candles: int = Field(..., gt=0, description="Number of candles to fetch for each symbol")
