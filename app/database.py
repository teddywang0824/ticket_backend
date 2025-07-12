from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 使用 SQLite，它會在本機建立一個 .db 的檔案
SQLALCHEMY_DATABASE_URL = "sqlite:///./member.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # "check_same_thread": False 是 SQLite 特有的設定
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency: 提供一個資料庫 session 給 API 路徑函式使用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()