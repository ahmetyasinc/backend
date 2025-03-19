def interval_to_minutes(interval: str) -> int:
    """Binance interval değerini dakika cinsine çevirir."""
    interval_mapping = {
        "1m": 1,
        "3m": 3,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "2h": 120,
        "4h": 240,
        "1d": 1440,
        "1w": 10080
    }
    
    return interval_mapping.get(interval, -1)  # Geçersiz interval için -1 döndür
