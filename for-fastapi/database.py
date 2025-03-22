from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 📌 Asenkron veritabanı URL'si (PostgreSQL için)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# 📌 Asenkron Engine oluştur
async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)

# 📌 Asenkron Session Factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# 📌 Asenkron DB bağlantısı yöneticisi
async def get_db():
    """Asenkron veritabanı bağlantısını aç ve güvenli bir şekilde kapat"""
    async with AsyncSessionLocal() as db:
        yield db  # Bağlantıyı çağırana ver
