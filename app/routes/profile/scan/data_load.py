import pandas as pd
from trade_engine.config import engine

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