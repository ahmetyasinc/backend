from sqlalchemy import text
from trade_engine.config import engine

def load_indicators(strategy_id):
    try:
        with engine.connect() as conn:
            # strategy_id'ye göre indicator_ids çek
            result = conn.execute(
                text("SELECT indicator_ids FROM strategies WHERE id = :strategy_id"),
                {"strategy_id": strategy_id}
            ).fetchone()

            if not result:
                return []

            indicator_ids = result._mapping['indicator_ids']

            if not indicator_ids:
                return []

            # ARRAY ise direkt kullan, değilse string olarak parse et
            if isinstance(indicator_ids, str):
                indicator_ids = [int(id.strip()) for id in indicator_ids.split(',')]

            # Şimdi indicators tablosundan verileri çek
            indicators_result = conn.execute(
                text("SELECT id, name, code FROM indicators WHERE id = ANY(:indicator_ids)"),
                {"indicator_ids": indicator_ids}
            ).fetchall()

            # SQLAlchemy Row nesnelerini dict'e çevir
            indicators = [dict(row._mapping) for row in indicators_result]

            return indicators

    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return []
