from fastapi import APIRouter, HTTPException
from .endpoints import items, users  # Örnek endpoint'ler
from core.redis_manager import redis

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

@api_router.get("/redis-test")
async def test_redis():
    try:
        await redis.set("test_key", "Redis çalışıyor!")
        result = await redis.get("test_key")
        return {"status": "success", "message": result.decode()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
