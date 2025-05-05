import time
from fastapi import APIRouter, Depends
from app.core.auth import verify_token
from app.routes.profile.scan.run_strategy_code import run_strategy_code
from app.routes.profile.scan.indicator_load import load_indicators
from app.routes.profile.scan.load_strategy_code import load_strategy_code
from app.routes.profile.scan.data_load import get_candles
from app.schemas.scan.scan import StrategyScanRequest

protected_router = APIRouter()

@protected_router.post("/api/scan/")
async def run_scan(
    payload: StrategyScanRequest,
    #user_id: dict = Depends(verify_token)
):
    """
    Belirli bir strateji ile belirli coinlerde tarama yapar.
    """
    print(f"Tarama başlatıldı. Strateji ID: {payload.strategy_id}")
    start_time = time.time()

    strategy_code = load_strategy_code(payload.strategy_id)
    indicator_codes = load_indicators(payload.strategy_id)

    if not strategy_code:
        return {"error": "Strategy not found"}

    results = {}  # Sonuçları burada toplayacağız

    for symbol in payload.symbols:
        df = get_candles(symbol, payload.interval, payload.candles)
        if df.empty:
            print(f"DataFrame is empty for symbol: {symbol}")
            continue
        
        result_entry = run_strategy_code(strategy_code, indicator_codes, df)

        if result_entry is not None:
            results[symbol] = float(result_entry)
        else:
            results[symbol] = None

    end_time = time.time()
    elapsed = round(end_time - start_time, 3)  # saniye cinsinden, 3 ondalık basamak

    print(f"Taramanın süresi: {elapsed} saniye. Strateji ID: {payload.strategy_id}")

    return {
        "results": results,
        "duration_seconds": elapsed
    }


async def scan_symbol(symbol: str, strategy_code: str, indicator_codes: list, interval: str, candles: int):
    df = get_candles(symbol, interval, candles)  # Eğer bu fonksiyon async değilse, sync olarak kalır
    if df.empty:
        print(f"DataFrame is empty for symbol: {symbol}")
        return symbol, None

    result_entry = run_strategy_code(strategy_code, indicator_codes, df)
    if result_entry is not None:
        return symbol, float(result_entry)
    else:
        return symbol, None
