
import asyncio
import time
from data.bot_load import load_active_bots
from data.strategy_load import load_strategy
from data.indicator_load import load_indicators
from data.data_load import fetch_all_candles

def run_trade_engine():
    t0 = time.time()
    print("Trade Engine Başlatılıyor...\n")
    bots = load_active_bots()
    t1 = time.time()
    print(f"=> Botlar yüklendi. Süre: {t1 - t0:.2f} saniye.")

    if not bots:
        print("Aktif bot bulunamadı.")
        return [], {}, []

    strategies_with_indicators = []
    coin_requirements = {}

    for bot in bots:
        strategy_code = load_strategy(bot['strategy_id'])
        indicator_list = load_indicators(bot['strategy_id'])

        strategies_with_indicators.append({
            'strategy_id': bot['strategy_id'],
            'strategy_code': strategy_code,
            'indicators': indicator_list
        })

        for coin_id in bot['stocks']:
            key = (coin_id, bot['period'])
            if key not in coin_requirements or coin_requirements[key] < bot['candle_count']:
                coin_requirements[key] = bot['candle_count']

    t2 = time.time()
    print(f"=> Stratejiler ve indikatörler yüklendi. Süre: {t2 - t1:.2f} saniye.")

    coin_data_dict = asyncio.run(fetch_all_candles(coin_requirements))

    t3 = time.time()
    print(f"=> Coin verileri yüklendi. Süre: {t3 - t2:.2f} saniye.")
    print(f"=> Toplam veri hazırlık süresi: {t3 - t0:.2f} saniye.")

    return strategies_with_indicators, coin_data_dict, bots