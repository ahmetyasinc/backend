from fastapi import Request, Response, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "38842270259879952027900728229105"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 saat
REFRESH_TOKEN_EXPIRE_DAYS = 7   # 7 gün

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):    
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ⬇️ Fonksiyonu async hale getirdik
async def verify_token(request: Request, response: Response):
    auth_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not auth_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id

    except ExpiredSignatureError:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Token expired, and no refresh token provided")

        try:
            refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = refresh_payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            new_access_token = create_access_token({"sub": user_id})
            # ✅ Doğru kullanım
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                max_age=60 * ACCESS_TOKEN_EXPIRE_MINUTES,
                samesite="Lax",
                path="/"
            )
            return user_id

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
