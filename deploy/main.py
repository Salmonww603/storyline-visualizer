"""
部署版应用入口：单个 FastAPI 服务同时干两件事——
1. 提供 /api/* 后端接口
2. 托管前端构建产物（dist），并处理 Vue Router 的 history 路由刷新

这样前端和后端同源，前端可以用相对路径 /api 调接口，不用写死地址。
启动：uvicorn main:app --host 0.0.0.0 --port $PORT
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from database import engine, Base
import models  # 确保 Base.metadata 知道所有表
from routers import auth_router, storyline_router, event_router

# 建表（SQLite 文件不存在时自动创建）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="故事线可视化平台",
    description="记录与分享你的每一段故事",
    version="2.0.0",
)

# 同源部署，CORS 其实用不上；保留 * 方便本地调试不同端口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(auth_router.router)
app.include_router(storyline_router.router)
app.include_router(event_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# ===== 托管前端静态文件 + SPA 路由回退 =====
# 前端 dist 构建产物放在 static/ 目录
STATIC_DIR = Path(__file__).resolve().parent / "static"

if STATIC_DIR.exists():
    # /assets/xxx.js 这类静态资源直接返回文件
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """Vue Router history 模式：任何非 API 路径都返回 index.html，让前端自己路由。
        这样直接访问 /share/2 或刷新页面不会 404。"""
        # 根路径和未知路径都给 index.html
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        return JSONResponse({"message": "前端未构建"}, status_code=404)
else:
    @app.get("/")
    def root():
        return {"message": "故事线可视化平台 API 运行中（前端未构建）", "docs": "/docs"}


# 直接 python main.py 启动时，从 PORT 环境变量读端口（沙箱注入），默认 3000。
# 把端口读取放进 Python 而不是启动命令，避免 shell 对 $PORT 展开的兼容问题。
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
