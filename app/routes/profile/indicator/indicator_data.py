from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.database import get_db


protected_router = APIRouter()

@protected_router.get("/api/get-binance-data/")
async def get_binance_data(symbol: str, interval: str, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    """Veritabanından belirtilen sembol ve zaman aralığındaki son 1000 veriyi JSON olarak getirir."""
    print(user_id + " kullanıcısı veri sorguluyor...")
    query = text("""
        SELECT jsonb_agg(jsonb_build_object(
            'timestamp', timestamp,
            'open', open,
            'high', high,
            'low', low,
            'close', close,
            'volume', volume
        )) AS data
        FROM (
            SELECT timestamp, open, high, low, close, volume
            FROM public.binance_data
            WHERE coin_id = :symbol 
              AND interval = :interval
            ORDER BY timestamp ASC
        ) t;
    """)

    result = await db.execute(query, {"symbol": symbol, "interval": interval})
    json_data = result.fetchone()[0]  # ✅ Fazladan listeyi kaldır

    # Eğer veri None (boş) gelirse, boş bir liste döndür
    if json_data is None:
        json_data = []

    return {"status": "success", "data": json_data}

