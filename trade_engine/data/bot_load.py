import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def load_active_bots():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Daha spesifik sütun seçimi (isteğe bağlı)
        cursor.execute("""
            SELECT id, user_id, strategy_id, api_id, period, stocks, active, candle_count
            FROM bots
            WHERE active = TRUE;
        """)
        bots = cursor.fetchall()

        cursor.close()
        conn.close()

        for bot in bots:
            if isinstance(bot['stocks'], str):
                bot['stocks'] = bot['stocks'].strip('{}').split(',')

        return bots

    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return []
