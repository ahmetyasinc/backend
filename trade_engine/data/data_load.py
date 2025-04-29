import pandas as pd
from config import engine  # engine doğrudan config.py'den geliyor
import asyncio
import time

async def fetch_all_candles(coin_requirements):
    semaphore = asyncio.Semaphore(15)  # Aynı anda max 15 tane çekilsin

    async def fetch_one(key, candle_count):
        coin_id, interval = key
        async with semaphore:
            #t0 = time.time()
            df = await get_candles_async(coin_id, interval, candle_count)
            #duration = time.time() - t0
            #print(f"⏱️ {coin_id}-{interval}: {duration:.2f} saniye")
            return key, df

    tasks = [fetch_one(key, count) for key, count in coin_requirements.items()]
    results = await asyncio.gather(*tasks)

    coin_data_dict = {}
    for (coin_id, interval), df in results:
        if len(df) >= coin_requirements[(coin_id, interval)]:
            coin_data_dict[(coin_id, interval)] = df
        else:
            #print(f"⚠️ Atlandı: coin_id={coin_id}, interval={interval} – Yeterli veri yok ({len(df)}/{coin_requirements[(coin_id, interval)]})")
            pass

    return coin_data_dict


async def get_candles_async(coin_id, interval, candle_count):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_candles, coin_id, interval, candle_count)

def get_candles(coin_id, interval, candle_count):
    query = """
        SELECT timestamp, open, high, low, close, volume
        FROM binance_data
        WHERE coin_id = %s AND interval = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    try:
        df = pd.read_sql_query(query, engine, params=(coin_id, interval, candle_count))
        df = df.sort_values(by='timestamp')
        return df
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return pd.DataFrame()
