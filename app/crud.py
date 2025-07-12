from sqlalchemy.orm import Session
from . import models, schemas, security

def get_user_by_email(db: Session, email: str):
    """透過 email 查詢使用者"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """透過 username 查詢使用者"""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """建立新使用者"""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_google_id(db: Session, google_id: str):
    """透過 google_id 查詢使用者"""
    return db.query(models.User).filter(models.User.google_id == google_id).first()

def create_user_from_google(db: Session, user_info: dict):
    """使用 Google 資訊建立新使用者"""
    db_user = models.User(
        email=user_info['email'],
        username=user_info.get('name', user_info['email']), # 如果沒有名字，就用 email 當作使用者名稱
        google_id=user_info['sub'],
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
