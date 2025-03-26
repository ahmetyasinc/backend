from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.core.auth import verify_token
from app.models.profile.indicator.indicator import Indicator
from app.models.profile.indicator.indicators_favorite import IndicatorsFavorite
from app.schemas.indicator.indicator_favorite import IndicatorFavoriteCreate

protected_router = APIRouter()

@protected_router.post("/api/indicator-add-favorite/") 
async def add_favorite_indicator(
    favorite_data: IndicatorFavoriteCreate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının favori göstergesini (indicator) kaydeder. Eğer zaten ekliyse hata döner."""

    # İlgili indikatörü getir
    result = await db.execute(select(Indicator).where(Indicator.id == favorite_data.indicator_id))
    indicator = result.scalars().first()

    # Eğer böyle bir indikatör yoksa hata döndür
    if not indicator:
        raise HTTPException(status_code=404, detail="Böyle bir gösterge bulunamadı!")

    # Eğer indikatör başkasına ait ve public değilse hata döndür
    if indicator.user_id != int(user_id) and not indicator.public and not indicator.tecnic:
        raise HTTPException(status_code=403, detail="Bu gösterge özel olduğu için favorilere ekleyemezsiniz!")

    # Zaten favorilere eklenmiş mi kontrol et
    result = await db.execute(
        select(IndicatorsFavorite)
        .where(
            IndicatorsFavorite.user_id == int(user_id),
            IndicatorsFavorite.indicator_id == favorite_data.indicator_id
        )
    )
    existing_favorite = result.scalars().first()

    if existing_favorite:
        raise HTTPException(status_code=400, detail="Bu gösterge zaten favorilere eklenmiş!")

    # Yeni favori kaydı oluştur
    new_favorite = IndicatorsFavorite(
        user_id=int(user_id),
        indicator_id=favorite_data.indicator_id
    )

    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    return {"message": "Indicator added to favorites successfully"}

@protected_router.delete("/api/indicator-remove-favourite/")
async def remove_favorite_indicator(
    favorite_data: IndicatorFavoriteCreate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının favorilerinden bir göstergeyi (indicator) kaldırır. Eğer favorilerde yoksa hata döner."""

    # İlgili favori kaydını getir
    result = await db.execute(
        select(IndicatorsFavorite)
        .where(
            IndicatorsFavorite.user_id == int(user_id),
            IndicatorsFavorite.indicator_id == favorite_data.indicator_id
        )
    )
    favorite = result.scalars().first()

    # Eğer favorilerde yoksa hata döndür
    if not favorite:
        raise HTTPException(status_code=404, detail="Bu gösterge favorilerde bulunamadı!")

    # Favori kaydını sil
    await db.delete(favorite)
    await db.commit()

    return {"message": "Indicator removed from favorites successfully"}
