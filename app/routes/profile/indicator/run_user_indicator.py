import math
from typing import List
import numpy as np
import pandas as pd
import time

from app.routes.profile.indicator.indicator_library.plot_indicator import plot
from app.routes.profile.indicator.indicator_library.print_indicator import custom_print

async def run_user_indicator(user_code: str, data: list[dict]):
    """
    Kullanıcının indikatör kodunu güvenli bir ortamda çalıştırır.
    Kullanıcı, `plot(indicator_name, type, on_graph, data)` fonksiyonunu kullanarak veri çizebilir.
    
    - `user_code`: Kullanıcının yazdığı Python kodu
    - `data`: 5000 mumluk veri (dict listesi)
    """

    try:
        # Veriyi Pandas DataFrame'e çevir
        df = pd.DataFrame(data)

        # İndikatör sonuçlarını saklayacak liste
        indicator_results = []

        # Kullanıcının `print()` çıktıları burada saklanacak
        print_outputs = []  

        # Kullanıcı kodunun çalışma ortamını kısıtla (Tüm gerekli fonksiyonları ekledik!)
        allowed_globals = {
            "__builtins__": {
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
                "float": float,
                "int": int,
                "str": str,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,

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
                "print": lambda *args, **kwargs: custom_print(print_outputs, *args, **kwargs)
            },

            # ✅ NumPy ve Pandas için İzinler
            "np": np,
            "pd": pd,
            "math": math,
            "df": df,

            # ✅ Zaman ölçümü için `time`
            "time": time,

            # ✅ Grafik oluşturma fonksiyonu (plot)
            "plot": lambda *args, **kwargs: plot(indicator_results, *args, **kwargs)
        }

        # Kullanıcı kodunu çalıştır
        exec(user_code, allowed_globals)

        # JSON formatına uygun hale getir
        return indicator_results, print_outputs

    except Exception as e:
        return {"status": "error", "message": str(e)}, {"prints": print_outputs}
