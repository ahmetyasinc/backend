from ast import Await
import math
from typing import List
import numpy as np
import pandas as pd
import time
import asyncio

from app.routes.profile.strategy.strategy_library.empty import empty
from app.routes.profile.strategy.strategy_library.plot_strategy import plot_strategy
from app.routes.profile.strategy.strategy_library.import_strategy import indicator
from app.routes.profile.strategy.strategy_library.print_strategy import custom_print

async def run_user_strategy(strategy_name: str, user_code: str, data: list[dict], user_id, indicator_codes: list[str], db):
    """
    Kullanıcının indikatör kodunu güvenli bir ortamda çalıştırır.
    Kullanıcı, `plot(strategy_name, type, on_graph, data)` fonksiyonunu kullanarak veri çizebilir.
    
    - `user_code`: Kullanıcının yazdığı Python kodu
    - `data`: 5000 mumluk veri (dict listesi)
    """

    try:       

        # Veriyi Pandas DataFrame'e çevir
        df = pd.DataFrame(data)

        # Strateji sonuçlarını saklayacak liste
        strategy_results = []

        # Kullanıcının `print()` çıktıları burada saklanacak
        print_outputs = []  

        user_globals = {}

        # ✅ Sonra allowed_globals sözlüğünü tanımla
        allowed_globals = {
            "__builtins__": {
                "await": Await,
                # ✅ Temel Python Fonksiyonları
                "range": range,
                "len": len,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "zip": zip,
                "enumerate": enumerate,
                "map": map,
                "filter": filter,
                "all": all,
                "any": any,
                
                # ✅ Veri Tipleri
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "float": float,

                # ✅ Matematiksel Fonksiyonlar
                "pow": pow,
                "divmod": divmod,

                # ✅ `math` Modülü (Trigonometri, Logaritma, Üstel Fonksiyonlar)
                "math": {
                    "ceil": math.ceil, "floor": math.floor, "fabs": math.fabs, "factorial": math.factorial,
                    "exp": math.exp, "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
                    "sin": math.sin, "cos": math.cos, "tan": math.tan, "atan": math.atan,
                    "pi": math.pi, "e": math.e
                },

                # ✅ Kullanıcının Print Çıktılarını Kaydetmesi İçin
                "print": lambda *args, **kwargs: empty(*args, **kwargs)
                #"print": lambda *args, **kwargs: custom_print(print_outputs, *args, **kwargs)
            },

            # ✅ NumPy ve Pandas için İzinler
            "np": np,
            "pd": pd,
            "asyncio": asyncio,
            "math": math,
            "df": df,

            # ✅ Zaman ölçümü için `time`
            "time": time,

            # ✅ Grafik oluşturma fonksiyonu (plot)
            "reach": lambda *args, **kwargs: indicator(user_globals, *args, **kwargs),
            "plot": lambda *args, **kwargs: empty(*args, **kwargs)
        }

        for indicator_code in indicator_codes:
            exec(indicator_code, allowed_globals)

        allowed_globals.update(user_globals)
        allowed_globals["plot"] = lambda *args, **kwargs: plot_strategy(strategy_name, strategy_results, *args, **kwargs)
        allowed_globals["__builtins__"]["print"] = lambda *args, **kwargs: custom_print(print_outputs, *args, **kwargs)
        
        # Kullanıcı kodunu çalıştır
        
        exec(user_code, allowed_globals)

        # Strateji verisini JSON'a uygun hale getir
        def convert_to_json_compatible(obj):
            """ NumPy tiplerini Python native tiplerine çevirir. """
            if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()  # NumPy array'leri listeye çevir
            elif isinstance(obj, list):
                return [convert_to_json_compatible(i) for i in obj]  # Liste içindeki NumPy tiplerini düzelt
            elif isinstance(obj, tuple):
                return tuple(convert_to_json_compatible(i) for i in obj)  # Tuple içindeki NumPy tiplerini düzelt
            elif isinstance(obj, dict):
                return {k: convert_to_json_compatible(v) for k, v in obj.items()}  # Dict içindeki NumPy tiplerini düzelt
            return obj
        
        strategy_results = convert_to_json_compatible(strategy_results)

        # JSON formatına uygun hale getir
        print(print_outputs)
        return strategy_results, print_outputs

    except Exception as e:
        return {"status": "error", "message": str(e)}, {"prints": print_outputs}
