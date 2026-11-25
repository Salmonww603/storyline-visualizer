"""
部署版数据库连接：默认 SQLite（沙箱自带，无需外部服务）。
本地开发版用的是 MySQL，两套配置分开，互不干扰。
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库文件放在 server 目录下；线上沙箱可写当前目录
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "storyline.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 允许用 DATABASE_URL 覆盖（方便测试），默认 SQLite 文件
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

# SQLite 需要 check_same_thread=False：FastAPI 多线程请求会共用连接
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
