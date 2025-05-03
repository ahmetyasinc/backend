import datetime
import json
import asyncio
import numpy as np
import decimal
import os

def group_results_by_bot(all_results):
    from collections import defaultdict

    grouped = defaultdict(list)

    for result in all_results:
        bot_id = result["bot_id"]

        # 🔹 Bot'a ait coin bilgileri + tüm ekstra bilgiler
        coin_result = {key: value for key, value in result.items() if key != "bot_id"}

        grouped[bot_id].append(coin_result)

    # 🔹 JSON yazımı için liste formatına dönüştür
    final_grouped = []
    for bot_id, coin_results in grouped.items():
        final_grouped.append({
            "bot_id": bot_id,
            "results": coin_results
        })

    return final_grouped



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

    # Dosya adı: 2025-04-29_13-53-00.json
    filename = last_time.strftime("%Y-%m-%d_%H-%M-%S.json")
    filepath = os.path.join(folder, filename)

    def write_json():
        try:
            with open(filepath, "w") as f:
                json.dump(result, f, indent=4)
        except Exception as e:
            print(f"JSON yazma hatası: {e}")

    await loop.run_in_executor(None, write_json)



