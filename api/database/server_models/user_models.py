# -*- coding: utf-8 -*-
"""
用户相关数据模型（soccer_server 数据库）
包含用户基本信息、等级、余额等
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表 - 完整用户信息（类似 okooo.com）"""
    __tablename__ = 'api_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)  # 用户名
    hashed_password = Column(String(255), nullable=False)  # 加密后的密码
    email = Column(String(100), nullable=True)  # 邮箱
    phone = Column(String(20), nullable=True)  # 手机号
    
    # 用户资料
    nickname = Column(String(50), nullable=True)  # 昵称
    avatar_url = Column(String(500), nullable=True)  # 头像URL
    gender = Column(String(10), nullable=True)  # 性别 (male/female/other)
    birthday = Column(DateTime, nullable=True)  # 生日
    
    # 等级系统
    level = Column(Integer, default=1)  # 用户等级 (1-100)
    experience = Column(Integer, default=0)  # 经验值
    vip_level = Column(Integer, default=0)  # VIP等级 (0-10)
    
    # 财务信息
    balance = Column(Float, default=0.0)  # 账户余额
    frozen_balance = Column(Float, default=0.0)  # 冻结余额
    total_recharge = Column(Float, default=0.0)  # 累计充值
    total_withdraw = Column(Float, default=0.0)  # 累计提现
    total_bet = Column(Float, default=0.0)  # 累计投注
    total_win = Column(Float, default=0.0)  # 累计中奖
    
    # 积分系统
    points = Column(Integer, default=0)  # 积分
    
    # 状态
    is_active = Column(Boolean, default=True)  # 是否激活
    is_admin = Column(Boolean, default=False)  # 是否管理员
    is_vip = Column(Boolean, default=False)  # 是否VIP
    last_login_at = Column(DateTime, nullable=True)  # 最后登录时间
    last_login_ip = Column(String(50), nullable=True)  # 最后登录IP
    
    # 其他
    remark = Column(Text, nullable=True)  # 备注
    external_link = Column(String(500), nullable=True)  # 外链地址（个人主页等）
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_level', 'level'),
        Index('idx_vip', 'vip_level'),
    )


class UserLevelConfig(Base):
    """用户等级配置表"""
    __tablename__ = 'user_level_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, unique=True, nullable=False, index=True)  # 等级
    level_name = Column(String(50), nullable=False)  # 等级名称（如：青铜、白银、黄金）
    min_experience = Column(Integer, nullable=False)  # 最低经验值
    max_experience = Column(Integer, nullable=True)  # 最高经验值
    icon_url = Column(String(500), nullable=True)  # 等级图标
    benefits = Column(Text, nullable=True)  # 等级权益（JSON格式）
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_level', 'level'),
    )


class UserBalanceLog(Base):
    """用户余额变动日志表"""
    __tablename__ = 'user_balance_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID
    change_type = Column(String(20), nullable=False)  # 变动类型 (recharge/withdraw/bet/win/refund)
    amount = Column(Float, nullable=False)  # 变动金额（正数增加，负数减少）
    balance_before = Column(Float, nullable=False)  # 变动前余额
    balance_after = Column(Float, nullable=False)  # 变动后余额
    description = Column(String(500), nullable=True)  # 描述
    related_id = Column(Integer, nullable=True)  # 关联ID（如投注ID、订单ID）
    
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_type_created', 'change_type', 'created_at'),
    )
