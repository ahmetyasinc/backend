import pandas as pd
import asyncio
from concurrent.futures import ProcessPoolExecutor
from .save import group_results_by_bot, save_result_to_json
from .run_bot import run_bot

from concurrent.futures import ProcessPoolExecutor
from os import cpu_count  # CPU çekirdek sayısını otomatik almak için

async def run_all_bots_async(bots, strategies_with_indicators, coin_data_dict, last_time, interval):
    loop = asyncio.get_running_loop()

    max_workers = min(len(bots), max(1, int(cpu_count() / 2)))  # En az 1
    #print(f"Max workers: {max_workers}")

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

        # 🔹 Tüm bot sonuçlarını düz liste haline getir
        all_results = []
        durations = []  # süre ölçümleri

        for res in results_per_bot:
            if isinstance(res, dict):
                durations.append((res["bot_id"], round(res.get("duration", 0), 2)))
                if "results" in res and isinstance(res["results"], list):
                    all_results.extend(res["results"])
                else:
                    all_results.append(res)
            elif isinstance(res, list):
                all_results.extend(res)

        # 🔹 Grupla ve JSON’a kaydet
        grouped_results = group_results_by_bot(all_results)
        await save_result_to_json(grouped_results, last_time, interval)

        # 🔹 Süre tablosunu yazdır
        #if durations:
        #    durations.sort(key=lambda x: x[1], reverse=True)
        #    print("\n🧾 BOT SÜRE TABLOSU:")
        #    print("{:<10} {:<10}".format("Bot ID", "Süre (s)"))
        #    print("-" * 25)
        #    for bot_id, dur in durations:
        #        print(f"{bot_id:<10} {dur:<10}")

        return all_results
