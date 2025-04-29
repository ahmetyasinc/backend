from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.models.profile.indicator.indicator import Indicator
from app.models.profile.strategy.strategy import Strategy
from app.database import get_db
from app.schemas.strategy.strategy_imports import StrategyIndicatorUpdate

protected_router = APIRouter()

@protected_router.put("/api/strategies/update")
async def update_strategy_indicators(
    data: StrategyIndicatorUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    # Stratejiyi bul
    result = await db.execute(select(Strategy).where(Strategy.id == data.id))
    strategy = result.scalars().first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    resolved_ids = []

    for name in data.indicator_names:
        # İsimle eşleşen, erişilebilir indikatörleri bul
        result = await db.execute(
            select(Indicator)
            .where(
                Indicator.name == name,
                (Indicator.user_id == int(user_id)) |
                (Indicator.public.is_(True)) |
                (Indicator.tecnic.is_(True))
            )
            .order_by(
                (Indicator.user_id == int(user_id)).desc(),
                Indicator.tecnic.desc(),
                Indicator.public.desc()
            )
            .limit(1)
        )
        indicator = result.scalars().first()
        
        if not indicator:
            raise HTTPException(status_code=400, detail=f"Indicator '{name}' not found or not accessible.")

        resolved_ids.append(indicator.id)

    strategy.indicator_ids = resolved_ids

    await db.commit()
    await db.refresh(strategy)

    return {
        "message": "Strategy updated",
        "indicator_ids": resolved_ids
    }

@protected_router.get("/api/strategies/{strategy_id}")
async def get_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
    strategy = result.scalars().first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # ❗ Yetki kontrolü: Strateji bu kullanıcıya mı ait?
    if strategy.user_id != int(user_id):
        raise HTTPException(status_code=403, detail="Bu stratejiye erişim yetkiniz yok")

    if not strategy.indicator_ids:
        return {
            "id": strategy.id,
            "name": strategy.name,
            "indicator_names": []
        }

    result = await db.execute(select(Indicator).where(Indicator.id.in_(strategy.indicator_ids)))
    indicators = result.scalars().all()
    indicator_names = [i.name for i in indicators]

    return {
        "id": strategy.id,
        "name": strategy.name,
        "indicator_names": indicator_names
    }


