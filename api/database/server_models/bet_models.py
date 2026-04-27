# -*- coding: utf-8 -*-
"""
投注相关数据模型（soccer_server 数据库）
包含投注记录、订单等
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class BetRecord(Base):
    """投注记录表"""
    __tablename__ = 'bet_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID
    username = Column(String(50), nullable=True, index=True)  # 用户名（冗余字段，方便查询）
    
    # 投注信息
    match_id = Column(Integer, nullable=False)  # 比赛ID
    match_num_str = Column(String(50), nullable=True)  # 比赛编号
    league_name = Column(String(100), nullable=True)  # 联赛名称
    home_team = Column(String(100), nullable=True)  # 主队
    away_team = Column(String(100), nullable=True)  # 客队
    match_time = Column(DateTime, nullable=True)  # 比赛时间
    
    # 玩法和选项
    bet_type = Column(String(50), nullable=False)  # 投注类型 (spf/handicap_spf/total_goal/score等)
    bet_option = Column(String(50), nullable=False)  # 投注选项 (3/1/0, 胜/平/负等)
    odds = Column(Float, nullable=False)  # 赔率
    handicap = Column(String(20), nullable=True)  # 让球数
    
    # 金额信息
    bet_amount = Column(Float, nullable=False)  # 投注金额
    potential_win = Column(Float, nullable=False)  # 预期奖金
    actual_win = Column(Float, default=0.0)  # 实际奖金（结算后）
    
    # 状态
    status = Column(String(20), default='pending')  # 状态 (pending/won/lost/refunded/cancelled)
    result = Column(String(50), nullable=True)  # 比赛结果
    
    # 其他
    remark = Column(Text, nullable=True)  # 备注
    settled_at = Column(DateTime, nullable=True)  # 结算时间
    
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_match_status', 'match_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
    )


class BetOrder(Base):
    """投注订单表（串关）"""
    __tablename__ = 'bet_orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True)  # 订单号
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID
    username = Column(String(50), nullable=True, index=True)  # 用户名
    
    # 订单信息
    bet_type = Column(String(50), nullable=False)  # 投注类型 (single/multiple) 单式/串关
    multiple_count = Column(Integer, default=1)  # 串关数量（几串几）
    
    # 金额信息
    total_amount = Column(Float, nullable=False)  # 总投注金额
    total_odds = Column(Float, nullable=False)  # 总赔率
    potential_win = Column(Float, nullable=False)  # 预期奖金
    actual_win = Column(Float, default=0.0)  # 实际奖金
    
    # 状态
    status = Column(String(20), default='pending')  # 状态 (pending/won/lost/refunded)
    
    # 其他
    bet_details = Column(Text, nullable=True)  # 投注详情（JSON格式，包含所有注项）
    remark = Column(Text, nullable=True)  # 备注
    settled_at = Column(DateTime, nullable=True)  # 结算时间
    
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_order_no', 'order_no'),
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_status_created', 'status', 'created_at'),
    )
