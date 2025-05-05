import math
import numpy as np
import pandas as pd
import time
import ta
import asyncio
from decimal import Decimal

from app.routes.profile.scan.library.empty import empty

def run_strategy_code(strategy_code,indicator_codes,df):
    

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
        "df": df,
        "time": time,
        "ta": ta,
        "mark": lambda *args, **kwargs: empty(*args, **kwargs),
        "plot": lambda *args, **kwargs: empty(*args, **kwargs),
    }

    for indicator in indicator_codes:
        try:
            exec(indicator['code'], allowed_globals)
        except Exception as e:
            print(f"Indicator çalıştırılırken hata: {e}")

    try:
        exec(strategy_code, allowed_globals)
    except Exception as e:
        print(f"Strateji çalıştırılırken hata: {e}")

    result_df = allowed_globals['df']
    if 'position' in result_df.columns and len(result_df) >= 1:
        last_position = result_df['position'].iloc[-1]
    else:
        last_position = None

    return last_position