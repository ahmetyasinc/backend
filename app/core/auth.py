from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Cookie, Request
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

# Gizli anahtar ve algoritma
SECRET_KEY = "38842270259879952027900728229105"  # Gerçek projelerde .env dosyasına koymalısın!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Access token süresi (60 dakika)
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token süresi (7 gün)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Kullanıcı için JWT access token oluşturur. """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Kullanıcı için JWT refresh token oluşturur. """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(request:Request):
    auth_token = request.cookies.get("access_token")
    if not auth_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id  # Kullanıcıyı API içinde kullanılabilir hale getir
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")
