import numpy as np
import pandas as pd

def mark_strategy(strategy_name, strategy_results, df,
                  long_open="", long_close="",
                  short_open="", short_close=""):
    """
    Trade stratejisini analiz eder, işlemleri belirler ve zaman serisine event olarak ekler.

    Ekstra olarak kullanıcı her event'e açıklama (note) verebilir. Vermezse boş kalır.
    """

    if 'position' not in df.columns:
        raise ValueError("DataFrame içinde 'position' sütunu bulunmalıdır!")

    # Zaman kontrolü
    if not np.issubdtype(df.index.dtype, np.datetime64):
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        else:
            raise ValueError("DataFrame içinde 'timestamp' sütunu bulunmalı veya indeks datetime olmalı!")

    df = df.sort_values(by="timestamp", ascending=True)
    df['position_prev'] = df['position'].shift()

    # Pozisyon değişim maskeleri
    long_open_mask = (df['position_prev'].le(0)) & (df['position'].gt(0))
    long_close_mask = (df['position_prev'].gt(0)) & (df['position'].le(0))
    short_open_mask = (df['position_prev'].ge(0)) & (df['position'].lt(0))
    short_close_mask = (df['position_prev'].lt(0)) & (df['position'].ge(0))

    # Event tipleri ve açıklamaları
    event_configs = [
        (long_open_mask, "Long Open", long_open),
        (long_close_mask, "Long Close", long_close),
        (short_open_mask, "Short Open", short_open),
        (short_close_mask, "Short Close", short_close),
    ]

    events = []
    for mask, event_name, note in event_configs:
        indices = np.where(mask)[0]
        if len(indices) > 0:
            timestamps = df['timestamp'].iloc[indices].dt.strftime('%Y-%m-%dT%H:%M:%S')
            sizes = np.abs(df['position'].iloc[indices].values)
            notes = [note] * len(indices)
            # 🔥 Artık her event 4 parçalı: (timestamp, event_name, size, note)
            events.extend(zip(timestamps, [event_name] * len(indices), sizes, notes))

    events.sort(key=lambda x: x[0])

    strategy_results.append({
        "name": strategy_name,
        "type": "events",
        "data": events
    })
