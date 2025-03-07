from fastapi import APIRouter, HTTPException, Depends, Response
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.models import User
from app.database import get_db
from app.core.auth import create_access_token, create_refresh_token  # JWT fonksiyonlarını içe aktar

import json

from app.models.profile.binance_data import MainData
from app.routes.profile.get_binance_data import get_binance_data

router = APIRouter()

class main_data(BaseModel):
    user_id: int
    symbol: str
    interval: str


@router.get("/api/get-binance-data/")
async def get_trades(data: main_data, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MainData).where(MainData.user_id == data.user_id))
    have_data = result.scalars().first()

    # Kullanıcının daha önce verisi varsa ve aynı symbol + interval ile istek yapıyorsa
    if have_data and have_data.symbol == data.symbol and have_data.interval == data.interval:
        return have_data.data

    # Binance'den veri çek
    candle_data = get_binance_data(symbol=data.symbol, interval=data.interval)
    candle_data = json.dumps(candle_data)

    if have_data:
        # Eğer kayıt varsa, güncelle
        have_data.symbol = data.symbol
        have_data.interval = data.interval
        have_data.data = candle_data
    else:
        # Eğer kayıt yoksa, yeni kayıt oluştur
        mainData = MainData(user_id=data.user_id, symbol=data.symbol, interval=data.interval, data=candle_data)
        db.add(mainData)

    await db.commit()
    if have_data:
        await db.refresh(have_data)  # Güncellenen veriyi tekrar yükle

    return candle_data

