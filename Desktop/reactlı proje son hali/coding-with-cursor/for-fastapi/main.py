from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import api_router
from .core.config import settings
from .core.database import database

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

# Veritabanı bağlantısı (gerekirse)
@app.on_event("startup")
async def startup_event():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()

# API router'ını dahil et
app.include_router(api_router, prefix=settings.API_V1_STR)