# -*- coding: utf-8 -*-
"""
收藏/关注相关数据模型（soccer_server 数据库）
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UserFavorite(Base):
    """用户收藏表（比赛、联赛等）"""
    __tablename__ = 'user_favorites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID
    
    # 收藏类型
    favorite_type = Column(String(20), nullable=False)  # 类型 (match/league/team)
    target_id = Column(Integer, nullable=False)  # 目标ID（比赛ID/联赛ID/球队ID）
    
    # 冗余字段（方便查询显示）
    target_name = Column(String(200), nullable=True)  # 目标名称
    extra_info = Column(Text, nullable=True)  # 额外信息（JSON格式）
    
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_user_type', 'user_id', 'favorite_type'),
        Index('idx_user_target', 'user_id', 'target_id', unique=True),  # 防止重复收藏
    )


class UserFollow(Base):
    """用户关注表（专家、分析师等）"""
    __tablename__ = 'user_follows'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 关注者ID
    follow_type = Column(String(20), nullable=False)  # 关注类型 (expert/analyst/user)
    target_id = Column(Integer, nullable=False)  # 被关注对象ID
    target_name = Column(String(100), nullable=True)  # 被关注对象名称
    
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_user_follow', 'user_id', 'follow_type'),
        Index('idx_user_target', 'user_id', 'target_id', unique=True),
    )
