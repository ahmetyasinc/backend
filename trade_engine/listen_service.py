import asyncio
import sys
import time
import psycopg

from data.last_data_load import load_last_data
from process.trade_engine import run_trade_engine
from process.process import run_all_bots_async

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

supported_intervals = [
    "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h",
    "6h", "8h", "12h", "1d", "3d", "1w", "1M"
]

interval_locks = {interval: asyncio.Lock() for interval in supported_intervals}
priority_interval = "1m"
priority_lock = asyncio.Lock()
queued_intervals = set()  # 🔐 Kuyrukta bekleyen interval'leri takip eder

async def handle_new_data(payload):
    interval = payload.strip()

    if interval not in interval_locks:
        print(f"⚠ Bilinmeyen interval: {interval}")
        return

    # Eğer zaten kuyruktaysa tekrar eklenmesin
    if interval in queued_intervals:
        print(f"🔁 {interval} zaten sırada bekliyor.")
        return

    queued_intervals.add(interval)

    # 1m için öncelikli kilit alınır
    if interval == priority_interval:
        if priority_lock.locked():
            print(f"❌❌❌ {interval} zaten çalışıyor.")
            queued_intervals.discard(interval)
            return
        async with priority_lock:
            await execute_bot_logic(interval)
    else:
        # 1m çalışıyorsa bekle
        while priority_lock.locked():
            print(f"⏸ {interval} için bekleniyor... (öncelikli {priority_interval} çalışıyor)")
            await asyncio.sleep(1)
        await execute_bot_logic(interval)

    # İş bittikten sonra sıradan çıkar
    queued_intervals.discard(interval)

async def execute_bot_logic(interval):
    lock = interval_locks[interval]

    if lock.locked():
        print(f"❌❌❌ {interval} zaten çalışıyor.")
        return

    async with lock:
        start_time = time.time()
        print(f"🚀 Yeni veri geldi. {interval} botları çalıştırılıyor...")

        try:
            last_time = load_last_data(interval)
            strategies_with_indicators, coin_data_dict, bots = await run_trade_engine(interval)

            if not strategies_with_indicators or not coin_data_dict or not bots:
                print(f"❌ {interval} için aktif bot bulunamadı.")
                return

            await run_all_bots_async(bots, strategies_with_indicators, coin_data_dict, last_time, interval)

            elapsed = time.time() - start_time
            print(f"✅ {last_time}, {interval} için botlar tamamlandı. Süre: {elapsed:.2f} saniye.")
        except Exception as e:
            print(f"❌ {interval} için bot çalıştırılırken hata: {e}")

async def listen_for_notifications():
    conn_str = "postgresql://postgres:admin@localhost/balina_db"
    async with await psycopg.AsyncConnection.connect(conn_str, autocommit=True) as conn:
        async with conn.cursor() as cur:
            await cur.execute("LISTEN new_data;")
            print("📡 PostgreSQL'den tetikleme bekleniyor...")

            async for notify in conn.notifies():
                print(f"🔔 Tetikleme: {notify.payload}")
                asyncio.create_task(handle_new_data(notify.payload))

if __name__ == "__main__":
    asyncio.run(listen_for_notifications())
