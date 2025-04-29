import asyncio
import sys

# Windows uyumluluğu için event loop policy ayarı
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import psycopg
from process.trade_engine import run_trade_engine
from process.process import run_all_bots_async


# Çakışmaları önlemek için lock
lock = asyncio.Lock()

# Botları çalıştır
async def handle_new_data():
    if lock.locked():
        print("Botlar zaten çalışıyor. Yeni tetikleme bekliyor...")
        return

    async with lock:
        print("Yeni veri geldi. Botlar çalıştırılıyor...")
        strategies_with_indicators, coin_data_dict, bots = run_trade_engine()
        await run_all_bots_async(bots, strategies_with_indicators, coin_data_dict)

# PostgreSQL tetikleyicisini dinle
async def listen_for_notifications():
    conn_str = "postgresql://postgres:admin@localhost/balina_db"
    async with await psycopg.AsyncConnection.connect(conn_str, autocommit=True) as conn:
        async with conn.cursor() as cur:
            await cur.execute("LISTEN new_data;")
            print("PostgreSQL'den tetikleme bekleniyor (kanal: new_data)...")

            async for notify in conn.notifies():
                print(f"Gelen tetikleme: {notify.payload}")
                await handle_new_data()




# Ana çalıştırıcı
if __name__ == "__main__":
    asyncio.run(listen_for_notifications())
