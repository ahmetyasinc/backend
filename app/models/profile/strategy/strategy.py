from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, Boolean
from sqlalchemy.orm import relationship, deferred
from app.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(Text, nullable=False)
    public = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    

    # RELOTIONSHIP
    favorited_by_users = relationship("StrategiesFavorite", back_populates="strategy", cascade="all, delete-orphan")