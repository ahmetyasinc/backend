from sqlalchemy import select
import asyncpg
import asyncio
import time
import threading
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.profile.binance_coins import BinanceCoin
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
    symbols: List[str]
    intervals: List[str]

# ✅ Binance'den veri indirme ve kaydetme endpoint'i
@websocket_router.get("/api/download-binance-data/")
async def get_trades(data: DownloadData, db: AsyncSession = Depends(get_db)):
    """Binance'den belirtilen interval'lerde veri çekip veritabanına kaydeder."""
    results = []

    for symbol in data.symbols:
        for interval in data.intervals:
            candles = get_binance_data(symbol=symbol, interval=interval)

            if not candles:
                results.append({"interval": interval, "status": "error", "message": "Binance API'den veri alınamadı."})
                continue

            save_result = await save_binance_data(db, symbol, interval, candles)
            results.append({"interval": interval, "status": "success", "details": save_result})
            print(f"✅ {symbol} için {interval} interval'inde veri kaydedildi.")

    return {"symbol": symbol, "results": results}


@websocket_router.post("/api/download-all-binance-data/")
async def get_all_binance_data(intervals: List[str], db: AsyncSession = Depends(get_db)):
    """Binance_coins tablosundaki tüm coinler için belirtilen interval'lerde veri çeker ve kaydeder."""
    results = []
    try:
        # ORM objelerini çektikten sonra dict'e dönüştürüyoruz
        result = await db.execute(select(BinanceCoin))
        coins = result.scalars().all()
        coin_list = [{"symbol": coin.symbol, "binance_symbol": coin.binance_symbol} for coin in coins]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veritabanı hatası: {e}")

    if not coin_list:
        raise HTTPException(status_code=404, detail="Veritabanında coin bulunamadı!")

    total_tasks = len(coin_list) * len(intervals)
    current_task = 1  # İşlem sayacını başlat

    for coin_index, coin in enumerate(coin_list, start=1):
        symbol = coin["binance_symbol"]
        for interval_index, interval in enumerate(intervals, start=1):
            try:
                candles = get_binance_data(symbol=symbol, interval=interval)

                if not candles:
                    results.append({
                        "symbol": symbol, 
                        "interval": interval, 
                        "status": "error", 
                        "message": "Binance API'den veri alınamadı."
                    })
                    print(f"[{current_task}/{total_tasks}] ❌ {symbol} {interval}: Veri alınamadı.")
                    current_task += 1
                    continue

                save_result = await save_binance_data(db, symbol, interval, candles)
                results.append({
                    "symbol": symbol, 
                    "interval": interval, 
                    "status": "success", 
                    "details": save_result
                })
                print(f"[{current_task}/{total_tasks}] ✅ {symbol} için {interval} interval'inde veri kaydedildi.")
            except Exception as e:
                results.append({
                    "symbol": symbol, 
                    "interval": interval, 
                    "status": "error", 
                    "message": str(e)
                })
                print(f"[{current_task}/{total_tasks}] ❌ Hata oluştu: {symbol}, Interval: {interval}, Hata: {e}")
            current_task += 1  # Her denemeden sonra artır

    return {"summary": results}

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