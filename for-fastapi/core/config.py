import os
from dotenv import load_dotenv

# ✅ Load variables from .env file
load_dotenv()

# ✅ Environment Variables (Loaded from .env)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/trading_db")
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ✅ Print Config on Startup (Optional)
print(f"🚀 Config Loaded: REDIS_URL={REDIS_URL}, DATABASE_URL={DATABASE_URL}, BINANCE_TESTNET={BINANCE_TESTNET}")
