import numpy as np
import pandas as pd
import math

def plot_strategy(strategy_name, strategy_graph, df, commission=0.0, type="line"):

    pd.set_option("display.max_rows", None)  # Satır limiti kaldırılır

    # Tüm sayısal kolonları floata çevir
    df['position'] = df['position'].astype(float)
    df['close'] = df['close'].astype(float)
    commission = float(commission)

    if 'position' not in df.columns:
        raise ValueError("DataFrame içinde 'position' sütunu bulunmalıdır!")
    if 'close' not in df.columns:
        raise ValueError("DataFrame içinde 'close' sütunu bulunmalıdır!")

    # Zaman kontrolü
    if not np.issubdtype(df.index.dtype, np.datetime64):
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        else:
            raise ValueError("DataFrame içinde 'timestamp' sütunu bulunmalı veya indeks datetime olmalı!")
    else:
        df['timestamp'] = df.index

    df = df.sort_values(by="timestamp", ascending=True)

    # Pozisyon değişimlerini bul
    df['position_prev'] = df['position'].shift().fillna(0.0)
    df['position_change'] = df['position'] - df['position_prev']

    # Fiyat değişim oranı
    df['price_prev'] = df['close'].shift()
    df['price_change'] = (df['close'] - df['price_prev']) / df['price_prev']
    df['price_change'] = df['price_change'].shift(-1).fillna(0.0)

    # PnL
    df['pnl'] = df['price_change'] * df['position']

    # Komisyon: sadece pozisyon değiştiğinde uygulanır
    df['commission_cost'] = df['position_change'].abs() * commission

    # Net getiri = PnL - komisyon
    df['net_return'] = df['pnl'] - df['commission_cost']

    # Balance hesabı
    initial_balance = df['close'].iloc[0]
    df['balance'] = initial_balance * (1 + df['net_return']).cumprod()
    df['balance'] = df['balance'].shift().ffill().bfill()
    
    # Geçerli (timestamp, balance) değerlerini seç
    def is_valid(v):
        try:
            return not (pd.isna(v) or math.isinf(v))
        except Exception:
            return False

    graph_data = [
        (ts, bal) for ts, bal in zip(df['timestamp'], df['balance']) if is_valid(bal)
    ]

    strategy_graph.append({
        "name": strategy_name,
        "type": type,
        "data": graph_data
    })
