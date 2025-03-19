from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.profile.indicator.indicator import Indicator  # Eğer model tanımlıysa
import asyncio

async def indicator(indicator_code: str, user_globals: dict):
    """
    PostgreSQL'deki indikatör kodunu getirip çalıştırır ve değişkenleri kullanıcıya tanımlar.
    """
    try:
        print("İndikatör Kodu:", indicator_code)

        # ✅ `exec` çalıştırılmadan önce mevcut değişkenleri kaydet
        before_vars = set(user_globals.keys())
        print("Önceki Değişkenler:", before_vars)

        # ✅ Kullanıcının koduyla aynı ortamda çalıştır (exec)
        exec(indicator_code, user_globals)

        # ✅ Yeni tanımlanan değişkenleri tespit et ve user_globals içine ekle
        after_vars = set(user_globals.keys())
        print("Sonraki Değişkenler:", after_vars)
        new_vars = after_vars - before_vars  # Yeni eklenen değişkenler
        print("Yeni Değişkenler:", new_vars)

        return {var: user_globals[var] for var in new_vars}

    except Exception as e:
        raise ImportError(f"İndikatör yüklenirken hata oluştu: {str(e)}")
