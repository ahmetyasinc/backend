import requests
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.models.profile.binance_coins import BinanceCoin
from app.models.profile.binance_coins_pinned import BinanceCoinsPinned
from sqlalchemy.future import select
from app.database import get_db
from app.schemas.binance_coins.binance_coins import CoinCreate, PinCoin
from fastapi import HTTPException

protected_router = APIRouter()

@protected_router.post("/api/fetch-and-add-binance-coins/")
async def fetch_and_add_binance_coins(db: AsyncSession = Depends(get_db)):
    # Binance exchangeInfo endpoint'inden verileri çek
    response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Binance API erişim hatası!")

    data = response.json()
    symbols_data = data.get("symbols", [])

    created_coins = []
    skipped_coins = []

    for item in symbols_data:
        binance_symbol = item.get("symbol")
        base_asset = item.get("baseAsset")
        quote_asset = item.get("quoteAsset")

        # Sadece USDT çiftlerini ekle (örn. BTCUSDT, ETHUSDT)
        if not binance_symbol.endswith("USDT"):
            continue

        result = await db.execute(
            select(BinanceCoin).where(
                BinanceCoin.symbol == base_asset,
                BinanceCoin.binance_symbol == binance_symbol
            )
        )
        existing_coin = result.scalars().first()

        if existing_coin:
            skipped_coins.append(binance_symbol)
            continue

        new_coin = BinanceCoin(
            name=base_asset,              # Örnek: Bitcoin, Ethereum, vs.
            symbol=base_asset,            # BTC, ETH
            binance_symbol=binance_symbol  # BTCUSDT
        )
        db.add(new_coin)
        created_coins.append(binance_symbol)

    await db.commit()

    return {
        "message": f"{len(created_coins)} coin eklendi.",
        "eklendi": created_coins,
        "atlananlar": skipped_coins
    }

@protected_router.get("/api/get-coin-list/")
async def get_coin_list(
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının tüm indikatörlerini JSON formatında getirir.
    Eğer bir indikatör favori olarak işaretlenmişse, 'favorite': true olarak döner.
    """

    from app.models.profile.binance_coins_pinned import BinanceCoinsPinned  # Modeli içe aktar

    # Kullanıcı için coinleri çek ve pinned olup olmadığını kontrol et
    result = await db.execute(
        select(
            BinanceCoin.id,
            BinanceCoin.name,
            BinanceCoin.symbol,
            #BinanceCoin.created_at,
            BinanceCoin.binance_symbol,
            BinanceCoinsPinned.id.isnot(None).label("pinned")  # Eğer pinned varsa True, yoksa False döner
        )
        .outerjoin(BinanceCoinsPinned,  # LEFT JOIN işlemi
                   (BinanceCoinsPinned.coin_id == BinanceCoin.id) &
                   (BinanceCoinsPinned.user_id == int(user_id)))
    )

    coins = result.mappings().all()

    return {"coins": [dict(row) for row in coins]}

@protected_router.post("/api/pin-binance_coin/") 
async def pin_binance_coin(
    pin_coin_data: PinCoin,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
    ):
    """Kullanıcının favori göstergesini (indicator) kaydeder. Eğer zaten ekliyse hata döner."""

    # İlgili indikatörü getir
    result = await db.execute(select(BinanceCoin).where(BinanceCoin.id == pin_coin_data.coin_id))
    coin = result.scalars().first()

    # Eğer böyle bir indikatör yoksa hata döndür
    if not coin:
        raise HTTPException(status_code=404, detail="Böyle bir coin bulunamadı!")

    # Zaten favorilere eklenmiş mi kontrol et
    result = await db.execute(
        select(BinanceCoinsPinned)
        .where(
            BinanceCoinsPinned.user_id == int(user_id),
            BinanceCoinsPinned.coin_id == pin_coin_data.coin_id
        )
    )
    existing_favorite = result.scalars().first()

    if existing_favorite:
        raise HTTPException(status_code=400, detail="Bu coin zaten pinlenmiş!")

    # Yeni favori kaydı oluştur
    new_pinned = BinanceCoinsPinned(
        user_id=int(user_id),
        coin_id=pin_coin_data.coin_id
    )

    db.add(new_pinned)
    await db.commit()
    await db.refresh(new_pinned)

    return {"message": "Coin added to pinned successfully"}

@protected_router.delete("/api/unpin-binance-coin/")
async def unpin_binance_coin(
    pin_coin_data: PinCoin,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının pinlediği coini kaldırır."""

    # Kullanıcının bu coini pinleyip pinlemediğini kontrol et
    result = await db.execute(
        select(BinanceCoinsPinned)
        .where(
            BinanceCoinsPinned.user_id == int(user_id),
            BinanceCoinsPinned.coin_id == pin_coin_data.coin_id
        )
    )
    pinned_coin = result.scalars().first()

    # Eğer kayıt yoksa hata döndür
    if not pinned_coin:
        raise HTTPException(status_code=404, detail="Bu coin zaten pinlenmemiş!")

    # Kayıt varsa, sil ve değişiklikleri kaydet
    await db.delete(pinned_coin)
    await db.commit()

    return {"message": "Coin removed from pinned successfully"}
