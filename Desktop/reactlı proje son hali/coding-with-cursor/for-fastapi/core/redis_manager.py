import aioredis
import json
import asyncio
import time
from binance.client import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models import Order, User

# ✅ Initialize Redis Connection
redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)

# ---------------------- 🔹 Store API Keys in Redis 🔹 ----------------------

async def save_bot_api(user_id: str, api_key: str, api_secret: str):
    """
    Store the user's Binance API key and secret in Redis.
    Automatically deletes if inactive after 1 hour.
    """
    bot_data = {
        "api_key": api_key,
        "api_secret": api_secret
    }

    await redis.hset("bots:active", user_id, json.dumps(bot_data))
    await redis.expire("bots:active", 3600)  # Auto-delete after 1 hour

    print(f"✅ API keys for user {user_id} saved in Redis.")

# ---------------------- 🔹 Save Orders in Redis (With API Keys) 🔹 ----------------------

async def save_order_to_redis(user_id: str, order_data: dict):
    """
    Store a user's order in Redis.
    - Automatically fetches API key & secret from Redis and adds it to the order.
    - Saves the order in a FIFO queue (list).
    """
    redis_key = f"orders:user:{user_id}"
    
    # ✅ Fetch API keys from Redis
    bot_info_json = await redis.hget("bots:active", user_id)
    if not bot_info_json:
        print(f"❌ No API keys found for user {user_id}. Order not saved.")
        return None  # Do not save the order if API keys are missing

    bot_info = json.loads(bot_info_json)

    # ✅ Add API keys to the order
    order_data["api_key"] = bot_info["api_key"]
    order_data["api_secret"] = bot_info["api_secret"]
    order_data["status"] = "PENDING"  # Default order status

    # ✅ Store order in Redis list (FIFO queue)
    await redis.rpush(redis_key, json.dumps(order_data))

    print(f"✅ Order saved to Redis for user {user_id}: {order_data}")
    return order_data

# ---------------------- 🔹 Save Orders to PostgreSQL Before Deleting 🔹 ----------------------

async def save_order_to_db(order_data: dict, db: AsyncSession):
    """
    Saves the executed order to the database under the correct user.
    """
    try:
        # Check if the user exists
        result = await db.execute(select(User).where(User.id == order_data["user_id"]))
        user = result.scalars().first()

        if not user:
            print(f"❌ User {order_data['user_id']} not found! Order not saved.")
            return False  # Ensure we don't save orders without valid users

        # ✅ Save the order linked to the correct user
        new_order = Order(
            order_id=order_data.get("orderId"),
            user_id=order_data.get("user_id"),
            symbol=order_data.get("symbol"),
            side=order_data.get("side"),
            order_type=order_data.get("type"),
            quantity=order_data.get("quantity"),
            price=order_data.get("price"),
            status="FILLED",  # Because it was executed
            executed_at=order_data.get("executed_at"),
        )
        db.add(new_order)
        await db.commit()
        print(f"✅ Order {order_data['orderId']} saved to DB under user {order_data['user_id']}.")
        return True

    except Exception as e:
        print(f"❌ Error saving order to DB: {e}")
        return False

# ---------------------- 🔹 Process Orders from Redis & Execute 🔹 ----------------------

async def process_orders_in_bulk():
    """
    - Fetches and executes all pending orders from Redis in bulk.
    - Uses stored API keys for authentication.
    - Processes orders with python-binance.
    - Saves executed orders under the correct user in PostgreSQL before deleting from Redis.
    - Retries failed orders up to 3 times.
    """
    redis_keys = await redis.keys("orders:user:*")  # Get all user order keys
    if not redis_keys:
        print("🚀 No pending orders found.")
        return

    pipe = redis.pipeline()
    orders_to_process = []

    # Retrieve all orders using pipeline
    for key in redis_keys:
        user_orders = await redis.lrange(key, 0, -1)  # Get all orders
        orders_to_process.extend([(key, json.loads(order)) for order in user_orders])
        await pipe.ltrim(key, len(user_orders), -1)  # Clear processed orders from Redis

    await pipe.execute()  # Execute Redis pipeline

    # Process orders in batch
    async with get_db() as db:
        for user_key, order_data in orders_to_process:
            user_id = order_data["user_id"]
            
            # ✅ Get API credentials from the saved order
            api_key = order_data["api_key"]
            api_secret = order_data["api_secret"]

            # ✅ Authenticate Binance API
            client = Client(api_key, api_secret)

            # ✅ Execute the order
            success = await execute_order(client, order_data)

            if success:
                print(f"✅ Order for user {user_id} executed successfully: {order_data}")

                # ✅ Save order to database under the correct user before deleting
                order_data["executed_at"] = time.time()
                await save_order_to_db(order_data, db)

            else:
                print(f"❌ Order execution failed for user {user_id}: {order_data}")
                order_data["status"] = "FAILED"
                order_data["retry_count"] = order_data.get("retry_count", 0) + 1

                if order_data["retry_count"] < 3:  # Retry max 3 times
                    print(f"🔄 Retrying order {order_data['orderId']} in 10 seconds...")
                    await asyncio.sleep(10)  # Wait 10 seconds before retrying
                    await redis.rpush(user_key, json.dumps(order_data))  # Save back to Redis

    print(f"🚀 Processed {len(orders_to_process)} orders!")

# ---------------------- 🔹 Execute Orders on Binance 🔹 ----------------------

async def execute_order(client: Client, order_data: dict):
    """
    Sends a real order to Binance API using python-binance.
    """
    try:
        symbol = order_data["symbol"]
        side = order_data["side"]
        order_type = order_data["type"]
        quantity = order_data["quantity"]
        price = order_data.get("price")
        stop_price = order_data.get("stopPrice")

        if order_type == "MARKET":
            response = client.order_market(
                symbol=symbol,
                side=side,
                quantity=quantity
            )

        elif order_type == "LIMIT":
            response = client.order_limit(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                timeInForce="GTC"
            )

        elif order_type in ["STOP_LOSS", "STOP_LOSS_LIMIT"]:
            response = client.create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                stopPrice=stop_price,
                timeInForce="GTC" if order_type == "STOP_LOSS_LIMIT" else None
            )

        print(f"✅ Order executed successfully: {response}")
        return response

    except Exception as e:
        print(f"❌ Binance Order Error: {e}")
        return None
