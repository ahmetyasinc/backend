from datetime import datetime, timedelta
import aiohttp
import asyncio
import asyncio
import websockets
import json

from app.services.binance_data.interval_maping import interval_to_minutes

# ✅ 4️⃣ Binance WebSocket Bağlantısı
async def binance_websocket(db_pool):
    """ Binance WebSocket'ten 1 dakikalık ve 3 dakikalık Bitcoin mumlarını dinle ve veritabanına kaydet """
    
    # ✅ WebSocket için çoklu abonelik JSON formatında hazırlanıyor
    uri = "wss://stream.binance.com:9443/ws"
    payload = {
    "method": "SUBSCRIBE",
    "params": [
        "btcusdt@kline_1m",   # 1 dakika
        "btcusdt@kline_3m",   # 3 dakika
        "btcusdt@kline_5m",   # 5 dakika
        "btcusdt@kline_15m",  # 15 dakika
        "btcusdt@kline_30m",  # 30 dakika
        "btcusdt@kline_1h",   # 1 saat
        "btcusdt@kline_2h",   # 2 saat
        "btcusdt@kline_4h",   # 4 saat
        "btcusdt@kline_1d",   # 1 gün
        "btcusdt@kline_1w",   # 1 hafta
#
        #"ethusdt@kline_1m",   # 1 dakika
        #"ethusdt@kline_3m",   # 3 dakika
        #"ethusdt@kline_5m",   # 5 dakika
        #"ethusdt@kline_15m",  # 15 dakika
        #"ethusdt@kline_30m",  # 30 dakika
        #"ethusdt@kline_1h",   # 1 saat
        #"ethusdt@kline_2h",   # 2 saat
        #"ethusdt@kline_4h",   # 4 saat
        #"ethusdt@kline_1d",   # 1 gün
        #"ethusdt@kline_1w",   # 1 hafta
#
        #"bnbusdt@kline_1m",   # 1 dakika
        #"bnbusdt@kline_3m",   # 3 dakika
        #"bnbusdt@kline_5m",   # 5 dakika
        #"bnbusdt@kline_15m",  # 15 dakika
        #"bnbusdt@kline_30m",  # 30 dakika
        #"bnbusdt@kline_1h",   # 1 saat
        #"bnbusdt@kline_2h",   # 2 saat
        #"bnbusdt@kline_4h",   # 4 saat
        #"bnbusdt@kline_1d",   # 1 gün
        #"bnbusdt@kline_1w",   # 1 hafta
#
        #"solusdt@kline_1m",   # 1 dakika
        #"solusdt@kline_3m",   # 3 dakika
        #"solusdt@kline_5m",   # 5 dakika
        #"solusdt@kline_15m",  # 15 dakika
        #"solusdt@kline_30m",  # 30 dakika
        #"solusdt@kline_1h",   # 1 saat
        #"solusdt@kline_2h",   # 2 saat
        #"solusdt@kline_4h",   # 4 saat
        #"solusdt@kline_1d",   # 1 gün
        #"solusdt@kline_1w",   # 1 hafta
#
        #"adausdt@kline_1m",   # 1 dakika
        #"adausdt@kline_3m",   # 3 dakika
        #"adausdt@kline_5m",   # 5 dakika
        #"adausdt@kline_15m",  # 15 dakika
        #"adausdt@kline_30m",  # 30 dakika
        #"adausdt@kline_1h",   # 1 saat
        #"adausdt@kline_2h",   # 2 saat
        #"adausdt@kline_4h",   # 4 saat
        #"adausdt@kline_1d",   # 1 gün
        #"adausdt@kline_1w",   # 1 hafta
    ],
    "id": 1
}

    async with websockets.connect(uri, ping_interval=10) as websocket:
        print("✅ WebSocket bağlantısı kuruldu.")
        
        # 🔥 WebSocket'e çoklu abonelik isteği gönder
        await websocket.send(json.dumps(payload))

        while True:
            try:
                data = await websocket.recv()
                json_data = json.loads(data)

                # Eğer mesaj "kline" içeriyorsa işlem yap
                if "k" in json_data:
                    kline = json_data["k"]
                    is_closed = kline["x"]  # Mum kapanmış mı?
                    interval = kline["i"]   # Zaman aralığı ("1m", "2m")
                    coin_id = kline["s"].upper()  # Coin ID ("BTCUSDT", "ETHUSDT")
                    
                    if is_closed:  # Eğer mum kapanmışsa kaydet
                        timestamp = datetime.utcfromtimestamp(kline["t"] / 1000)
                        open_price = float(kline["o"])
                        high_price = float(kline["h"])
                        low_price = float(kline["l"])
                        close_price = float(kline["c"])
                        volume = float(kline["v"])

                        # ✅ 5️⃣ Veriyi veritabanına kaydet
                        async with db_pool.acquire() as conn:

                            await fill_data_from_binance(conn, coin_id, interval, timestamp)

                            await conn.execute(
                                """
                                INSERT INTO binance_data (coin_id, interval, timestamp, open, high, low, close, volume)
                                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                                ON CONFLICT (coin_id, interval, timestamp) DO NOTHING
                                """,
                                coin_id, interval, timestamp, open_price, high_price, low_price, close_price, volume
                            )

                            # ✅ Eski verileri temizle (5000 kayıt üstü sil)
                            await conn.execute(
                                """
                                DELETE FROM binance_data 
                                WHERE id IN (
                                    SELECT id FROM binance_data 
                                    WHERE coin_id = $1 AND interval = $2
                                    ORDER BY timestamp ASC
                                    LIMIT GREATEST(0, (SELECT COUNT(*) FROM binance_data WHERE coin_id = $1 AND interval = $2) - 5000)
                                );
                                """,
                                coin_id, interval
                            )

                        print(f"✅ New Data: {interval} - {coin_id} - {timestamp}")

            except websockets.exceptions.ConnectionClosed:
                print("❌ WebSocket bağlantısı kapandı. Yeniden bağlanıyor...")
                break  # Döngüden çıkıp tekrar bağlanmasını sağla

            except Exception as e:
                print(f"⚠ Hata oluştu: {e}")
                await asyncio.sleep(5)  # Küçük bir gecikme ile tekrar dene

async def fill_data_from_binance(conn, coin_id, interval, latest_timestamp):
    """
    Eğer eksik veri varsa, Binance REST API'den çekerek aradaki tüm boşlukları tamamla.
    """
    interval_minutes = interval_to_minutes(interval)

    # 🔹 Önce en son kaydedilen veriyi al
    last_timestamp = await conn.fetchval(
        """
        SELECT timestamp FROM binance_data
        WHERE coin_id = $1 AND interval = $2
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        coin_id, interval
    )

    if last_timestamp is None:
        print(f"⚠ Veritabanında hiç veri yok, eksik veri çekilemiyor.")
        return 404

    # 🔹 Eğer son kaydedilen veri ile yeni gelen veri arasında boşluk varsa
    if last_timestamp < latest_timestamp - timedelta(minutes=interval_minutes):
        print(f"⚠ {coin_id} {interval} için eksik veri tespit edildi: {last_timestamp} - {latest_timestamp}, Binance'den çekiliyor...")

        # 🔹 Binance API'den eksik verileri al
        missing_data = await fetch_missing_data(coin_id, interval, last_timestamp + timedelta(minutes=1), latest_timestamp)

        if missing_data:
            insert_queries = []
            for kline in missing_data:
                ts = datetime.utcfromtimestamp(kline[0] / 1000) + timedelta(hours=3)
                open_price, high_price, low_price, close_price, volume = map(float, kline[1:6])

                insert_queries.append((coin_id, interval, ts, open_price, high_price, low_price, close_price, volume))        

            for query in insert_queries:
                await conn.execute(
                    """
                    INSERT INTO binance_data (coin_id, interval, timestamp, open, high, low, close, volume)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (coin_id, interval, timestamp) DO NOTHING
                    """,
                    *query
                )

            print(f"✅ {coin_id} - {interval} için eksik veriler tamamlandı ({len(insert_queries)} adet mum eklendi).")

async def fetch_missing_data(coin_id, interval, start_time, end_time):
    """
    Binance REST API kullanarak eksik mum verilerini getir.
    """
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": coin_id,
        "interval": interval,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000),
        "limit": 1000
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"❌ Binance API hatası: {response.status}")
                return []