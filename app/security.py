from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

from . import crud, models

load_dotenv()

# --- 金鑰與設定管理 ---
SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not SECRET_KEY or not GOOGLE_CLIENT_ID:
    raise ValueError("Missing SECRET_KEY or GOOGLE_CLIENT_ID from environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token 30 分鐘後過期


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證明文密碼與雜湊密碼是否相符"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """將明文密碼進行雜湊"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """建立 JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """使用者認證：檢查使用者是否存在且密碼是否正確"""
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def verify_google_token(token: str) -> Optional[dict]:
    """驗證 Google ID Token"""
    try:
        # 驗證 token
        id_info = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID
        )
        return id_info
    except ValueError:
        # Token 無效
        return None