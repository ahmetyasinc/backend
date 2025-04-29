from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from app.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String(50), nullable=False)
    api_name = Column(String(100), nullable=False)
    api_key = Column(Text, nullable=False)
    api_secret = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
