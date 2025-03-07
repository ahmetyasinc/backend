import requests

def get_binance_data(symbol: str, interval: str):
    """Binance API üzerinden belirtilen symbol ve period için maksimum 500 mum verisi çeker."""
    base_url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": 500  # Binance en fazla 500 mum verisi döndürebiliyor
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()  # HTTP hatalarını yakala
        
        data = response.json()
        
        if not isinstance(data, list):
            raise ValueError(f"Geçersiz yanıt: {data}")
        
        candles = []
        for item in data:
            candles.append({
                "open_time": item[0],  # Açılış zamanı (timestamp)
                "open": float(item[1]),  # Açılış fiyatı
                "high": float(item[2]),  # En yüksek fiyat
                "low": float(item[3]),   # En düşük fiyat
                "close": float(item[4]), # Kapanış fiyatı
                "volume": float(item[5]) # Hacim
            })
        
        return candles
    
    except requests.exceptions.RequestException as e:
        print(f"API Hatası: {e}")
        return None
    except (ValueError, IndexError) as e:
        print(f"Veri Hatası: {e}")
        return None