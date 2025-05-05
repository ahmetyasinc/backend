from trade_engine.config import engine

def load_strategy_code(strategy_id: int) -> str | None:
    try:
        conn = engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM strategies WHERE id = %s", (strategy_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None
