from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.models.profile.binance_data import BinanceData
from app.models.profile.indicator.indicator import Indicator
from sqlalchemy.future import select
from app.database import get_db
from app.routes.profile.indicator.run_user_indicator import run_user_indicator
from app.schemas.indicator.indicator import IndicatorRun
from sqlalchemy import text
import time


protected_router = APIRouter()

@protected_router.post("/api/run-indicator/")
async def run_indicator(
    indicator_data: IndicatorRun,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Gönderilen coin_id, interval ve end değerlerine göre binance_data tablosundan veri çeker, indikatörü doğrular ve çalıştırır."""

    start_time = time.time()  # Fonksiyon başlangıcındaki zaman damgası


    # **1️⃣ BinanceData tablosundan son 1000 veriyi çek**
    query = (
        select(BinanceData)
        .where(
            BinanceData.coin_id == indicator_data.binance_symbol,  # Hatalı sütun ismi düzeltildi
            BinanceData.interval == indicator_data.interval,
            BinanceData.timestamp <= indicator_data.end
        )
        .order_by(BinanceData.timestamp.desc())
        .limit(1000)
    )

    result = await db.execute(query)


    query = text("""
        SELECT * FROM (
            SELECT * FROM public.binance_data
            WHERE coin_id = :coin_id
            AND "interval" = :interval
            AND timestamp <= :end_time
            ORDER BY timestamp DESC
            LIMIT 1000
        ) AS subquery
        ORDER BY timestamp ASC;
    """)

    result = await db.execute(query, {
        "coin_id": indicator_data.binance_symbol,
        "interval": indicator_data.interval,
        "end_time": indicator_data.end
    })
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No data found for the given parameters.")

    # **2️⃣ Indicator tablosundan kullanıcı indikatörünü al**
    indicator_query = (
        select(Indicator)
        .where(Indicator.id == indicator_data.indicator_id)
    )

    indicator_result = await db.execute(indicator_query)
    indicator = indicator_result.scalars().first()

    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found.")

    # **3️⃣ Kullanıcı yetkisini doğrula**
    if indicator.user_id != int(user_id) and not indicator.public and not indicator.tecnic:
        raise HTTPException(status_code=403, detail="You are not authorized to access this indicator.")

    # **4️⃣ Çekilen veriyi JSON formatına çevir**
    historical_data = [
        {
            "timestamp": row.timestamp,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
        }
        for row in rows
    ]

    # **5️⃣ Kullanıcının indikatör kodunu çalıştır**
    indicator_result, print_outputs = await run_user_indicator(indicator.code, historical_data)

    end_time = time.time()  # Fonksiyon bitişindeki zaman damgası
    execution_time = end_time - start_time  # Çalışma süresi hesaplanıyor

    return {"indicator_id": indicator.id, "execution_time": execution_time, "indicator_result": indicator_result, "prints": print_outputs}