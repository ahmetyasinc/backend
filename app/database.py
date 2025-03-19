from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os, asyncio
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Asenkron PostgreSQL bağlantı URL'si
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:admin@localhost:5432/balina_db")

# Asenkron SQLAlchemy engine oluştur
engine = create_async_engine(DATABASE_URL, echo=False) # echo=True olursa SQL sorgularını görebilirsin

# Asenkron veritabanı oturumu (session) oluşturucu
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# SQLAlchemy Base Modeli
Base = declarative_base()

# Veritabanı bağlantısını sağlayan asenkron fonksiyon
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def test_db():
    async with engine.begin() as conn:
        print("✅ Veritabanı bağlantısı başarılı!")

# asyncio.run(test_db())
