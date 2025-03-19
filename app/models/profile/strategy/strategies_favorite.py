from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class StrategiesFavorite(Base):
    __tablename__ = "strategies_favorite"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # İlişkiler
    user = relationship("User", back_populates="favorite_strategies")
    strategy = relationship("Strategy", back_populates="favorited_by_users")
