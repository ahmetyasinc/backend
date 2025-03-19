import numpy as np
import pandas as pd

def plot(strategy_name, strategy_results, df):
    """
    Kullanıcının trade stratejisini analiz eden ve işlemleri belirleyen fonksiyon.
    """
    if 'position' not in df.columns:
        raise ValueError("DataFrame içinde 'position' sütunu bulunmalıdır!")

    # Eğer indeks datetime değilse, timestamp sütununu datetime'a çevir
    if not np.issubdtype(df.index.dtype, np.datetime64):
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        else:
            raise ValueError("DataFrame içinde 'timestamp' sütunu bulunmalı veya indeks datetime olmalı!")

    # **Zaman Damgasına Göre Sıralama** (🚀 Hızlı ve stabil sıralama)
    df = df.sort_values(by="timestamp", ascending=True)

    df['position_prev'] = df['position'].shift()
    
    # Pozisyon değişiklikleri için maskeleri oluştur
    long_open_mask = (df['position_prev'].le(0)) & (df['position'].gt(0))
    long_close_mask = (df['position_prev'].gt(0)) & (df['position'].le(0))
    short_open_mask = (df['position_prev'].ge(0)) & (df['position'].lt(0))
    short_close_mask = (df['position_prev'].lt(0)) & (df['position'].ge(0))

    # **Trade olaylarını listeye ekle (sıralı)**
    events = []
    
    for mask, event_name in zip([long_open_mask, long_close_mask, short_open_mask, short_close_mask],
                                ["Long Aç", "Long Kapat", "Short Aç", "Short Kapat"]):
        indices = np.where(mask)[0]
        if len(indices) > 0:
            timestamps = df['timestamp'].iloc[indices].dt.strftime('%Y-%m-%dT%H:%M:%S')  # ✅ Yeni Yöntem
            sizes = np.abs(df['position'].iloc[indices].values)  # Short pozisyonları pozitife çevir
            events.extend(zip(timestamps, [event_name] * len(indices), sizes))

    # **Final Listeyi Sıralama Garanti (Gerekmez Ama Emin Olmak İçin)**
    events.sort(key=lambda x: x[0])  # Zaten sıralı, ancak ekstra güvenlik için

    # DataFrame dönüşümü yerine doğrudan liste ile ekleme
    strategy_results.append({
        "name": strategy_name,
        "type": "events",
        "data": events  # ✅ `isoformat()` yerine doğrudan `strftime()` ile dönüşüm yapıldı.
    })
