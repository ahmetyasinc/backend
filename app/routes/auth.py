from fastapi import APIRouter, HTTPException, Depends, Response
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.models import User
from app.database import get_db
from app.core.auth import create_access_token, create_refresh_token  # JWT fonksiyonlarını içe aktar
import logging

SECRET_KEY = "38842270259879952027900728229105"  # Gerçek projelerde .env dosyasına koymalısın!
ALGORITHM = "HS256"

router = APIRouter()

# Giriş verileri için Pydantic modeli
class LoginRequest(BaseModel):
    username: str
    password: str
    rememberMe: bool = False

# Giriş verileri için Pydantic modeli
class RegisterRequest(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    password: str
    confirmPassword: str

# Refresh token isteği için Pydantic modeli
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
# Logger kullanımı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/api/login/")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Veritabanında kullanıcıyı sorgula
    result = await db.execute(select(User).where(User.name == data.username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre!")

    # Şifre kontrolü (Burada basit bir string kontrolü yaptım, ama bcrypt gibi bir kütüphane kullanmalısın)
    if user.password != data.password:
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre!")

    access_token = create_access_token({"sub": user.name})
    refresh_token = create_refresh_token({"sub": user.name})

    logger.info(f"Kullanıcı giriş yaptı: {user.name}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# Kullanıcı ekleme fonksiyonu
@router.post("/api/register")
async def add_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Aynı e-posta adresi zaten var mı kontrol et
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalars().first()

    if existing_user:
        print(existing_user)
        print(existing_user.email)
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kullanılıyor!")

    # Yeni kullanıcı oluştur
    user = User(name=data.username, email=data.email, password=data.password)
    db.add(user)
    await db.commit()  # Değişiklikleri kaydet
    await db.refresh(user)  # Kullanıcıyı güncelle
    return {"message": "User created successfully", "user": {"id": user.id, "name": user.name, "email": user.email, "password": user.password}}  


@router.post("/api/refresh-token/")
async def refresh_token(request: RefreshTokenRequest, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise HTTPException(status_code=401, detail="Geçersiz refresh token")

        # 🚀 `query()` yerine `execute()` kullanıyoruz
        result = await db.execute(select(User).where(User.name == username))
        user = result.scalars().first()  # `scalars()` ile veriyi alıyoruz

        if not user:
            raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")

        # Yeni access token oluştur
        new_access_token = create_access_token({"sub": user.name})
        return {"access_token": new_access_token, "token_type": "bearer"}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Geçersiz token")
    