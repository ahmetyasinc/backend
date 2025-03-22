from ..core.order_manager import redis_manager
from ..database import get_db
from fastapi import Depends
from ..api import websocket_handler
from sqlalchemy.orm import Session
import asyncio
from redis_manager import (
    save_order_to_redis,
    process_orders_in_bulk
)

class OrderService:
    """Emirleri yöneten servis (Redis + DB)"""

    @staticmethod
    async def add_order(user_id: str, order_data: dict):
        """
        Yeni bir emri FIFO kuyruğuna ekler (Redis üzerinden).
        """
        await save_order_to_redis(user_id, order_data)

    @staticmethod
    async def start_order_processing(batch_size=50):
        """
        Sürekli çalışan bir loop ile emirleri işler.
        Eğer hata alırsa bekleyip tekrar başlar.
        """
        while True:
            try:
                await process_orders_in_bulk(batch_size)  # Kuyruktaki emirleri işle
            except Exception as e:
                print(f"🚨 Hata alındı, tekrar başlatılıyor: {e}")
                await asyncio.sleep(2)  # 2 saniye bekleyip tekrar dene
