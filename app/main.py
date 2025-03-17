from fastapi import FastAPI, HTTPException, Depends
from app.routes.user import router as user_router
from app.routes.auth import router as auth_router
from app.routes.profile.indicator.indicator_data import protected_router as indicator_data_router
from app.routes.profile.indicator.indicator import protected_router as indicator_router
from app.routes.profile.indicator.websocket_binance import websocket_router as websocket_binance_router


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# USER ROUTES
app.include_router(user_router)
app.include_router(auth_router)
# INDICATOR ROUTES
app.include_router(websocket_binance_router)
app.include_router(indicator_data_router)
app.include_router(indicator_router) 


# CORS Middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Güvenlik için sadece frontend URL'sini koy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"status": "ok"}



@app.get("/api/hero-infos/")
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
