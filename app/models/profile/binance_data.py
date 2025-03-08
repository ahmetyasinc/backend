from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func, UniqueConstraint, DECIMAL
from app.database import Base

class BinanceData(Base):
    __tablename__ = "BinanceData"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(50), nullable=False)
    interval = Column(String(10), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    open = Column(DECIMAL(18, 8), nullable=False)
    high = Column(DECIMAL(18, 8), nullable=False)
    low = Column(DECIMAL(18, 8), nullable=False)
    close = Column(DECIMAL(18, 8), nullable=False)
    volume = Column(DECIMAL(18, 8), nullable=False)

    __table_args__ = (UniqueConstraint("coin_id", "interval", "timestamp", name="unique_candlestick"),)

