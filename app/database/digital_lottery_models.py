# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 数字彩票类型表
class DigitalLotteryType(Base):
    __tablename__ = 'digital_lottery_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lottery_code = Column(String(10), unique=True, nullable=False, index=True)  # 彩票类型代码，如04,35,85,350133
    lottery_name = Column(String(20), nullable=False)  # 彩票名称，如七星彩、排列3、超级大乐透、排列5
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 数字彩票开奖信息表
class DigitalLotteryDraw(Base):
    __tablename__ = 'digital_lottery_draws'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 彩票类型关联
    lottery_code = Column(String(10), nullable=False, index=True)  # 彩票类型代码
    lottery_name = Column(String(20), nullable=False)  # 彩票名称
    
    # 开奖基本信息
    draw_num = Column(String(10), nullable=False, index=True)  # 开奖期号，如26002,26004
    draw_time = Column(DateTime, nullable=False, index=True)  # 开奖时间
    draw_result = Column(String(50), nullable=False)  # 开奖结果，如"3 4 5 5 9 8 9"或"8 7 8"
    unsorted_draw_result = Column(String(50))  # 未排序的开奖结果（用于排列3/5）
    
    # 奖池信息
    pool_balance_after_draw = Column(String(20))  # 开奖后奖池金额
    
    # 销售信息
    sale_begin_time = Column(DateTime)  # 销售开始时间
    sale_end_time = Column(DateTime)  # 销售结束时间
    
    # 其他信息
    draw_pdf_url = Column(String(100))  # 开奖PDF链接
    is_verified = Column(Integer, default=0)  # 是否已验证（0未验证，1已验证）
    rule_type = Column(Integer)  # 规则类型
    equipment_count = Column(Integer)  # 设备数量
    notice_flag = Column(Integer)  # 通知标志
    notice_show_flag = Column(Integer)  # 通知显示标志
    
    # 关联奖级信息
    prize_levels = relationship("DigitalLotteryPrize", back_populates="lottery_draw", cascade="all, delete-orphan")
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 数字彩票奖级信息表
class DigitalLotteryPrize(Base):
    __tablename__ = 'digital_lottery_prizes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联开奖信息
    draw_id = Column(Integer, ForeignKey('digital_lottery_draws.id'), nullable=False, index=True)
    lottery_draw = relationship("DigitalLotteryDraw", back_populates="prize_levels")
    
    # 奖级基本信息
    prize_level = Column(String(20), nullable=False)  # 奖级名称，如"一等奖"、"直选"、"组选3"
    award_type = Column(Integer)  # 奖项类型
    group = Column(String(10))  # 奖级分组
    lottery_condition = Column(String(50))  # 中奖条件
    sort = Column(Integer)  # 排序
    
    # 中奖信息
    stake_count = Column(String(20), nullable=False)  # 中奖注数
    stake_amount = Column(String(20), nullable=False)  # 单注奖金
    stake_amount_format = Column(String(20))  # 格式化后的单注奖金
    total_prize_amount = Column(String(20), nullable=False)  # 总奖金金额
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 数字彩票历史开奖记录辅助表（用于存储期号列表）
class DigitalLotteryTermList(Base):
    __tablename__ = 'digital_lottery_term_lists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 彩票类型关联
    lottery_code = Column(String(10), nullable=False, index=True)  # 彩票类型代码
    lottery_name = Column(String(20), nullable=False)  # 彩票名称
    
    # 期号列表信息
    term_list = Column(Text)  # 期号列表，以JSON格式存储
    term_count = Column(Integer, default=0)  # 期号数量
    
    # 更新信息
    last_update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)