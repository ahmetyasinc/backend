from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# Gizli anahtar ve algoritma
SECRET_KEY = "38842270259879952027900728229105"  # Gerçek projelerde .env dosyasına koymalısın!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token süresi (30 dakika)
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token süresi (7 gün)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Kullanıcı için JWT access token oluşturur. """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES))
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

def verify_token(token: str):
    """ JWT token doğrulama ve çözme işlemi """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Token içeriğini döndür
    except JWTError:
        return None  # Token geçersizse None döndür
