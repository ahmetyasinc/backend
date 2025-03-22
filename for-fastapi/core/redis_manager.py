import aioredis
import json
import asyncio
import time
from binance.client import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Order, User

# ✅ Redis Bağlantısını Başlat
redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)

# ---------------------- 🔹 Kullanıcı API Anahtarlarını Redis'e Kaydet 🔹 ----------------------

async def save_bot_api(user_id: str, api_key: str, api_secret: str):
    """
    Kullanıcının Binance API anahtarlarını Redis'e kaydeder.
    - 1 saat boyunca aktif olmazsa otomatik olarak silinir.
    """
    bot_data = {
        "api_key": api_key,
        "api_secret": api_secret
    }
    
    await redis.hset("bots:active", user_id, json.dumps(bot_data))
    await redis.expire("bots:active", 3600)  # 1 saat sonra otomatik sil

    print(f"✅ Kullanıcı {user_id} için API anahtarları kaydedildi.")

# ---------------------- 🔹 Emirleri Redis'e Kaydet (API Anahtarları Dahil) 🔹 ----------------------

async def save_order_to_redis(user_id: str, order_data: dict):
    """
    Kullanıcının emirlerini Redis'e kaydeder.
    - Kullanıcının API anahtarlarını Redis'ten çekerek emre ekler.
    - Emirleri FIFO (ilk giren ilk çıkar) listesi olarak saklar.
    """
    redis_key = f"orders:user:{user_id}"
    
    # ✅ Kullanıcının API anahtarlarını Redis'ten çek
    bot_info_json = await redis.hget("bots:active", user_id)
    if not bot_info_json:
        print(f"❌ Kullanıcı {user_id} için API anahtarları bulunamadı. Emir kaydedilmedi.")
        return None  # API anahtarı yoksa kaydetme

    bot_info = json.loads(bot_info_json)

    # ✅ API anahtarlarını emre ekle
    order_data["api_key"] = bot_info["api_key"]
    order_data["api_secret"] = bot_info["api_secret"]
    order_data["status"] = "PENDING"  # Varsayılan durum: Beklemede

    # ✅ Redis listesine ekle (FIFO kuyruğu)
    await redis.rpush(redis_key, json.dumps(order_data))

    print(f"✅ Kullanıcı {user_id} için emir kaydedildi: {order_data}")
    return order_data

# ---------------------- 🔹 Emirleri PostgreSQL'e Kaydet (Silmeden Önce) 🔹 ----------------------

async def save_order_to_db(order_data: dict, db: AsyncSession):
    """
    İşlenmiş emirleri PostgreSQL veritabanına kaydeder.
    """
    try:
        # ✅ Kullanıcının var olup olmadığını kontrol et
        result = await db.execute(select(User).where(User.id == order_data["user_id"]))
        user = result.scalars().first()

        if not user:
            print(f"❌ Kullanıcı {order_data['user_id']} bulunamadı. Emir kaydedilmedi.")
            return False

        # ✅ Yeni siparişi veritabanına ekle
        new_order = Order(
            order_id=order_data.get("orderId"),
            user_id=order_data.get("user_id"),
            symbol=order_data.get("symbol"),
            side=order_data.get("side"),
            order_type=order_data.get("type"),
            quantity=order_data.get("quantity"),
            price=order_data.get("price"),
            status="FILLED",  # Emir tamamlandı
            executed_at=order_data.get("executed_at"),
        )
        db.add(new_order)
        await db.commit()
        print(f"✅ Kullanıcı {order_data['user_id']} için emir veritabanına kaydedildi.")
        return True

    except Exception as e:
        print(f"❌ Veritabanına kayıt hatası: {e}")
        return False

# ---------------------- 🔹 Redis'ten Emirleri Çek ve Binance API'ye Gönder 🔹 ----------------------

async def process_orders_in_bulk(batch_size=50):
    """
    - FIFO kuyruğundan batch_size kadar emir çeker.
    - Binance API limitine göre emirleri işler.
    - Başarılı emirleri Redis'ten siler ve DB'ye kaydeder.
    - Başarısız emirleri tekrar kuyruğa ekler (max 3 deneme).
    """
    redis_key = "orders:queue"

    while True:
        orders = await redis.lrange(redis_key, 0, batch_size - 1)  # İlk batch_size kadar emri al
        if not orders:
            await asyncio.sleep(0.5)  # Kuyruk boşsa bekle
            continue

        async with get_db() as db:
            tasks = []
            for order_json in orders:
                order_data = json.loads(order_json)
                tasks.append(execute_and_save_order(order_data, db))  # Paralel işlem listesine ekle

            # ✅ API limitlerini kontrol etmek için rate limiter ekleyelim
            try:
                results = await asyncio.gather(*tasks)
            except Exception as e:
                print(f"🚨 Binance API Rate Limit hatası: {e}")
                await asyncio.sleep(1)  # API limitine takıldıysan 1 saniye bekle
                continue

        # ✅ Başarılı emirleri Redis'ten temizle
        await redis.ltrim(redis_key, len(orders), -1)

        # ❌ Başarısız olan emirleri tekrar kuyruğa ekle
        for idx, success in enumerate(results):
            if not success:
                order_data = json.loads(orders[idx])
                order_data["retry_count"] = order_data.get("retry_count", 0) + 1

                if order_data["retry_count"] < 3:
                    print(f"🔄 Kullanıcı {order_data['user_id']} için emir tekrar kuyruğa ekleniyor...")
                    await redis.rpush(redis_key, json.dumps(order_data))
                else:
                    print(f"🚨 Kullanıcı {order_data['user_id']} için emir 3 kez başarısız oldu. Log'a kaydedilecek.")


# ---------------------- 🔹 Binance API'ye Emir Gönder ve Veritabanına Kaydet 🔹 ----------------------

async def execute_and_save_order(order_data: dict, db: AsyncSession):
    """
    - Binance API'ye emir gönderir.
    - İşlem başarılı olursa PostgreSQL'e kaydeder.
    - Başarısız olursa 3 kez tekrar dener.
    """
    user_id = order_data["user_id"]
    api_key = order_data["api_key"]
    api_secret = order_data["api_secret"]

    client = Client(api_key, api_secret)

    success = await execute_order(client, order_data)

    if success:
        print(f"✅ Kullanıcı {user_id} için emir başarıyla işlendi: {order_data}")
        order_data["executed_at"] = time.time()
        await save_order_to_db(order_data, db)
    else:
        print(f"❌ Kullanıcı {user_id} için emir başarısız oldu: {order_data}")
        order_data["retry_count"] = order_data.get("retry_count", 0) + 1
        if order_data["retry_count"] < 3:
            print(f"🔄 Emir tekrar deneniyor...")
            await asyncio.sleep(10)
            await redis.rpush(f"orders:user:{user_id}", json.dumps(order_data))

