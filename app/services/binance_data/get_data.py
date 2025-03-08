import requests
import time

def get_binance_data(symbol: str, interval: str, total_limit: int = 5000):
    """Binance API üzerinden belirtilen symbol ve interval için total_limit kadar mum verisi çeker."""
    base_url = "https://api.binance.com/api/v3/klines"
    limit_per_request = 1000  # Binance her seferde en fazla 1000 mum döndürebiliyor
    collected_candles = []
    end_time = None  # İlk başta en güncel veriyi çekmek için None

    try:
        while len(collected_candles) < total_limit:
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit_per_request
            }
            if end_time:
                params["endTime"] = end_time  # Eski verileri çekmek için endTime kullan

            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            
            if not isinstance(data, list) or not data:
                raise ValueError(f"Geçersiz yanıt: {data}")

            candles = []
            for item in data:
                candles.append({
                    "open_time": item[0],  
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5])
                })

            collected_candles = candles + collected_candles

            # Eğer çekilen veri 1000'den azsa daha eski veri yoktur, döngüyü kır
            if len(candles) < limit_per_request:
                break

            # Son çekilen mumun açılış zamanını end_time olarak belirle
            end_time = candles[0]["open_time"] - 1  # Biraz geri alıyoruz, tekrar eden veri olmasın

            time.sleep(0.5)  # API isteğini sınırlamak için kısa bir bekleme ekliyoruz

        # Veriyi en eski mumdan en yeniye sıralıyoruz
        #collected_candles.reverse()
        return collected_candles[:total_limit]

    except requests.exceptions.RequestException as e:
        print(f"API Hatası: {e}")
        return None
    except (ValueError, IndexError) as e:
        print(f"Veri Hatası: {e}")
        return None
