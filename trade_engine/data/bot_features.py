import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def load_bot_holding(bot_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT user_id, bot_id, symbol, percentage
            FROM bot_holdings
            WHERE bot_id = %s;
        """, (bot_id,))

        holdings = cursor.fetchall()

        cursor.close()
        conn.close()

        return holdings

    except Exception as e:
        print(f"Veritabanı hatası (bot_holdings): {e}")
        return []

def load_bot_positions(bot_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT symbol, side, leverage, amount, percentage
            FROM bot_positions
            WHERE bot_id = %s AND state = 1;
        """, (bot_id,))

        positions = cursor.fetchall()
        cursor.close()
        conn.close()

        return positions

    except Exception as e:
        print(f"Veritabanı hatası (bot_positions): {e}")
        return []
    
def load_bot_value(bot_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT current_usd_value
            FROM bots
            WHERE id = %s;
        """, (bot_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return float(result['current_usd_value'])
        else:
            return 0.0  # veya None

    except Exception as e:
        print(f"Veritabanı hatası (bots): {e}")
        return 0.0
