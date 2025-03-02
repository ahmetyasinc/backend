from sqlalchemy import Column, BigInteger, String, DateTime, func
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

