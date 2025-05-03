import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def load_last_data(interval):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # İstediğimiz veriyi çekiyoruz
        query = """
            SELECT timestamp
            FROM binance_data
            WHERE coin_id = 'BTCUSDT' AND interval = %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        cursor.execute(query, (interval,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result['timestamp']  # timestamp değerini döndür
        else:
            return None  # Eğer veri yoksa None döndür

    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return None
