import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def load_active_bots(interval):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, user_id, strategy_id, api_id, period, stocks, active, candle_count
            FROM bots
            WHERE active = TRUE AND period = %s;
        """, (interval,))  # Parametre güvenli şekilde eklendi

        bots = cursor.fetchall()

        cursor.close()
        conn.close()

        # Eğer stocks alanı string olarak tutuluyorsa listeye çevir
        for bot in bots:
            if isinstance(bot['stocks'], str):
                bot['stocks'] = bot['stocks'].strip('{}').split(',')

        return bots

    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return []

