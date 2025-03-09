from ..core.order_manager import order_manager
from ..core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

async def create_order(order_data: dict, db: Session = Depends(get_db)):
    # Veritabanına kaydetme işlemleri
    order_id = 1  # Örnek
    order_manager.add_order(order_id, order_data)
    return {"message": "Sipariş oluşturuldu", "order_id": order_id}
