from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from . import crud, models, schemas, security
from .database import engine, get_db

# 讓 SQLAlchemy 在啟動時根據 models.py 建立所有資料表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="購票系統 API - 登入/註冊模組",
    description="提供使用者註冊與登入功能"
)

# 掛載 static 資料夾
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- 提供前端頁面 ---
@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_index():
    return "static/index.html"


# --- 註冊 API ---
@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    處理使用者註冊。
    - 接收使用者名稱、Email 和密碼。
    - 檢查使用者名稱或 Email 是否已被註冊。
    - 成功後將使用者資料存入資料庫。
    """
    # 檢查使用者是否已存在
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 這裡可以加上驗證碼或 reCAPTCHA 的後端驗證邏輯
    # if not verify_captcha(user.captcha_token):
    #     raise HTTPException(status_code=400, detail="Invalid CAPTCHA")

    return crud.create_user(db=db, user=user)


# --- 登入 API ---
@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    處理使用者登入，成功後回傳 JWT Token。
    - 使用 OAuth2PasswordRequestForm，前端需用 form-data 格式傳送 `username` 和 `password`。
    - 驗證使用者帳號密碼。
    - 產生 JWT access token。
    """
    # 這裡可以加上驗證碼的後端驗證邏輯
    # ...

    user = security.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Google 登入 API ---
@app.post("/auth/google", response_model=schemas.Token, tags=["Authentication"])
def login_with_google(token_data: schemas.GoogleToken, db: Session = Depends(get_db)):
    """
    處理 Google 登入。
    - 接收來自 Google 的 ID Token。
    - 驗證 Token 有效性。
    - 如果使用者是第一次登入，自動建立帳號。
    - 回傳內部的 JWT Token。
    """
    google_user_info = security.verify_google_token(token_data.credential)
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    # 檢查使用者是否已存在
    user = crud.get_user_by_google_id(db, google_id=google_user_info['sub'])

    # 如果使用者不存在，就用 Google 資訊建立新使用者
    if not user:
        # 檢查 email 是否已被註冊
        existing_user_by_email = crud.get_user_by_email(db, email=google_user_info['email'])
        if existing_user_by_email:
            # 如果 email 已被註冊，但沒有連結 Google ID，可以選擇在這裡引導使用者合併帳號
            # 目前為了簡單起見，我們先拋出錯誤
            raise HTTPException(
                status_code=400,
                detail="Email already registered with a different account. Please log in with your password."
            )
        user = crud.create_user_from_google(db, user_info=google_user_info)

    # 產生 JWT token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}