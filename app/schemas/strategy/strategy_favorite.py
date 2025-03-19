from pydantic import BaseModel

class StrategyFavoriteCreate(BaseModel):
    strategy_id: int

