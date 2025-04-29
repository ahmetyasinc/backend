from sqlalchemy import text
from config import engine

def load_strategy(id):
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT code FROM strategies WHERE id = :id"),
                {"id": id}
            ).scalar()  # sadece 'code' değerini alır

            return result  # direkt string veya None

    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return None
