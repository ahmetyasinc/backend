async def get_user(user_id: int):
    # Kullanıcı bilgilerini veritabanından çekme işlemleri
    return {"user_id": user_id, "username": "testuser"}

async def get_binance_keys(user_id: int):
    """Kullanıcının Binance API ve Secret Key'ini veritabanından getirir"""
    async with get_db() as db:
        user = await db.execute("SELECT binance_api_key, binance_secret_key FROM users WHERE id = ?", (user_id,))
        keys = await user.fetchone()
        return keys if keys else (None, None)
