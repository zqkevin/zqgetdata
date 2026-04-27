# -*- coding: utf-8 -*-
"""
FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes.auth import router as auth_router
from routes.tczq import router as tczq_router
from routes.bjdc import router as bjdc_router
from routes.base import router as base_router
from routes.user import router as user_router
from routes.bet import router as bet_router
from routes.favorite import router as favorite_router


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="体育数据采集系统 API 接口",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(auth_router, prefix="/api")
    app.include_router(tczq_router, prefix="/api")
    app.include_router(bjdc_router, prefix="/api")
    app.include_router(base_router, prefix="/api")
    app.include_router(user_router, prefix="/api")
    app.include_router(bet_router, prefix="/api")
    app.include_router(favorite_router, prefix="/api")
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "Welcome to Soccer Data API",
            "version": settings.APP_VERSION,
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy"}
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
