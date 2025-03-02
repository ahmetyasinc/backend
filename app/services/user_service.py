from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from database import get_db

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()
