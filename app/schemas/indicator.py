from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IndicatorCreate(BaseModel):
    name: str
    code: str
