import asyncio
from database import engine, Base

# Tabloları oluştur
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
