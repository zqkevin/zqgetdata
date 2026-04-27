# -*- coding: utf-8 -*-
"""
系统相关数据模型（soccer_server 数据库）
包含查询日志、系统配置、Token管理等
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class QueryLog(Base):
    """API 查询日志表"""
    __tablename__ = 'query_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)  # 用户ID（可为空，未登录用户）
    username = Column(String(50), nullable=True, index=True)  # 用户名
    endpoint = Column(String(200), nullable=False)  # API 端点
    method = Column(String(10), nullable=False)  # HTTP 方法 (GET/POST等)
    params = Column(Text, nullable=True)  # 请求参数（JSON格式）
    ip_address = Column(String(50), nullable=True)  # IP 地址
    response_status = Column(Integer, nullable=True)  # 响应状态码
    response_time = Column(Float, nullable=True)  # 响应时间（秒）
    error_message = Column(Text, nullable=True)  # 错误信息
    
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_endpoint_created', 'endpoint', 'created_at'),
    )


class ApiToken(Base):
    """API Token 管理表"""
    __tablename__ = 'api_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID
    token = Column(String(500), unique=True, nullable=False)  # JWT Token
    token_type = Column(String(20), default='access')  # token 类型 (access/refresh)
    is_revoked = Column(Boolean, default=False, index=True)  # 是否已撤销
    expires_at = Column(DateTime, nullable=False)  # 过期时间
    
    created_at = Column(DateTime, default=datetime.now)
    revoked_at = Column(DateTime, nullable=True)  # 撤销时间
    
    __table_args__ = (
        Index('idx_user_token', 'user_id', 'is_revoked'),
    )


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)  # 配置键
    config_value = Column(Text, nullable=True)  # 配置值
    description = Column(String(500), nullable=True)  # 配置描述
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_config_key', 'config_key'),
    )
