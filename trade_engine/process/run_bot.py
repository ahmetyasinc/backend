import math
import numpy as np
import pandas as pd
import time
import ta
import asyncio
from decimal import Decimal

from .library.empty import empty


def run_bot(bot, strategy_code, indicator_list, coin_data_dict):
    start_time = time.time()  # 🕒 Başlangıç zamanı

    order_fields = {
        "order_type": "", "limit_price": 0.0, "stop_price": 0.0, "stop_limit_price": 0.0,
        "callback_rate": 0.0, "activation_price": 0.0, "time_in_force": ""
    }

    df_dict = {}
    for coin_id in bot['stocks']:
        key = (coin_id, bot['period'])
        df = coin_data_dict.get(key)
        if df is not None:
            df = df.copy()
            df['coin_id'] = coin_id
            df_dict[coin_id] = df

    if not df_dict:
        print(f"Bot ID: {bot['id']} için veri bulunamadı.")
        return {"bot_id": bot['id'], "status": "no_data", "duration": 0.0}

    try:
        #print(f"Bot ID: {bot['id']} çalıştırılıyor...")
        results = []

        for coin_id in bot['stocks']:
            if coin_id not in df_dict:
                results.append({
                    "bot_id": bot['id'], "coin_id": coin_id,
                    "period": bot['period'], "status": "skipped", "message": "No data."
                })
                continue

            allowed_globals = {
                "__builtins__": {
                    "range": range, "len": len, "min": min, "max": max, "sum": sum, "abs": abs, "round": round,
                    "sorted": sorted, "zip": zip, "enumerate": enumerate, "map": map, "filter": filter,
                    "all": all, "any": any, "list": list, "dict": dict, "tuple": tuple, "set": set, "float": float,
                    "Decimal": Decimal, "pow": pow, "divmod": divmod,
                    "math": {
                        "ceil": math.ceil, "floor": math.floor, "fabs": math.fabs, "factorial": math.factorial,
                        "exp": math.exp, "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
                        "sin": math.sin, "cos": math.cos, "tan": math.tan, "atan": math.atan,
                        "pi": math.pi, "e": math.e
                    },
                    "print": lambda *args, **kwargs: empty(*args, **kwargs),
                },
                "np": np,
                "pd": pd,
                "asyncio": asyncio,
                "math": math,
                "df": df_dict[coin_id],
                "time": time,
                "ta": ta,
                "mark": lambda *args, **kwargs: empty(*args, **kwargs),
                "plot": lambda *args, **kwargs: empty(*args, **kwargs),
            }

            for indicator in indicator_list:
                exec(indicator['code'], allowed_globals)

            exec(strategy_code, allowed_globals)

            result_df = allowed_globals['df']
            last_positions = result_df['position'].iloc[-2:].tolist() if 'position' in result_df.columns and len(result_df) >= 2 else None

            order_info = {
                field: result_df[field].iloc[-1] if field in result_df.columns and len(result_df) > 0 else default
                for field, default in order_fields.items()
            }

            result_entry = {
                "bot_id": bot['id'], "coin_id": coin_id, "period": bot['period'],
                "status": "success", "last_positions": last_positions
            }
            result_entry.update(order_info)
            results.append(result_entry)

        duration = time.time() - start_time
        #print(f"✅ Bot ID: {bot['id']} tamamlandı. Süre: {duration:.2f} saniye")

        # 💡 Toplam sürenin de eklenmesi için metadata objesi
        return {
            "bot_id": bot['id'],
            "duration": duration,
            "status": "success",
            "results": results
        }

    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Bot ID: {bot['id']} çalışırken hata oluştu:\n{error_msg}")
        return {"bot_id": bot['id'], "status": "error", "error": error_msg, "duration": time() - start_time}

