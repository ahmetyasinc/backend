import asyncpg
import asyncio
import time
import threading

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.services.binance_data.manage_data import binance_websocket
from app.services.binance_data.save_data import save_binance_data
from app.services.binance_data.get_data import get_binance_data

websocket_router = APIRouter()

# Veritabanı bağlantısı için global değişken
db_pool = None  
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/balina_db"

# WebSocket ve Startup için kontrol değişkenleri
startup_lock = threading.Lock()
startup_called = False
websocket_task = None  # WebSocket görevini yönetmek için

class DownloadData(BaseModel):
    symbol: str
    interval: str

# ✅ Binance'den veri indirme ve kaydetme endpoint'i
@websocket_router.get("/api/download-binance-data/")
async def get_trades(data: DownloadData, db: AsyncSession = Depends(get_db)):
    """Binance'den 5000 mumluk veri çekip veritabanına kaydeder."""
    candles = get_binance_data(symbol=data.symbol, interval=data.interval)

    if not candles:
        return {"error": "Binance API'den veri alınamadı."}

    result = await save_binance_data(db, data.symbol, data.interval, candles)
    return result

# ✅ FastAPI başlatıldığında WebSocket'i ve veritabanı bağlantısını başlat
@websocket_router.on_event("startup")
async def startup():
    """Uygulama başladığında veritabanı bağlantı havuzunu oluştur ve WebSocket başlat."""
    global db_pool, startup_called, websocket_task

    with startup_lock:
        if startup_called:  
            print("🚫 Startup zaten çalıştırılmış, tekrar başlatılmıyor.")
            return
        startup_called = True  # Bir daha çalışmasını engelle

    print(f"🌐 WebSocket başlatılıyor... {time.time()}")

    db_pool = await asyncpg.create_pool(DATABASE_URL)

    # WebSocket'i çalıştır ve görevi sakla
    websocket_task = asyncio.create_task(run_websocket_with_reconnect())

# ✅ FastAPI kapandığında temizleme işlemleri
@websocket_router.on_event("shutdown")
async def shutdown():
    """Uygulama kapanırken WebSocket'i ve veritabanı bağlantısını kapat."""
    global db_pool, websocket_task

    if websocket_task:
        websocket_task.cancel()  # WebSocket görevini durdur
        websocket_task = None

    if db_pool:
        await db_pool.close()

# ✅ WebSocket Bağlantısını Yönet (Koparsa Yeniden Bağlan)
async def run_websocket_with_reconnect():
    """ WebSocket bağlantısı koparsa otomatik olarak tekrar bağlan """
    while True:
        try:
            print(f"🌐 * WebSocket başlatılıyor... {time.time()}")
            await binance_websocket(db_pool)
        except Exception as e:
            print(f"❌ WebSocket bağlantısı kesildi: {e}")
            print("⏳ 5 saniye sonra tekrar bağlanıyor...")
            await asyncio.sleep(5)  # 5 saniye bekleyip tekrar bağlan
