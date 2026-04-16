# -*- coding: utf-8 -*-
"""
Pytest 全局配置和 fixtures
"""
import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def app_config():
    """应用配置 fixture"""
    from config import config
    return config


@pytest.fixture(scope="session")
def db_engine(app_config):
    """数据库引擎 fixture"""
    from sqlalchemy import create_engine
    db_config = app_config['local']
    engine = create_engine(
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """数据库会话 fixture（每个测试函数独立）"""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db_engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def tczq_collector():
    """体彩足球数据采集器 fixture"""
    from app.crawler.tczq import TczqDataCollector
    return TczqDataCollector()


@pytest.fixture
def jcbk_collector():
    """竞彩篮球数据采集器 fixture"""
    from app.crawler.jcbk import JcbkDataCollector
    return JcbkDataCollector()


@pytest.fixture
def bjdc_collector():
    """北京单场数据采集器 fixture"""
    from app.crawler.bjdc import BjdcDataCollector
    return BjdcDataCollector()


@pytest.fixture
def lottery_collector():
    """数字彩数据采集器 fixture"""
    from app.crawler.lottery import LotteryDataCollector
    return LotteryDataCollector()
