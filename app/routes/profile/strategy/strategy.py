from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.models.profile.strategy.strategy import Strategy
from app.models.profile.strategy.strategies_favorite import StrategiesFavorite
from sqlalchemy.future import select
from app.database import get_db
from app.schemas.strategy.strategy import StrategyCreate, StrategyUpdate
from fastapi import HTTPException

protected_router = APIRouter()

@protected_router.get("/api/all-strategies/")
async def get_all_strategies(
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Tüm türdeki indikatörleri (kişisel, teknik, topluluk) tek API ile döner."""

    user_id = int(user_id)

    # 1. Kullanıcının kişisel indikatörleri
    user_result = await db.execute(
        select(
            Strategy.id,
            Strategy.name,
            Strategy.code,
            Strategy.created_at,
            Strategy.public,
            StrategiesFavorite.id.isnot(None).label("favorite")
        )
        .outerjoin(StrategiesFavorite,
                   (StrategiesFavorite.strategy_id == Strategy.id) & 
                   (StrategiesFavorite.user_id == user_id))
        .where(Strategy.user_id == user_id)
    )
    personal = user_result.mappings().all()

    # 2. Teknik (tecnic) indikatörler
    tecnic_result = await db.execute(
        select(
            Strategy.id,
            Strategy.name,
            Strategy.code,
            Strategy.public,
            Strategy.tecnic,
            StrategiesFavorite.id.isnot(None).label("favorite")
        )
        .outerjoin(StrategiesFavorite,
                   (StrategiesFavorite.strategy_id == Strategy.id) & 
                   (StrategiesFavorite.user_id == user_id))
        .where(Strategy.tecnic == True)
    )
    tecnic = tecnic_result.mappings().all()

    # 3. Topluluk (public) indikatörler
    public_result = await db.execute(
        select(
            Strategy.id,
            Strategy.name,
            Strategy.code,
            Strategy.public,
            Strategy.tecnic,
            StrategiesFavorite.id.isnot(None).label("favorite")
        )
        .outerjoin(StrategiesFavorite,
                   (StrategiesFavorite.strategy_id == Strategy.id) & 
                   (StrategiesFavorite.user_id == user_id))
        .where(Strategy.public == True)
    )
    public = public_result.mappings().all()

    return {
        "personal_strategies": [dict(row) for row in personal],
        "tecnic_strategies": [dict(row) for row in tecnic],
        "public_strategies": [dict(row) for row in public],
    }


@protected_router.get("/api/public-strategies/")
async def get_public_strategies(
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
    ):
    """Public olan tüm strateji getirir."""
    
    result = await db.execute(
        select(Strategy.id,
                Strategy.name,
                Strategy.code,
                #Strategy.created_at,
                Strategy.public,
                Strategy.tecnic,
               StrategiesFavorite.id.isnot(None).label("favorite")  # Eğer favori varsa True, yoksa False döner
               )
               .outerjoin(StrategiesFavorite,  # LEFT JOIN işlemi
                   (StrategiesFavorite.strategy_id == Strategy.id) &
                   (StrategiesFavorite.user_id == int(user_id)))
               .where(Strategy.public == True)
    )
    public_strategies = result.mappings().all()

    return {"public_strategies": public_strategies}

@protected_router.get("/api/tecnic-strategies/")
async def get_tecnic_strategies(
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
    ):
    """Public olan tüm indikatörleri getirir."""
    
    result = await db.execute(
        select(Strategy.id,
                Strategy.name,
                Strategy.code,
                #Strategy.created_at,
                Strategy.public,
                Strategy.tecnic,
               StrategiesFavorite.id.isnot(None).label("favorite")  # Eğer favori varsa True, yoksa False döner
               )
               .outerjoin(StrategiesFavorite,  # LEFT JOIN işlemi
                   (StrategiesFavorite.strategy_id == Strategy.id) &
                   (StrategiesFavorite.user_id == int(user_id)))
               .where(Strategy.tecnic == True)
    )
    public_strategies = result.mappings().all()

    return {"tecnic_strategies": public_strategies}

@protected_router.get("/api/get-strategies/")
async def get_strategies(
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcının tüm strateji JSON formatında getirir.
    Eğer bir strateji favori olarak işaretlenmişse, 'favorite': true olarak döner.
    """
    # Kullanıcının tüm strateji çek ve favori olup olmadığını kontrol et
    result = await db.execute(
        select(
            Strategy.id,
            Strategy.name,
            Strategy.code,
            Strategy.created_at,
            Strategy.public,
            StrategiesFavorite.id.isnot(None).label("favorite")  # Eğer favori varsa True, yoksa False döner
        )
        .outerjoin(StrategiesFavorite,  # LEFT JOIN işlemi
                   (StrategiesFavorite.strategy_id == Strategy.id) &
                   (StrategiesFavorite.user_id == int(user_id)))
        .where(Strategy.user_id == int(user_id))
    )

    strategies = result.mappings().all()

    return {"strategies": [dict(row) for row in strategies]}

@protected_router.post("/api/add-strategy/")
async def create_strategy(
    strategy_data: StrategyCreate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Kullanıcı için yeni bir strateji oluşturur. Eğer aynı isimde strateji varsa hata döner."""
    
    result = await db.execute(select(Strategy).where(Strategy.user_id == int(user_id), Strategy.name == strategy_data.name))
    existing_strategy = result.scalars().first()

    if existing_strategy:
        raise HTTPException(status_code=400, detail="Bu isimde bir strateji zaten mevcut!")

    # Yeni strateji oluştur
    new_strategy = Strategy(
        user_id= int(user_id),
        name=strategy_data.name,
        code=strategy_data.code,
    )
    db.add(new_strategy)
    await db.commit()
    await db.refresh(new_strategy)

    return {
        "id": new_strategy.id,
        "name": new_strategy.name,
        "code": new_strategy.code,
        "tecnic": new_strategy.tecnic,
        "public": new_strategy.public,
        "favorite": False
    }

@protected_router.put("/api/edit-strategy/")
async def update_strategy(
    strategy_data: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Belirtilen strateji bilgilerini günceller. Eğer strateji bulunamazsa hata döner."""
    
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_data.id, Strategy.user_id == int(user_id)))
    strategy = result.scalars().first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found!")

    # Güncellenmesi gereken alanları değiştir
    strategy.name = strategy_data.name
    strategy.code = strategy_data.code

    await db.commit()
    await db.refresh(strategy)

    return {"message": "Strategy updated successfully", "strategy": strategy}

@protected_router.delete("/api/delete-strategy/{strategy_id}/")
async def delete_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: dict = Depends(verify_token)
):
    """Belirtilen strateji siler. Eğer strateji bulunamazsa hata döner."""
    
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == int(user_id)))
    strategy = result.scalars().first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found!")

    await db.delete(strategy)
    await db.commit()

    return {"message": "Strategy deleted successfully"}
