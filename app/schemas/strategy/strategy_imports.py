from pydantic import BaseModel
from typing import List

class StrategyIndicatorUpdate(BaseModel):
    id: int
    indicator_names: List[str]  # isim listesi gelecek
