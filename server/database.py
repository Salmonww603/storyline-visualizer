"""
数据库连接配置。
所有数据库操作都通过这里的 engine 和 SessionLocal。
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 从 .env 文件加载环境变量（.env 已加入 .gitignore，不会上传到 git）
load_dotenv()

# 数据库连接字符串从环境变量读取，绝不硬编码密码在代码里
# 格式：mysql+pymysql://用户名:密码@主机:端口/数据库名
DATABASE_URL = os.getenv("DATABASE_URL")

# 创建引擎：SQLAlchemy 的核心，负责管理连接池
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 每次取连接前先 ping 一下，避免拿到断开的旧连接
    echo=False,          # 改成 True 可以在控制台看到所有 SQL 语句（调试用）
)

# 会话工厂：每次请求创建一个 session，操作完关闭
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类：所有数据模型都继承它
Base = declarative_base()


def get_db():
    """
    依赖注入函数：FastAPI 每个请求调用它拿一个数据库会话。
    yield 之后的代码在请求结束时执行，保证 session 一定被关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
