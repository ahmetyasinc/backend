import asyncpg
import asyncio
import asyncpg
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.services.binance_data.manage_data import binance_websocket
from app.services.binance_data.save_data import save_binance_data
from app.services.binance_data.get_data import get_binance_data
from fastapi import APIRouter, Depends

router = APIRouter()

db_pool = None  # Global bağlantı havuzu
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/balina_db"

class download_data(BaseModel):
    symbol: str
    interval: str

class get_data(BaseModel):
    symbol: str
    interval: str


@router.post("/api/get-binance-data/")
async def get_trades(data: get_data, db: AsyncSession = Depends(get_db)):
    """Veritabanından belirtilen sembol ve zaman aralığındaki son 1000 veriyi JSON olarak getirir."""

    query = text("""
    SELECT json_agg(row_to_json(t))
    FROM (
        SELECT * 
        FROM public.binance_data
        WHERE coin_id = :symbol 
          AND interval = :interval
        ORDER BY timestamp ASC
    ) t
    """)


    result = await db.execute(query, {"symbol": data.symbol, "interval": data.interval})
    json_data = result.scalar()  # Tek bir JSON nesnesi döndürülecek

    return {"status": "success", "data": json_data}



# Binanceden veri indirime
@router.get("/api/download-binance-data/")
async def get_trades(data: download_data, db: AsyncSession = Depends(get_db)):
    """Binance'den 5000 mumluk veri çekip veritabanına kaydeder."""
    candles = get_binance_data(symbol=data.symbol, interval=data.interval)

    if not candles:
        return {"error": "Binance API'den veri alınamadı."}

    result = await save_binance_data(db, data.symbol, data.interval, candles)
    return result

# WEBSOCKET BAĞLANTILARI
startup_called = False
@router.on_event("startup")
async def startup():
    """Uygulama başladığında veritabanı bağlantı havuzunu oluştur"""
    global db_pool, startup_called

    if startup_called:  # Eğer zaten çalıştırılmışsa, tekrar başlatma
        return
    startup_called = True

    db_pool = await asyncpg.create_pool(DATABASE_URL)
    asyncio.create_task(run_websocket_with_reconnect())  # WebSocket görevini başlat

# FastAPI Kapanırken Veritabanı Bağlantısını Kapat
@router.on_event("shutdown")
async def shutdown():
    """Uygulama kapanırken veritabanı bağlantısını kapat"""
    print("🔌 Veritabanı bağlantısı kapatılıyor...")
    global db_pool
    if db_pool:
        await db_pool.close()

# WebSocket Bağlantısını Yönet (Koparsa Yeniden Bağlan)
async def run_websocket_with_reconnect():
    """ WebSocket bağlantısı koparsa otomatik olarak tekrar bağlan """
    while True:
        try:
            await binance_websocket(db_pool)
        except Exception as e:
            print(f"❌ WebSocket bağlantısı kesildi: {e}")
            print("⏳ 5 saniye sonra tekrar bağlanıyor...")
            await asyncio.sleep(5)  # 5 saniye bekleyip tekrar bağlan
    