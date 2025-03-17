from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.models.profile.indicator import Indicator
from sqlalchemy.future import select


from app.database import get_db
from app.schemas.indicator import IndicatorCreate

protected_router = APIRouter()

from fastapi import HTTPException

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
