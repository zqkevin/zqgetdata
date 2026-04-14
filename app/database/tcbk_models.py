# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 联赛表
class TcbkLeague(Base):
    __tablename__ = 'tcbk_league'
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, unique=True, nullable=False, index=True)  # 联赛ID
    league_name = Column(String(50), nullable=False)  # 联赛全称
    league_name_abbr = Column(String(20), nullable=False)  # 联赛简称
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 体彩篮球对阵主表
class TcbkMatch(Base):
    __tablename__ = 'tcbk_match'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)  # 比赛ID
    match_num = Column(Integer)  # 比赛编号
    match_num_str = Column(String(20))  # 比赛编号字符串，如"周一001"
    match_num_date = Column(String(10))  # 比赛日期编号
    match_week = Column(String(10))  # 比赛星期
    match_date = Column(String(20))  # 比赛日期
    match_time = Column(String(20))  # 比赛时间
    business_date = Column(String(20))  # 业务日期
    
    league_id = Column(Integer, ForeignKey('tcbk_league.league_id'))  # 联赛ID，关联到联赛表
    
    home_team_id = Column(Integer)  # 主队ID
    home_team_code = Column(String(20))  # 主队代码
    home_team_all_name = Column(String(50))  # 主队全称
    home_team_abb_name = Column(String(20))  # 主队简称
    home_team_rank = Column(String(20))  # 主队排名
    
    away_team_id = Column(Integer)  # 客队ID
    away_team_code = Column(String(20))  # 客队代码
    away_team_all_name = Column(String(50))  # 客队全称
    away_team_abb_name = Column(String(20))  # 客队简称
    away_team_rank = Column(String(20))  # 客队排名
    
    base_home_team_id = Column(Integer)  # 基础主队ID
    base_away_team_id = Column(Integer)  # 基础客队ID
    
    match_name = Column(String(50))  # 比赛名称
    group_name = Column(String(50))  # 分组名称
    
    match_status = Column(String(20))  # 比赛状态，如"Selling"
    sell_status = Column(Integer)  # 销售状态
    is_hot = Column(Integer)  # 是否热门
    is_hide = Column(Integer)  # 是否隐藏
    betting_single = Column(Integer)  # 单场投注
    betting_all_up = Column(Integer)  # 串关投注
    
    back_color = Column(String(20))  # 背景颜色
    remark = Column(Text)  # 备注
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('TcbkLeague', backref='matches', uselist=False, lazy=True)
    
    # 一对多关系
    spf = relationship('TcbkSpf', backref='match', uselist=False, lazy=True)
    rfsf = relationship('TcbkRfsf', backref='match', uselist=False, lazy=True)
    dxf = relationship('TcbkDxf', backref='match', uselist=False, lazy=True)
    sfc = relationship('TcbkSfc', backref='match', uselist=False, lazy=True)
    result = relationship('TcbkResult', backref='match', uselist=False, lazy=True)

# 胜负赔率表 (spf)
class TcbkSpf(Base):
    __tablename__ = 'tcbk_spf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tcbk_match.match_id'), unique=True, nullable=False)
    
    # 胜负赔率
    h = Column(Float)  # 主队胜赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新

# 让分胜负赔率表 (rfsf)
class TcbkRfsf(Base):
    __tablename__ = 'tcbk_rfsf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tcbk_match.match_id'), unique=True, nullable=False)
    
    # 让分胜负赔率
    goal_line = Column(Float)  # 让分数值
    goal_line_str = Column(String(10))  # 让分数值字符串
    
    h = Column(Float)  # 主队胜赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新

# 大小分赔率表 (dxf)
class TcbkDxf(Base):
    __tablename__ = 'tcbk_dxf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tcbk_match.match_id'), unique=True, nullable=False)
    
    # 大小分赔率
    goal_line = Column(Float)  # 大小分盘口
    goal_line_str = Column(String(10))  # 大小分盘口字符串
    
    over = Column(Float)  # 大分赔率
    under = Column(Float)  # 小分赔率
    
    overf = Column(Integer)  # 大分赔率变化
    underf = Column(Integer)  # 小分赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新

# 胜分差赔率表 (sfc)
class TcbkSfc(Base):
    __tablename__ = 'tcbk_sfc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tcbk_match.match_id'), unique=True, nullable=False)
    
    # 胜分差赔率 - 主队胜
    h1 = Column(Float)  # 主队胜1-5分
    h2 = Column(Float)  # 主队胜6-10分
    h3 = Column(Float)  # 主队胜11-15分
    h4 = Column(Float)  # 主队胜16-20分
    h5 = Column(Float)  # 主队胜21-25分
    h6 = Column(Float)  # 主队胜26+分
    
    # 胜分差赔率 - 客队胜
    a1 = Column(Float)  # 客队胜1-5分
    a2 = Column(Float)  # 客队胜6-10分
    a3 = Column(Float)  # 客队胜11-15分
    a4 = Column(Float)  # 客队胜16-20分
    a5 = Column(Float)  # 客队胜21-25分
    a6 = Column(Float)  # 客队胜26+分
    
    # 赔率变化
    h1f = Column(Integer)  # 主队胜1-5分赔率变化
    h2f = Column(Integer)  # 主队胜6-10分赔率变化
    h3f = Column(Integer)  # 主队胜11-15分赔率变化
    h4f = Column(Integer)  # 主队胜16-20分赔率变化
    h5f = Column(Integer)  # 主队胜21-25分赔率变化
    h6f = Column(Integer)  # 主队胜26+分赔率变化
    
    a1f = Column(Integer)  # 客队胜1-5分赔率变化
    a2f = Column(Integer)  # 客队胜6-10分赔率变化
    a3f = Column(Integer)  # 客队胜11-15分赔率变化
    a4f = Column(Integer)  # 客队胜16-20分赔率变化
    a5f = Column(Integer)  # 客队胜21-25分赔率变化
    a6f = Column(Integer)  # 客队胜26+分赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新

# 竞彩篮球 - 赔率变化历史记录表
class TcbkOddsChangeLog(Base):
    """
    竞彩篮球赔率波动日志表
    记录每次赔率变化的详细信息（增量式记录）
    """
    __tablename__ = 'bk_odds_change_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, nullable=False, index=True)  # 比赛 ID
    odds_table = Column(String(50), nullable=False)  # 赔率表名 (如 tcbk_spf, tcbk_dxf)
    odds_record_id = Column(Integer, nullable=False, index=True)  # 赔率记录ID (关联到具体赔率表的主键)
    odds_field = Column(String(50), nullable=False)  # 赔率字段 (如 h, a, over, under)
    old_value = Column(Float, nullable=False)  # 旧值
    new_value = Column(Float, nullable=False)  # 新值
    change_time = Column(DateTime, nullable=False)  # 变化时间
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)

# 比赛赛果表
class TcbkResult(Base):
    __tablename__ = 'tcbk_result'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tcbk_match.match_id'), unique=True, nullable=False)
    
    # 赛果基本信息
    match_result_status = Column(String(20))  # 比赛结果状态
    pool_status = Column(String(20))  # 奖池状态
    result_status = Column(String(20))  # 结果状态
    win_flag = Column(String(10))  # 获胜方 H-主队 A-客队
    
    # 比分信息
    half_score = Column(String(20))  # 半场比分
    full_score = Column(String(20))  # 全场比分
    home_score = Column(Integer)  # 主队得分
    away_score = Column(Integer)  # 客队得分
    score_diff = Column(Integer)  # 分差
    
    # 球队信息
    home_team = Column(String(50))  # 主队名称
    away_team = Column(String(50))  # 客队名称
    all_home_team = Column(String(50))  # 主队全称
    all_away_team = Column(String(50))  # 客队全称
    
    # 联赛信息
    league_id = Column(Integer, ForeignKey('tcbk_league.league_id'))  # 联赛ID，关联到联赛表
    league_back_color = Column(String(20))  # 联赛背景颜色
    
    # 投注信息
    betting_single = Column(Integer)  # 单场投注状态
    is_cancel = Column(Integer)  # 是否取消
    
    # 玩法结果
    spf_result = Column(String(10))  # 胜负结果
    rfsf_result = Column(String(10))  # 让分胜负结果
    dxf_result = Column(String(10))  # 大小分结果
    sfc_result = Column(String(10))  # 胜分差结果
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('TcbkLeague', backref='results', uselist=False, lazy=True)

# 比赛玩法结果表（matchResultList）
class TcbkMatchResult(Base):
    __tablename__ = 'tcbk_match_result'
    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey('tcbk_result.id'), nullable=False)
    
    code = Column(String(20))  # 玩法代码
    combination = Column(String(20))  # 组合
    combination_desc = Column(String(50))  # 组合描述
    goal_line = Column(String(20))  # 让球数/大小分
    line_status = Column(String(20))  # 线路状态
    match_id = Column(Integer)  # 比赛ID
    odds = Column(String(20))  # 赔率
    odds_type = Column(String(10))  # 赔率类型
    pool_id = Column(Integer)  # 奖池ID
    pool_totals = Column(String(20))  # 奖池总额
    refund_status = Column(String(10))  # 退款状态
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 赔率历史主表（oddsHistory）
class TcbkOddsHistory(Base):
    __tablename__ = 'tcbk_odds_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tcbk_match.match_id'), nullable=False)
    
    # 比赛基本信息
    home_team_id = Column(Integer)  # 主队ID
    away_team_id = Column(Integer)  # 客队ID
    home_team_all_name = Column(String(50))  # 主队全称
    home_team_abb_name = Column(String(20))  # 主队简称
    away_team_all_name = Column(String(50))  # 客队全称
    away_team_abb_name = Column(String(20))  # 客队简称
    league_id = Column(Integer, ForeignKey('tcbk_league.league_id'))  # 联赛ID，关联到联赛表
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('TcbkLeague', backref='odds_histories', uselist=False, lazy=True)
    spf_history = relationship('TcbkOddsHistorySpf', backref='odds_history', uselist=False, lazy=True)
    rfsf_history = relationship('TcbkOddsHistoryRfsf', backref='odds_history', uselist=False, lazy=True)
    dxf_history = relationship('TcbkOddsHistoryDxf', backref='odds_history', uselist=False, lazy=True)
    sfc_history = relationship('TcbkOddsHistorySfc', backref='odds_history', uselist=False, lazy=True)

# 赔率历史 - 胜负赔率（spf）
class TcbkOddsHistorySpf(Base):
    __tablename__ = 'tcbk_odds_history_spf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tcbk_odds_history.id'), nullable=False)
    
    h = Column(Float)  # 主队胜赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新

# 赔率历史 - 让分胜负赔率（rfsf）
class TcbkOddsHistoryRfsf(Base):
    __tablename__ = 'tcbk_odds_history_rfsf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tcbk_odds_history.id'), nullable=False)
    
    goal_line = Column(Float)  # 让分数值
    goal_line_str = Column(String(10))  # 让分数值字符串
    
    h = Column(Float)  # 主队胜赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新

# 赔率历史 - 大小分赔率（dxf）
class TcbkOddsHistoryDxf(Base):
    __tablename__ = 'tcbk_odds_history_dxf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tcbk_odds_history.id'), nullable=False)
    
    goal_line = Column(Float)  # 大小分盘口
    goal_line_str = Column(String(10))  # 大小分盘口字符串
    
    over = Column(Float)  # 大分赔率
    under = Column(Float)  # 小分赔率
    
    overf = Column(Integer)  # 大分赔率变化
    underf = Column(Integer)  # 小分赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新

# 赔率历史 - 胜分差赔率（sfc）
class TcbkOddsHistorySfc(Base):
    __tablename__ = 'tcbk_odds_history_sfc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tcbk_odds_history.id'), nullable=False)
    
    # 胜分差赔率 - 主队胜
    h1 = Column(Float)  # 主队胜1-5分
    h2 = Column(Float)  # 主队胜6-10分
    h3 = Column(Float)  # 主队胜11-15分
    h4 = Column(Float)  # 主队胜16-20分
    h5 = Column(Float)  # 主队胜21-25分
    h6 = Column(Float)  # 主队胜26+分
    
    # 胜分差赔率 - 客队胜
    a1 = Column(Float)  # 客队胜1-5分
    a2 = Column(Float)  # 客队胜6-10分
    a3 = Column(Float)  # 客队胜11-15分
    a4 = Column(Float)  # 客队胜16-20分
    a5 = Column(Float)  # 客队胜21-25分
    a6 = Column(Float)  # 客队胜26+分
    
    # 赔率变化
    h1f = Column(Integer)  # 主队胜1-5分赔率变化
    h2f = Column(Integer)  # 主队胜6-10分赔率变化
    h3f = Column(Integer)  # 主队胜11-15分赔率变化
    h4f = Column(Integer)  # 主队胜16-20分赔率变化
    h5f = Column(Integer)  # 主队胜21-25分赔率变化
    h6f = Column(Integer)  # 主队胜26+分赔率变化
    
    a1f = Column(Integer)  # 客队胜1-5分赔率变化
    a2f = Column(Integer)  # 客队胜6-10分赔率变化
    a3f = Column(Integer)  # 客队胜11-15分赔率变化
    a4f = Column(Integer)  # 客队胜16-20分赔率变化
    a5f = Column(Integer)  # 客队胜21-25分赔率变化
    a6f = Column(Integer)  # 客队胜26+分赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间，包含日期和时间，自动更新