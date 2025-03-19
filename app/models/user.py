from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, func, Enum
from sqlalchemy.orm import relationship, deferred
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)

    # Kullanıcı bilgileri
    username = Column(String(50), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # Profil bilgileri
    phone = Column(String(20), unique=True, nullable=True)  # Telefon numarası (isteğe bağlı)
    profile_picture = Column(String(255), nullable=True)  # Profil fotoğrafı URL
    bio = Column(String(500), nullable=True)  # Kullanıcı hakkında kısa biyografi
    location = Column(String(255), nullable=True)  # Şehir, ülke bilgisi
    
    # Yetki ve Durum
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)  # Kullanıcı rolü
    is_active = Column(Boolean, default=True)  # Kullanıcı aktif mi?
    is_verified = Column(Boolean, default=False)  # Kullanıcı e-posta veya telefonunu doğruladı mı?

    # Zaman damgaları
    created_at = Column(DateTime, default=func.now())  # Hesap oluşturulma tarihi
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Son güncelleme

    # RELOTIONSHIP - MODELLERİ STRING OLARAK TANIMLADIK
    pinned_coins = relationship("BinanceCoinsPinned", back_populates="user", cascade="all, delete-orphan")
    favorite_indicators = relationship("IndicatorsFavorite", back_populates="user", cascade="all, delete-orphan")
    favorite_strategies = relationship("StrategiesFavorite", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email}, role={self.role})>"
