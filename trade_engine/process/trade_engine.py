from data.bot_load import load_active_bots
from data.strategy_load import load_strategy
from data.indicator_load import load_indicators
from data.data_load import fetch_all_candles

async def run_trade_engine(interval):
    bots = load_active_bots(interval)
    if not bots:
        #print("Aktif bot bulunamadı.")
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

    coin_data_dict = await fetch_all_candles(coin_requirements)

    return strategies_with_indicators, coin_data_dict, bots