from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from datetime import datetime
import pytz

async def save_binance_data(db: AsyncSession, symbol: str, interval: str, candles: list):
    """Binance'den çekilen verileri candlestick_data tablosuna ekler."""
    if not candles:
        return {"message": "No data to insert."}

    try:
        query = text("""
            INSERT INTO binance_data (coin_id, interval, timestamp, open, high, low, close, volume)
            VALUES (:coin_id, :interval, :timestamp, :open, :high, :low, :close, :volume)
            ON CONFLICT (coin_id, interval, timestamp) DO NOTHING
        """)

        for candle in candles:
            timestamp = datetime.utcfromtimestamp(candle["open_time"] / 1000)
            params = {
                "coin_id": symbol,
                "interval": interval,
                "timestamp": timestamp,
                "open": candle["open"],
                "high": candle["high"],
                "low": candle["low"],
                "close": candle["close"],
                "volume": candle["volume"],
            }
            await db.execute(query, params)

        await db.commit()
        return {"message": f"{len(candles)} data inserted successfully."}

    except Exception as e:
        await db.rollback()
        return {"error": str(e)}
