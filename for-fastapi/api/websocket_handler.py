import asyncio
import websockets
import json
import aiohttp
import logging
from typing import List
from database import get_db
from core.config import BINANCE_API_URL

# Logger ayarları
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
#qwrerw
BASE_URL = "wss://stream.binance.com:9443/stream?streams="  # Combined stream için base URL
MAX_LISTEN_KEYS_PER_WS = 100  # Bir WebSocket başına maksimum listenKey sayısı
PING_INTERVAL = 30  # WebSocket'e her 30 saniyede bir ping atılacak
RECONNECT_DELAY = 5  # Bağlantı koparsa tekrar bağlanmak için bekleme süresi
LISTENKEY_REFRESH_INTERVAL = 1800  # 30 dakikada bir listenKey yenilenecek (1800 saniye)

active_websockets = {}  # Çalışan WebSocket'leri takip etmek için

async def create_listenkey(user_id: int, api_key: str, secret_key: str):
    """Binance API ile asenkron olarak listenKey oluşturur ve veritabanına kaydeder."""
    url = f"{BINANCE_API_URL}/api/v3/userDataStream"
    headers = {"X-MBX-APIKEY": api_key}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                listen_key = data.get("listenKey")
                
                async with get_db() as db:
                    await db.execute("UPDATE users SET listen_key = ? WHERE id = ?", (listen_key, user_id))
                    await db.commit()
                
                return listen_key
            else:
                error_text = await response.text()
                raise Exception(f"ListenKey oluşturulamadı: {error_text}")


def split_listen_keys(listen_keys: List[str]) -> List[List[str]]:
    """ListenKey listesini MAX_LISTEN_KEYS_PER_WS sınırına göre bölerek WebSocket grupları oluşturur."""
    return [listen_keys[i:i + MAX_LISTEN_KEYS_PER_WS] for i in range(0, len(listen_keys), MAX_LISTEN_KEYS_PER_WS)]


async def process_binance_data(user_id: int, data: dict):
    """Binance'ten gelen veriyi işleyip veritabanına kaydeder."""
    event_type = data.get("e")  # Olay türü (örneğin 'outboundAccountPosition')
    if event_type == "outboundAccountPosition":
        balances = data.get("B", [])
        async with get_db() as db:
            for balance in balances:
                asset = balance["a"]
                free_amount = balance["f"]
                locked_amount = balance["l"]
                await db.execute(
                    """
                    INSERT INTO user_balances (user_id, asset, free, locked)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, asset) DO UPDATE SET free = ?, locked = ?
                    """,
                    (user_id, asset, free_amount, locked_amount, free_amount, locked_amount)
                )
            await db.commit()
        logger.info(f"User {user_id} için bakiye güncellendi: {balances}")


async def start_websocket(listen_keys: List[str], websocket_name: str):
    """Belirtilen listenKey grubunu tek bir WebSocket üzerinden dinler."""
    streams = "/".join(listen_keys)
    url = f"{BASE_URL}{streams}"
    
    while True:
        try:
            async with websockets.connect(url) as websocket:
                logger.info(f"{websocket_name} başlatıldı...")
                active_websockets[websocket_name] = websocket
                
                async def ping_pong():
                    while True:
                        try:
                            await websocket.ping()
                            logger.info(f"{websocket_name} - Ping gönderildi.")
                        except Exception as e:
                            logger.error(f"{websocket_name} - Ping başarısız, bağlantı kesilmiş olabilir: {e}")
                            break
                        await asyncio.sleep(PING_INTERVAL)
                
                asyncio.create_task(ping_pong())  # Ping/pong işlemini paralel olarak çalıştır
                
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    logger.info(f"{websocket_name} Data: {data}")  # Gelen veriyi işle
                    user_id = 1  # Bunu gerçek kullanıcı ID ile eşlemen lazım
                    await process_binance_data(user_id, data)
        except Exception as e:
            logger.error(f"{websocket_name} Hatası: {e}, {RECONNECT_DELAY} saniye sonra tekrar denenecek...")
            await asyncio.sleep(RECONNECT_DELAY)  # Bağlantı koparsa biraz bekleyip tekrar dene


async def manage_websockets(listen_keys: List[str]):
    """WebSocket'lerin açık olup olmadığını kontrol eder, kapalıysa yeniden açar."""
    listen_key_groups = split_listen_keys(listen_keys)
    tasks = []
    
    for index, group in enumerate(listen_key_groups, start=1):
        websocket_name = f"multi_websocket{index}"
        websocket = active_websockets.get(websocket_name)
        
        if not websocket or websocket.closed:
            logger.info(f"{websocket_name} açık değil, başlatılıyor...")
            tasks.append(start_websocket(group, websocket_name))
        else:
            logger.info(f"{websocket_name} zaten açık.")
    
    if tasks:
        await asyncio.gather(*tasks)


async def refresh_listenkeys(interval: int = LISTENKEY_REFRESH_INTERVAL):
    """Binance listenKey'leri her 30 dakikada bir yeniler."""
    while True:
        async with get_db() as db:
            users = await db.execute("SELECT id, api_key FROM users WHERE listen_key IS NOT NULL")
            users = await users.fetchall()
            
        for user_id, api_key in users:
            url = f"{BINANCE_API_URL}/api/v3/userDataStream"
            headers = {"X-MBX-APIKEY": api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"User {user_id} listenKey başarıyla yenilendi.")
                    else:
                        error_text = await response.text()
                        logger.error(f"User {user_id} listenKey yenilenemedi: {error_text}")
        
        await asyncio.sleep(interval)
