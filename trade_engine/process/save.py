import datetime
import json
import asyncio
import numpy as np
import decimal
import os

def aggregate_results_by_bot_id(all_results):
    from collections import defaultdict

    result = defaultdict(list)

    for res in all_results:
        bot_id = res["bot_id"]
        coin_data = {key: value for key, value in res.items() if key != "bot_id"}
        result[bot_id].append(coin_data)

    return dict(result)  # defaultdict yerine düz dict döndürmek daha güvenli


def convert_json_compatible(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_json_compatible(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_json_compatible(i) for i in obj]
    return obj


async def save_result_to_json(result, last_time, interval):
    loop = asyncio.get_running_loop()
    result = convert_json_compatible(result)

    # Dosya yolu: results/1m/
    folder = os.path.join("results", interval)
    os.makedirs(folder, exist_ok=True)

    # Zamanı datetime objesine çevir
    if isinstance(last_time, str):
        try:
            last_time = datetime.fromisoformat(last_time)
        except ValueError:
            last_time = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")

    filename = last_time.strftime("%Y-%m-%d_%H-%M-%S.json")
    filepath = os.path.join(folder, filename)

    def write_json():
        try:
            with open(filepath, "w") as f:
                json.dump(result, f, indent=4)
        except Exception as e:
            print(f"JSON yazma hatası: {e}")

    await loop.run_in_executor(None, write_json)



