import pandas as pd
import asyncio
from concurrent.futures import ProcessPoolExecutor
from .save import save_result_to_json, aggregate_results_by_bot_id
from .run_bot import run_bot

from concurrent.futures import ProcessPoolExecutor
from os import cpu_count  # CPU çekirdek sayısını otomatik almak için

async def run_all_bots_async(bots, strategies_with_indicators, coin_data_dict, last_time, interval):
    loop = asyncio.get_running_loop()

    max_workers = min(len(bots), max(1, int(cpu_count() / 2)))  # En az 1

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        tasks = []
        for bot, strategy_info in zip(bots, strategies_with_indicators):
            strategy_code = strategy_info['strategy_code']
            indicator_list = strategy_info['indicators']

            # 🔹 Sadece gerekli verileri coin_data_dict'ten çek
            required_keys = [(coin_id, bot['period']) for coin_id in bot['stocks']]
            filtered_coin_data = {
                key: coin_data_dict[key]
                for key in required_keys
                if key in coin_data_dict
            }

            task = loop.run_in_executor(
                executor, run_bot, bot, strategy_code, indicator_list, filtered_coin_data
            )
            tasks.append(task)

        results_per_bot = await asyncio.gather(*tasks)

        all_results = []

        for res in results_per_bot:
            if isinstance(res, dict):
                if "results" in res and isinstance(res["results"], list):
                    all_results.extend(res["results"])
                else:
                    all_results.append(res)
            elif isinstance(res, list):
                all_results.extend(res)

        print("here")

        # 🔹 Grupla ve JSON’a kaydet
        result_dict = aggregate_results_by_bot_id(all_results)
        # BURADA BİNANCE İŞLEMLERİ İÇİN TETİKLENME YAPILACAK
        # TAHANINFONKSİYONU(result_dict)
        await save_result_to_json(result_dict, last_time, interval)

        return all_results
