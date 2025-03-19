from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class BinanceCoinsPinned(Base):
    __tablename__ = "binance_coins_pinned"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id = Column(Integer, ForeignKey("binance_coins.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # RELOTIONSHIP
    user = relationship("User", back_populates="pinned_coins")
    coin = relationship("BinanceCoin", back_populates="pinned_by_users")