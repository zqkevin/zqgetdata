# -*- coding: utf-8 -*-
"""
标准足球数据库核心配置
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('SF_DB_HOST', 'localhost'),
    'port': int(os.getenv('SF_DB_PORT', '3306')),
    'user': os.getenv('SF_DB_USER', 'soccer_team_db'),
    'password': os.getenv('SF_DB_PASSWORD', '123456'),
    'database': os.getenv('SF_DB_NAME', 'soccer_team_db'),
}

# 创建引擎
engine = create_engine(
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}",
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20,
    echo=False,  # 生产环境设为False
    connect_args={
        'charset': 'utf8mb4'
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话（依赖注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)
