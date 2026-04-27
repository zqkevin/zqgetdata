# -*- coding: utf-8 -*-
"""
北京单场 (BJDC) 数据模型
独立于体彩足球的北京单场相关表
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base_models import Base, League, Team, MatchTypeEnum
from .base_models import (
    BaseSpfOdds,
    BaseHandicapSpfOdds,
    BaseTotalGoalOdds,
    BaseScoreOdds,
    BaseHalfTimeFullTimeOdds,
    BaseMatchResult,
    BaseOddsChangeLog
)

# 北京单场比赛主表
class BjdcMatch(Base):
    __tablename__ = 'bjdc_match'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)  # 比赛 ID
    
    # 期数相关
    issue = Column(String(20), nullable=False, index=True)  # 期数
    match_num = Column(Integer, nullable=False)  # 比赛编号
    match_num_str = Column(String(20))  # 比赛编号字符串，如"周一 001"
    match_week = Column(String(10), nullable=False)  # 比赛星期
    
    # 时间相关
    match_time = Column(DateTime, nullable=False, index=True)  # 比赛时间（包含日期和时分秒）
    
    # 联赛和球队 (关联到公用的 league 和 team 表)
    league_id = Column(Integer, ForeignKey('league.id'))  # 联赛 ID
    home_team_id = Column(Integer, ForeignKey('team.id'))  # 主队 ID
    away_team_id = Column(Integer, ForeignKey('team.id'))  # 客队 ID
    
    # 比赛状态
    status = Column(Integer, default=0, index=True)  # 状态 0-未开始 1-已结束等
    
    # 其他信息
    remark = Column(Text)  # 备注
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('League', backref='bjdc_matches', uselist=False, lazy=True)
    home_team = relationship('Team', foreign_keys=[home_team_id], backref='bjdc_home_matches', uselist=False, lazy=True)
    away_team = relationship('Team', foreign_keys=[away_team_id], backref='bjdc_away_matches', uselist=False, lazy=True)
    
    # 赔率表关系 - 使用 primaryjoin 明确指定连接条件
    spf = relationship(
        'BjdcSpfOdds',
        primaryjoin="and_(BjdcMatch.match_id == foreign(BjdcSpfOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 胜平负赔率
    hh_spf = relationship(
        'BjdcHandicapSpfOdds',
        primaryjoin="and_(BjdcMatch.match_id == foreign(BjdcHandicapSpfOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 让球胜平负赔率
    score = relationship(
        'BjdcScoreOdds',
        primaryjoin="and_(BjdcMatch.match_id == foreign(BjdcScoreOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 比分赔率
    total_goal = relationship(
        'BjdcTotalGoalOdds',
        primaryjoin="and_(BjdcMatch.match_id == foreign(BjdcTotalGoalOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 总进球赔率
    ht_ft = relationship(
        'BjdcHalfTimeFullTimeOdds',
        primaryjoin="and_(BjdcMatch.match_id == foreign(BjdcHalfTimeFullTimeOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 半全场胜平负赔率
    up_down = relationship(
        'BjdcUpDownOdds',
        primaryjoin="and_(BjdcMatch.match_id == foreign(BjdcUpDownOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 上下单双赔率

# 北京单场 - 胜平负赔率表 (继承通用基类)
class BjdcSpfOdds(Base, BaseSpfOdds):
    __tablename__ = 'bjdc_spf_odds'

# 北京单场 - 让球胜平负赔率表 (继承通用基类)
class BjdcHandicapSpfOdds(Base, BaseHandicapSpfOdds):
    __tablename__ = 'bjdc_handicap_spf_odds'

# 北京单场 - 总进球赔率表 (继承通用基类)
class BjdcTotalGoalOdds(Base, BaseTotalGoalOdds):
    __tablename__ = 'bjdc_total_goal_odds'

# 北京单场 - 比分赔率表 (继承通用基类)
class BjdcScoreOdds(Base, BaseScoreOdds):
    __tablename__ = 'bjdc_score_odds'

# 北京单场 - 半全场胜平负赔率表 (继承通用基类)
class BjdcHalfTimeFullTimeOdds(Base, BaseHalfTimeFullTimeOdds):
    __tablename__ = 'bjdc_ht_ft_odds'

# 北京单场 - 上下单双赔率表
class BjdcUpDownOdds(Base):
    __tablename__ = 'bjdc_up_down_odds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)  # 比赛 ID
    
    up_single = Column(Float, default=0)  # 上 + 单
    up_double = Column(Float, default=0)  # 上 + 双
    down_single = Column(Float, default=0)  # 下 + 单
    down_double = Column(Float, default=0)  # 下 + 双
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 北京单场 - 赛果记录表 (继承通用基类)
class BjdcMatchResult(Base, BaseMatchResult):
    __tablename__ = 'bjdc_match_result'

# 北京单场 - 赔率变化历史记录表 (继承通用基类)
class BjdcOddsChangeLog(Base, BaseOddsChangeLog):
    __tablename__ = 'bjdc_odds_change_log'
