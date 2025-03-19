from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.core.auth import verify_token
from app.models.profile.strategy.strategy import Strategy
from app.models.profile.strategy.strategies_favorite import StrategiesFavorite
from app.schemas.strategy.strategy_favorite import StrategyFavoriteCreate

protected_router = APIRouter()

@protected_router.post("/api/strategy-add-favorite/") 
async def add_favorite_strategy(
    favorite_data: StrategyFavoriteCreate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının favori göstergesini (strategy) kaydeder. Eğer zaten ekliyse hata döner."""

    # İlgili stratejiü getir
    result = await db.execute(select(Strategy).where(Strategy.id == favorite_data.strategy_id))
    strategy = result.scalars().first()

    # Eğer böyle bir strateji yoksa hata döndür
    if not strategy:
        raise HTTPException(status_code=404, detail="Böyle bir gösterge bulunamadı!")

    # Eğer strateji başkasına ait ve public değilse hata döndür
    if strategy.user_id != int(user_id) and not strategy.public:
        raise HTTPException(status_code=403, detail="Bu gösterge özel olduğu için favorilere ekleyemezsiniz!")

    # Zaten favorilere eklenmiş mi kontrol et
    result = await db.execute(
        select(StrategiesFavorite)
        .where(
            StrategiesFavorite.user_id == int(user_id),
            StrategiesFavorite.strategy_id == favorite_data.strategy_id
        )
    )
    existing_favorite = result.scalars().first()

    if existing_favorite:
        raise HTTPException(status_code=400, detail="Bu gösterge zaten favorilere eklenmiş!")

    # Yeni favori kaydı oluştur
    new_favorite = StrategiesFavorite(
        user_id=int(user_id),
        strategy_id=favorite_data.strategy_id
    )

    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    return {"message": "Strategy added to favorites successfully"}

@protected_router.delete("/api/strategy-remove-favourite/")
async def remove_favorite_strategy(
    favorite_data: StrategyFavoriteCreate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının favorilerinden bir göstergeyi (strategy) kaldırır. Eğer favorilerde yoksa hata döner."""

    # İlgili favori kaydını getir
    result = await db.execute(
        select(StrategiesFavorite)
        .where(
            StrategiesFavorite.user_id == int(user_id),
            StrategiesFavorite.strategy_id == favorite_data.strategy_id
        )
    )
    favorite = result.scalars().first()

    # Eğer favorilerde yoksa hata döndür
    if not favorite:
        raise HTTPException(status_code=404, detail="Bu gösterge favorilerde bulunamadı!")

    # Favori kaydını sil
    await db.delete(favorite)
    await db.commit()

    return {"message": "Strategy removed from favorites successfully"}
