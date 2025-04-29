from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.models.profile.api_keys.api_keys import APIKey
from sqlalchemy.future import select
from app.database import get_db
from app.schemas.api_keys.api_keys import APIKeyBase, APIKeyCreate, APIKeyOut
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

protected_router = APIRouter()

@protected_router.get("/api/get-apis/")
async def get_user_apis(db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    result = await db.execute(select(APIKey).where(APIKey.user_id == int(user_id)))
    api_keys = result.scalars().all()
    return api_keys

@protected_router.post("/api/create-api/")
async def create_api_key(api_key: APIKeyCreate, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    db_api_key = APIKey(**api_key.dict(), user_id=int(user_id))
    print(f"API key data: {api_key.dict()}")
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    return db_api_key


@protected_router.post("/api/delete-api/")
async def delete_api_key(data: dict, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    api_name = data.get("name")
    if not api_name:
        raise HTTPException(status_code=400, detail="API adı belirtilmedi.")

    # Kullanıcının bu isimde API'si var mı?
    result = await db.execute(select(APIKey).where(APIKey.user_id == int(user_id), APIKey.api_name == api_name))
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API anahtarı bulunamadı.")

    await db.delete(api_key)
    await db.commit()
    return {"detail": "API anahtarı başarıyla silindi."}