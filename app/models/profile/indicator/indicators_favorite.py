from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class IndicatorsFavorite(Base):
    __tablename__ = "indicators_favorite"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # İlişkiler
    user = relationship("User", back_populates="favorite_indicators")
    indicator = relationship("Indicator", back_populates="favorited_by_users")
