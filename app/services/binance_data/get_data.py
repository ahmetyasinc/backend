import requests
import time

def get_binance_data(symbol: str, interval: str, total_limit: int = 5000, retry_limit: int = 3):
    """Binance API üzerinden belirtilen symbol ve interval için total_limit kadar mum verisi çeker."""
    base_url = "https://api.binance.com/api/v3/klines"
    limit_per_request = 1000
    collected_candles = []
    end_time = None

    try:
        while len(collected_candles) < total_limit:
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit_per_request
            }
            if end_time:
                params["endTime"] = end_time

            for attempt in range(retry_limit):
                try:
                    response = requests.get(base_url, params=params, timeout=10)
                    response.raise_for_status()
                    break  # Başarılı ise döngüden çık
                except requests.exceptions.RequestException as e:
                    print(f"API Hatası: {e}, Deneme: {attempt + 1}/{retry_limit}")
                    time.sleep(2)  # Hatalı istekten sonra biraz bekle
            else:
                print(f"❌ {symbol} için API isteği başarısız. Atlanıyor...")
                return None

            data = response.json()
            
            if not isinstance(data, list) or not data:
                print(f"⚠️ {symbol} için geçersiz yanıt: {data}")
                break

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

            collected_candles = candles + collected_candles  # Eski verileri üste ekliyoruz

            print(f"✅ {symbol} | {interval} | Toplam veri: {len(collected_candles)}")

            if len(candles) < limit_per_request:
                break  # Daha fazla veri yok

            end_time = candles[0]["open_time"] - 1  # Geri çek, çakışmayı önle
            time.sleep(0.3)  # Daha az bekleme süresi, güvenli limitte

        return collected_candles[:total_limit]

    except (ValueError, IndexError) as e:
        print(f"Veri Hatası: {e}")
        return None
