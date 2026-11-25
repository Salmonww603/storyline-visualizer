"""
FastAPI 应用入口。
启动：uvicorn main:app --reload --port 8000
接口文档：http://localhost:8000/docs （FastAPI 自动生成，Swagger UI）
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models  # 导入模型，确保 Base.metadata 知道所有表
from routers import auth_router, storyline_router, event_router

# 创建数据库表（如果不存在）——开发期方便，生产环境用 Alembic 迁移
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="故事线可视化平台 API",
    description="支持用户注册登录、故事线与事件管理、公开发现",
    version="2.0.0",
)

# CORS 配置：允许前端（localhost 各端口）跨域调用
# 生产环境应改成具体域名，而不是 "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册三个路由模块
app.include_router(auth_router.router)
app.include_router(storyline_router.router)
app.include_router(event_router.router)


@app.get("/")
def root():
    """根路径：健康检查，确认后端活着"""
    return {"message": "故事线可视化平台 API 运行中", "docs": "/docs"}


@app.get("/health")
def health():
    """健康检查接口（部署/监控用）"""
    return {"status": "ok"}
