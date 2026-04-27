# -*- coding: utf-8 -*-
"""
体彩足球 (TCZQ) 数据模型
独立于北京单场的体彩足球相关表
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

# 体彩足球比赛主表
class TczqMatch(Base):
    __tablename__ = 'tczq_match'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)  # 比赛 ID
    
    # 期数相关
    issue = Column(String(20), nullable=False, index=True)  # 期数
    match_num = Column(Integer, nullable=False)  # 比赛编号
    match_num_str = Column(String(20))  # 比赛编号字符串，如"周一 001"
    match_week = Column(String(10), nullable=False)  # 比赛星期
    
    # 时间相关
    match_time = Column(DateTime, nullable=False, index=True)  # 比赛时间
    match_date = Column(String(10))  # 比赛日期
    
    # 联赛和球队 (关联到公用的 league 和 team 表)
    league_id = Column(Integer, ForeignKey('league.id'))  # 联赛 ID
    home_team_id = Column(Integer, ForeignKey('team.id'))  # 主队 ID
    away_team_id = Column(Integer, ForeignKey('team.id'))  # 客队 ID
    
    # 跨系统关联
    bjdc_match_id = Column(Integer, nullable=True, index=True)  # 匹配到的BJDC比赛ID（避免重复匹配）
    
    # 比赛状态
    status = Column(Integer, default=0, index=True)  # 状态 0-未开始 1-已结束等
    
    # 其他信息
    remark = Column(Text)  # 备注
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('League', backref='tczq_matches', uselist=False, lazy=True)
    home_team = relationship('Team', foreign_keys=[home_team_id], backref='tczq_home_matches', uselist=False, lazy=True)
    away_team = relationship('Team', foreign_keys=[away_team_id], backref='tczq_away_matches', uselist=False, lazy=True)
    
    # 赔率表关系 - 使用 primaryjoin 明确指定连接条件
    spf = relationship(
        'TczqSpfOdds',
        primaryjoin="and_(TczqMatch.match_id == foreign(TczqSpfOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 胜平负赔率
    hh_spf = relationship(
        'TczqHandicapSpfOdds',
        primaryjoin="and_(TczqMatch.match_id == foreign(TczqHandicapSpfOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 让球胜平负赔率
    score = relationship(
        'TczqScoreOdds',
        primaryjoin="and_(TczqMatch.match_id == foreign(TczqScoreOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 比分赔率
    total_goal = relationship(
        'TczqTotalGoalOdds',
        primaryjoin="and_(TczqMatch.match_id == foreign(TczqTotalGoalOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 总进球赔率
    ht_ft = relationship(
        'TczqHalfTimeFullTimeOdds',
        primaryjoin="and_(TczqMatch.match_id == foreign(TczqHalfTimeFullTimeOdds.match_id))",
        backref='match',
        uselist=False,
        lazy=True
    )  # 半全场胜平负赔率

# 体彩足球 - 胜平负赔率表 (继承通用基类)
class TczqSpfOdds(Base, BaseSpfOdds):
    __tablename__ = 'tczq_spf_odds'

# 体彩足球 - 让球胜平负赔率表 (继承通用基类)
class TczqHandicapSpfOdds(Base, BaseHandicapSpfOdds):
    __tablename__ = 'tczq_handicap_spf_odds'

# 体彩足球 - 总进球赔率表 (继承通用基类)
class TczqTotalGoalOdds(Base, BaseTotalGoalOdds):
    __tablename__ = 'tczq_total_goal_odds'

# 体彩足球 - 比分赔率表 (继承通用基类)
class TczqScoreOdds(Base, BaseScoreOdds):
    __tablename__ = 'tczq_score_odds'

# 体彩足球 - 半全场胜平负赔率表 (继承通用基类)
class TczqHalfTimeFullTimeOdds(Base, BaseHalfTimeFullTimeOdds):
    __tablename__ = 'tczq_ht_ft_odds'

# 体彩足球 - 赛果记录表 (继承通用基类)
class TczqMatchResult(Base, BaseMatchResult):
    __tablename__ = 'tczq_match_result'

# 体彩足球 - 赔率变化历史记录表 (继承通用基类)
class TczqOddsChangeLog(Base, BaseOddsChangeLog):
    __tablename__ = 'tczq_odds_change_log'
