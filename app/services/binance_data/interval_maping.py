def interval_to_minutes(interval: str) -> int:
    """Binance interval değerini dakika cinsine çevirir."""
    interval_mapping = {
        "1m": 1,
        "3m": 3,
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "4h": 240,
        "1d": 1440
    }
    
    return interval_mapping.get(interval, -1)  # Geçersiz interval için -1 döndür
