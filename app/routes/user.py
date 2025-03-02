from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User

router = APIRouter()

# Kullanıcıları listeleme endpoint'i
@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {"users": users}


# Kullanıcı güncelleme (Edit) fonksiyonu
@router.put("/edit/{user_id}")
async def update_user(user_id: int, name: str = Form(None), email: str = Form(None), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    # Kullanıcıyı veritabanında ara
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")

    # Eğer name veya email gönderildiyse güncelle
    if name:
        user.name = name
    if email:
        user.email = email
    if password:
        user.password = password

    await db.commit()
    await db.refresh(user)  # Güncellenmiş kullanıcıyı al

    return {"message": "Kullanıcı başarıyla güncellendi", "user": {"id": user.id, "name": user.name, "email": user.email, "password": user.password}}
