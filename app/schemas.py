from pydantic import BaseModel, EmailStr
from typing import Optional

# --- User Schemas ---
# 用於註冊時接收的資料
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # 前端傳來的是明文密碼

# 用於 API 回應時，保護敏感資訊 (如密碼)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True # 讓 Pydantic 能從 SQLAlchemy 物件讀取資料

# --- Token Schemas ---
# 用於登入成功後的回應
class Token(BaseModel):
    access_token: str
    token_type: str

# 用於解析 JWT 權杖內容
class TokenData(BaseModel):
    username: Optional[str] = None

# --- Google Token Schema ---
class GoogleToken(BaseModel):
    credential: str
