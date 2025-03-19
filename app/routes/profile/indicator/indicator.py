from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token

from app.models.profile.indicator.indicator import Indicator
from app.models.profile.indicator.indicators_favorite import IndicatorsFavorite
from sqlalchemy.future import select
from app.database import get_db
from app.schemas.indicator.indicator import IndicatorCreate, IndicatorUpdate
from fastapi import HTTPException

protected_router = APIRouter()

@protected_router.get("/api/public-indicators/")
async def get_public_indicators(
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
    ):
    """Public olan tüm indikatörleri getirir."""
    
    result = await db.execute(
        select(Indicator.id,
                Indicator.name,
                Indicator.code,
                #Indicator.created_at,
                Indicator.public,
               IndicatorsFavorite.id.isnot(None).label("favorite")  # Eğer favori varsa True, yoksa False döner
               )
               .outerjoin(IndicatorsFavorite,  # LEFT JOIN işlemi
                   (IndicatorsFavorite.indicator_id == Indicator.id) &
                   (IndicatorsFavorite.user_id == int(user_id)))
               .where(Indicator.public == True)
    )
    public_indicators = result.mappings().all()

    return {"public_indicators": public_indicators}

@protected_router.get("/api/get-indicators/")
async def get_indicators(
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının tüm indikatörlerini JSON formatında getirir.
    Eğer bir indikatör favori olarak işaretlenmişse, 'favorite': true olarak döner.
    """
    # Kullanıcının tüm indikatörlerini çek ve favori olup olmadığını kontrol et
    result = await db.execute(
        select(
            Indicator.id,
            Indicator.name,
            Indicator.code,
            Indicator.created_at,
            Indicator.public,
            IndicatorsFavorite.id.isnot(None).label("favorite")  # Eğer favori varsa True, yoksa False döner
        )
        .outerjoin(IndicatorsFavorite,  # LEFT JOIN işlemi
                   (IndicatorsFavorite.indicator_id == Indicator.id) &
                   (IndicatorsFavorite.user_id == int(user_id)))
        .where(Indicator.user_id == int(user_id))
    )

    indicators = result.mappings().all()

    return {"indicators": [dict(row) for row in indicators]}


@protected_router.get("/api/add-indicator/")
async def create_indicator(
    indicator_data: IndicatorCreate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcı için yeni bir indikatör oluşturur. Eğer aynı isimde indikatör varsa hata döner."""
    
    result = await db.execute(select(Indicator).where(Indicator.user_id == int(user_id), Indicator.name == indicator_data.name))
    existing_indicator = result.scalars().first()

    if existing_indicator:
        raise HTTPException(status_code=400, detail="Bu isimde bir indikatör zaten mevcut!")

    # Yeni indikatör oluştur
    new_indicator = Indicator(
        user_id= int(user_id),
        name=indicator_data.name,
        code=indicator_data.code,
    )
    db.add(new_indicator)
    await db.commit()
    await db.refresh(new_indicator)

    return {"message": "Indicator created successfully"}

@protected_router.put("/api/edit-indicator/{indicator_id}/")
async def update_indicator(
    indicator_id: int,
    indicator_data: IndicatorUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Belirtilen indikatörün bilgilerini günceller. Eğer indikatör bulunamazsa hata döner."""
    
    result = await db.execute(select(Indicator).where(Indicator.id == indicator_id, Indicator.user_id == int(user_id)))
    indicator = result.scalars().first()

    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found!")

    # Güncellenmesi gereken alanları değiştir
    indicator.name = indicator_data.name
    indicator.code = indicator_data.code

    await db.commit()
    await db.refresh(indicator)

    return {"message": "Indicator updated successfully", "indicator": indicator}

@protected_router.delete("/api/delete-indicator/{indicator_id}/")
async def delete_indicator(
    indicator_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Belirtilen indikatörü siler. Eğer indikatör bulunamazsa hata döner."""
    
    result = await db.execute(select(Indicator).where(Indicator.id == indicator_id, Indicator.user_id == int(user_id)))
    indicator = result.scalars().first()

    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found!")

    await db.delete(indicator)
    await db.commit()

    return {"message": "Indicator deleted successfully"}
