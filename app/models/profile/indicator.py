from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from app.database import Base

class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
