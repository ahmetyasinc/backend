from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.routes import api_router
from .core.config import settings
from .database import database
import asyncio
from services.order_service import OrderService  # OrderService’i içe aktar

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS ayarları (gerekirse)
origins = ["*"]  # Güvenliğiniz için belirli domain'lere izin verin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Uygulama başlarken OrderService başlat"""
    asyncio.create_task(OrderService.start_order_processing(batch_size=10))


@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()

# API router'ını dahil et
app.include_router(api_router, prefix=settings.API_V1_STR)