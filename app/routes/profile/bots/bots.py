from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.auth import verify_token
from app.models.profile.bots.bots import Bots
from app.database import get_db
from app.schemas.bots.bots import BotsBase, BotsCreate, BotsUpdate, BotsOut

protected_router = APIRouter()

# GET all bots for user
@protected_router.get("/api/get-bots", response_model=list[BotsOut])
async def get_all_bots(db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    result = await db.execute(select(Bots).where(Bots.user_id == int(user_id)))
    return result.scalars().all()

# POST new bot (otomatik user_id eklenir)
@protected_router.post("/api/add-bots", response_model=BotsOut)
async def create_bot(bot: BotsCreate, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    new_bot = Bots(**bot.dict(), user_id=int(user_id))
    db.add(new_bot)
    await db.commit()
    await db.refresh(new_bot)
    return new_bot

# PATCH update bot (sadece kendi botunu güncelleyebilir)
@protected_router.patch("/api/bots/{bot_id}", response_model=BotsOut)
async def update_bot(bot_id: int, bot_data: BotsUpdate, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    result = await db.execute(select(Bots).where(Bots.id == bot_id, Bots.user_id == int(user_id)))
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found or unauthorized")

    for field, value in bot_data.dict(exclude_unset=True).items():
        setattr(bot, field, value)

    await db.commit()
    await db.refresh(bot)
    return bot

# DELETE bot (sadece kendi botunu silebilir)
@protected_router.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: int, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    result = await db.execute(select(Bots).where(Bots.id == bot_id, Bots.user_id == int(user_id)))
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found or unauthorized")
    await db.delete(bot)
    await db.commit()
    return {"detail": "Bot deleted"}

# PATCH activate (sadece kendi botunu aktif hale getirebilir)
@protected_router.patch("/api/bots/{bot_id}/activate")
async def activate_bot(bot_id: int, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    result = await db.execute(select(Bots).where(Bots.id == bot_id, Bots.user_id == int(user_id)))
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found or unauthorized")
    bot.active = True
    await db.commit()
    return {"detail": "Bot activated"}

# PATCH deactivate (sadece kendi botunu pasif hale getirebilir)
@protected_router.patch("/api/bots/{bot_id}/deactivate")
async def deactivate_bot(bot_id: int, db: AsyncSession = Depends(get_db), user_id: dict = Depends(verify_token)):
    result = await db.execute(select(Bots).where(Bots.id == bot_id, Bots.user_id == int(user_id)))
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found or unauthorized")
    bot.active = False
    await db.commit()
    return {"detail": "Bot deactivated"}
