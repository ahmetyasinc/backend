from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func, UniqueConstraint
from app.database import Base

class BinanceData(Base):
    __tablename__ = "main_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    symbol = Column(String(20), nullable=False)
    interval = Column(String(10), nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "symbol", "interval", name="unique_user_symbol_interval"),)