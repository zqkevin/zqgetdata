# -*- coding: utf-8 -*-
"""
基础数据模型 - 联赛、球队和通用赔率结构 (公用)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# 比赛类型枚举
class MatchTypeEnum(str, enum.Enum):
    """比赛类型枚举"""
    TCZQ = "tczq"  # 体彩足球
    BJDC = "bjdc"  # 北京单场

# 联赛表 (公用)
class League(Base):
    __tablename__ = 'league'
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, unique=True, nullable=False, index=True)  # 联赛 ID
    league_name = Column(String(100), nullable=False)  # 联赛全称
    league_name_abbr = Column(String(20), nullable=False)  # 联赛简称
    region = Column(String(50))  # 联赛地区
    country = Column(String(50))  # 联赛国家
    href = Column(String(255), nullable=False)  # 联赛链接地址
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 球队信息表 (公用)
class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, unique=True, nullable=False, index=True)  # 球队 ID
    team_code = Column(String(20), nullable=False)  # 球队代码
    team_full_name = Column(String(100), nullable=False)  # 球队全称
    team_short_name = Column(String(20), nullable=False)  # 球队简称
    team_short_en_name = Column(String(20))  # 球队英文简称
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系 - 球队别名
    aliases = relationship('TeamAlias', backref='team', lazy='dynamic', cascade='all, delete-orphan')

# 球队别名字典表 (公用)
class TeamAlias(Base):
    __tablename__ = 'team_alias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)  # 关联到球队 ID
    alias_name = Column(String(100), nullable=False)  # 别名
    source_type = Column(String(20), nullable=False)  # 来源类型 (tczq/bjdc/okooo 等)
    is_primary = Column(Integer, default=0)  # 是否为主别名 (1-是，0-否)
    remark = Column(Text)  # 备注
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)


# ========== 以下是通用赔率模型基类 (Mixin) ==========
# 使用 Mixin 模式，让体彩足球和北京单场可以继承相同的结构

class BaseSpfOdds(object):
    """胜平负赔率基类"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)
    
    win_pl = Column(Float, default=0)  # 主队胜赔率
    draw_pl = Column(Float, default=0)  # 平局赔率
    lose_pl = Column(Float, default=0)  # 客队胜赔率
    winpl_eu = Column(Float, default=0)  # 欧洲平均胜赔率
    drawpl_eu = Column(Float, default=0)  # 欧洲平均平赔率
    losepl_eu = Column(Float, default=0)  # 欧洲平均负赔率
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseHandicapSpfOdds(object):
    """让球胜平负赔率基类"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)
    
    handicap = Column(Float, default=0)  # 让球数
    win_pl = Column(Float, default=0)  # 让球胜赔率
    draw_pl = Column(Float, default=0)  # 让球平赔率
    lose_pl = Column(Float, default=0)  # 让球负赔率
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseTotalGoalOdds(object):
    """总进球赔率基类"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)
    
    goal_0 = Column(Float, default=0)  # 总进球 0
    goal_1 = Column(Float, default=0)  # 总进球 1
    goal_2 = Column(Float, default=0)  # 总进球 2
    goal_3 = Column(Float, default=0)  # 总进球 3
    goal_4 = Column(Float, default=0)  # 总进球 4
    goal_5 = Column(Float, default=0)  # 总进球 5
    goal_6 = Column(Float, default=0)  # 总进球 6
    goal_about = Column(Float, default=0)  # 总进球 7+
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseScoreOdds(object):
    """比分赔率基类"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # 比分赔率
    score_0_0 = Column(Float, default=0)  # 比分 0:0
    score_0_1 = Column(Float, default=0)  # 比分 0:1
    score_0_2 = Column(Float, default=0)  # 比分 0:2
    score_0_3 = Column(Float, default=0)  # 比分 0:3
    score_0_4 = Column(Float, default=0)  # 比分 0:4
    score_0_5 = Column(Float, default=0)  # 比分 0:5
    score_1_0 = Column(Float, default=0)  # 比分 1:0
    score_1_1 = Column(Float, default=0)  # 比分 1:1
    score_1_2 = Column(Float, default=0)  # 比分 1:2
    score_1_3 = Column(Float, default=0)  # 比分 1:3
    score_1_4 = Column(Float, default=0)  # 比分 1:4
    score_1_5 = Column(Float, default=0)  # 比分 1:5
    score_2_0 = Column(Float, default=0)  # 比分 2:0
    score_2_1 = Column(Float, default=0)  # 比分 2:1
    score_2_2 = Column(Float, default=0)  # 比分 2:2
    score_2_3 = Column(Float, default=0)  # 比分 2:3
    score_2_4 = Column(Float, default=0)  # 比分 2:4
    score_2_5 = Column(Float, default=0)  # 比分 2:5
    score_3_0 = Column(Float, default=0)  # 比分 3:0
    score_3_1 = Column(Float, default=0)  # 比分 3:1
    score_3_2 = Column(Float, default=0)  # 比分 3:2
    score_3_3 = Column(Float, default=0)  # 比分 3:3
    score_3_4 = Column(Float, default=0)  # 比分 3:4
    score_3_5 = Column(Float, default=0)  # 比分 3:5
    score_4_0 = Column(Float, default=0)  # 比分 4:0
    score_4_1 = Column(Float, default=0)  # 比分 4:1
    score_4_2 = Column(Float, default=0)  # 比分 4:2
    score_4_3 = Column(Float, default=0)  # 比分 4:3
    score_4_4 = Column(Float, default=0)  # 比分 4:4
    score_4_5 = Column(Float, default=0)  # 比分 4:5
    score_5_0 = Column(Float, default=0)  # 比分 5:0
    score_5_1 = Column(Float, default=0)  # 比分 5:1
    score_5_2 = Column(Float, default=0)  # 比分 5:2
    score_6_0 = Column(Float, default=0)  # 比分 6:0
    score_6_1 = Column(Float, default=0)  # 比分 6:1
    score_7_0 = Column(Float, default=0)  # 比分 7:0
    score_win_about = Column(Float, default=0)  # 胜其他
    score_lose_about = Column(Float, default=0)  # 负其他
    score_draw_about = Column(Float, default=0)  # 平其他
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseHalfTimeFullTimeOdds(object):
    """半全场胜平负赔率基类"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # 半全场胜平负赔率
    half_win_full_win = Column(Float, default=0)  # 半场胜全场胜
    half_win_full_draw = Column(Float, default=0)  # 半场胜全场平
    half_win_full_lose = Column(Float, default=0)  # 半场胜全场负
    half_draw_full_win = Column(Float, default=0)  # 半场平全场胜
    half_draw_full_draw = Column(Float, default=0)  # 半场平全场平
    half_draw_full_lose = Column(Float, default=0)  # 半场平全场负
    half_lose_full_win = Column(Float, default=0)  # 半场负全场胜
    half_lose_full_draw = Column(Float, default=0)  # 半场负全场平
    half_lose_full_lose = Column(Float, default=0)  # 半场负全场负
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseMatchResult(object):
    """赛果记录基类"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # 全场赛果
    home_team_goals = Column(Integer, default=0)  # 主队全场得分
    away_team_goals = Column(Integer, default=0)  # 客队全场得分
    
    # 半场赛果
    half_time_home_goals = Column(Integer, default=0)  # 主队半场得分
    half_time_away_goals = Column(Integer, default=0)  # 客队半场得分
    
    # 赛果类型
    result_type = Column(String(10))  # 赛果类型 (胜/平/负)
    handicap_result = Column(String(10))  # 让球赛果
    total_goals = Column(Integer, default=0)  # 总进球数
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseOddsChangeLog(object):
    """赔率变化历史记录基类"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, nullable=False, index=True)  # 比赛 ID
    odds_table = Column(String(50), nullable=False)  # 赔率表名 (如 tczq_spf_odds)
    odds_record_id = Column(Integer, nullable=False, index=True)  # 赔率记录ID (关联到具体赔率表的主键)
    odds_field = Column(String(50), nullable=False)  # 赔率字段 (如 win_pl)
    old_value = Column(Float, nullable=False)  # 旧值
    new_value = Column(Float, nullable=False)  # 新值
    change_time = Column(DateTime, nullable=False)  # 变化时间
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
