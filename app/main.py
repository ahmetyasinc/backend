from fastapi import FastAPI, HTTPException
from app.routes.user import router as user_router
from app.routes.auth import router as auth_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(user_router)  # Router'ı FastAPI'ye dahil et!
app.include_router(auth_router)  # Router'ı FastAPI'ye dahil et!


# CORS Middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Güvenlik için sadece frontend URL'sini koy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/trades")
def get_trades():
    sample_trades = [
        {"id": 1, "symbol": "BTCUSDT", "side": "buy", "price": 50000, "quantity": 0.1},
        {"id": 2, "symbol": "ETHUSDT", "side": "sell", "price": 3500, "quantity": 1.5},
    ]
    return {"trades": sample_trades}

@app.get("/api/hero-infos")
def get_hero_infos():
    user_count = 8
    trader_count = 3
    strategy_count = 5
    bot_count = 2
    hero_infos = {
        "user_count": user_count,
        "trader_count": trader_count,
        "strategy_count": strategy_count,
        "bot_count": bot_count
    }
    return hero_infos

# test için
@app.get("/api/fake-unauthorized/")
def fake_unauthorized():
    raise HTTPException(status_code=401, detail="Unauthorized")
