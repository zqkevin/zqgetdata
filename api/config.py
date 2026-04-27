# -*- coding: utf-8 -*-
"""
API 配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "Soccer Data API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置 - soccer_data（体育数据，只读）
    DATA_DB_HOST: str = "127.0.0.1"
    DATA_DB_PORT: int = 3306
    DATA_DB_USER: str = "soccer"
    DATA_DB_PASSWORD: str = "123456"
    DATA_DB_NAME: str = "soccer_data"
    
    # 数据库配置 - soccer_server（API服务，用户/日志等）
    SERVER_DB_HOST: str = "127.0.0.1"
    SERVER_DB_PORT: int = 3306
    SERVER_DB_USER: str = "soccer_server"
    SERVER_DB_PASSWORD: str = "pety93033"
    SERVER_DB_NAME: str = "soccer_server"
    
    # JWT 认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
