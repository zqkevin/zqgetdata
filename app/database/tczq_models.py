# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 联赛表
class TczqLeague(Base):
    __tablename__ = 'tczq_league'
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, unique=True, nullable=False, index=True)  # 联赛ID
    league_name = Column(String(50), nullable=False)  # 联赛全称
    league_name_abbr = Column(String(20), nullable=False)  # 联赛简称
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 体彩足球对阵主表
class TczqMatch(Base):
    __tablename__ = 'tczq_match'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, unique=True, nullable=False, index=True)  # 比赛ID
    match_num = Column(Integer)  # 比赛编号
    match_num_str = Column(String(20))  # 比赛编号字符串，如"周一001"
    match_num_date = Column(String(10))  # 比赛日期编号
    match_week = Column(String(10))  # 比赛星期
    match_date = Column(String(20))  # 比赛日期
    match_time = Column(String(20))  # 比赛时间
    business_date = Column(String(20))  # 业务日期
    tax_date_no = Column(String(20))  # 税务日期编号
    
    league_id = Column(Integer, ForeignKey('tczq_league.league_id'))  # 联赛ID，关联到联赛表
    
    home_team_id = Column(Integer)  # 主队ID
    home_team_code = Column(String(20))  # 主队代码
    home_team_all_name = Column(String(50))  # 主队全称
    home_team_abb_name = Column(String(20))  # 主队简称
    home_team_abb_en_name = Column(String(20))  # 主队英文简称
    home_rank = Column(String(20))  # 主队排名
    
    away_team_id = Column(Integer)  # 客队ID
    away_team_code = Column(String(20))  # 客队代码
    away_team_all_name = Column(String(50))  # 客队全称
    away_team_abb_name = Column(String(20))  # 客队简称
    away_team_abb_en_name = Column(String(20))  # 客队英文简称
    away_rank = Column(String(20))  # 客队排名
    
    base_home_team_id = Column(Integer)  # 基础主队ID
    base_away_team_id = Column(Integer)  # 基础客队ID
    
    match_name = Column(String(50))  # 比赛名称
    group_name = Column(String(50))  # 分组名称
    line_num = Column(String(20))  # 线路号

    betting_single = Column(Integer)  # 单场投注
    betting_all_up = Column(Integer)  # 串关投注

    remark = Column(Text)  # 备注
    status = Column(Integer)  # 状态 0-未开始 1-赛果已经记录 2-赛果获取失败 3-比赛已取消 4-其他
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('TczqLeague', backref='matches', uselist=False, lazy=True)
    
    # 一对多关系
    crs = relationship('TczqCrs', backref='match', uselist=False, lazy=True)
    had = relationship('TczqHad', backref='match', uselist=False, lazy=True)
    hhad = relationship('TczqHhad', backref='match', uselist=False, lazy=True)
    hafu = relationship('TczqHafu', backref='match', uselist=False, lazy=True)
    ttg = relationship('TczqTtg', backref='match', uselist=False, lazy=True)
    result = relationship('TczqResult', backref='match', uselist=False, lazy=True)

# 比赛赛果表
class TczqResult(Base):
    __tablename__ = 'tczq_result'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tczq_match.match_id'), unique=True, nullable=False)
    
    # 赛果基本信息
    match_result_status = Column(String(20))  # 比赛结果状态
    pool_status = Column(String(20))  # 奖池状态
    result_status = Column(String(20))  # 结果状态
    win_flag = Column(String(10))  # 获胜方 H-主队 A-客队 D-平局
    
    # 比分信息
    half_score = Column(String(20))  # 半场比分 (sectionsNo1)
    full_score = Column(String(20))  # 全场比分 (sectionsNo999)
    
    # 球队信息
    home_team = Column(String(50))  # 主队名称
    away_team = Column(String(50))  # 客队名称
    all_home_team = Column(String(50))  # 主队全称
    all_away_team = Column(String(50))  # 客队全称
    
    # 联赛信息
    league_id = Column(Integer, ForeignKey('tczq_league.league_id'))  # 联赛ID，关联到联赛表
    league_back_color = Column(String(20))  # 联赛背景颜色
    
    # 赔率信息
    h = Column(Float)  # 主队胜赔率
    d = Column(Float)  # 平局赔率
    a = Column(Float)  # 客队胜赔率
    goal_line = Column(String(20))  # 让球数
    
    # 投注信息
    betting_single = Column(Integer)  # 单场投注状态
    is_cancel = Column(Integer)  # 是否取消
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('TczqLeague', backref='results', uselist=False, lazy=True)
    match_results = relationship('TczqMatchResult', backref='result', lazy=True)
    odds_history = relationship('TczqOddsHistory', backref='result', uselist=False, lazy=True)

# 比赛玩法结果表（matchResultList）
class TczqMatchResult(Base):
    __tablename__ = 'tczq_match_result'
    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey('tczq_result.id'), nullable=False)
    
    code = Column(String(20))  # 玩法代码
    combination = Column(String(20))  # 组合
    combination_desc = Column(String(50))  # 组合描述
    goal_line = Column(String(20))  # 让球数
    line_status = Column(String(20))  # 线路状态
    match_id = Column(Integer)  # 比赛ID
    odds = Column(String(20))  # 赔率
    odds_goal_line = Column(String(20))  # 赔率让球数
    odds_type = Column(String(10))  # 赔率类型
    pool_id = Column(Integer)  # 奖池ID
    pool_totals = Column(String(20))  # 奖池总额
    refund_status = Column(String(10))  # 退款状态
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 赔率历史主表（oddsHistory）
class TczqOddsHistory(Base):
    __tablename__ = 'tczq_odds_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey('tczq_result.id'), nullable=True)
    
    # 比赛基本信息
    match_id = Column(Integer)  # 比赛ID
    home_team_id = Column(Integer)  # 主队ID
    away_team_id = Column(Integer)  # 客队ID
    home_team_all_name = Column(String(50))  # 主队全称
    home_team_abb_name = Column(String(20))  # 主队简称
    away_team_all_name = Column(String(50))  # 客队全称
    away_team_abb_name = Column(String(20))  # 客队简称
    league_id = Column(Integer, ForeignKey('tczq_league.league_id'))  # 联赛ID，关联到联赛表
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    league = relationship('TczqLeague', backref='odds_histories', uselist=False, lazy=True)
    crs_list = relationship('TczqOddsHistoryCrs', backref='odds_history', lazy=True)
    hhad_list = relationship('TczqOddsHistoryHhad', backref='odds_history', lazy=True)
    ttg_list = relationship('TczqOddsHistoryTtg', backref='odds_history', lazy=True)
    had_list = relationship('TczqOddsHistoryHad', backref='odds_history', lazy=True)
    hafu_list = relationship('TczqOddsHistoryHafu', backref='odds_history', lazy=True)
    single_list = relationship('TczqOddsSingle', backref='odds_history', lazy=True)

# 赔率历史 - 总进球赔率（crsList）
class TczqOddsHistoryCrs(Base):
    __tablename__ = 'tczq_odds_history_crs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tczq_odds_history.id'), nullable=False)
    
    # 赔率字段
    s00s00 = Column(Float)  # 0-0
    s00s01 = Column(Float)  # 0-1
    s00s02 = Column(Float)  # 0-2
    s00s03 = Column(Float)  # 0-3
    s00s04 = Column(Float)  # 0-4
    s00s05 = Column(Float)  # 0-5
    s01s00 = Column(Float)  # 1-0
    s01s01 = Column(Float)  # 1-1
    s01s02 = Column(Float)  # 1-2
    s01s03 = Column(Float)  # 1-3
    s01s04 = Column(Float)  # 1-4
    s01s05 = Column(Float)  # 1-5
    s02s00 = Column(Float)  # 2-0
    s02s01 = Column(Float)  # 2-1
    s02s02 = Column(Float)  # 2-2
    s02s03 = Column(Float)  # 2-3
    s02s04 = Column(Float)  # 2-4
    s02s05 = Column(Float)  # 2-5
    s03s00 = Column(Float)  # 3-0
    s03s01 = Column(Float)  # 3-1
    s03s02 = Column(Float)  # 3-2
    s03s03 = Column(Float)  # 3-3
    s04s00 = Column(Float)  # 4-0
    s04s01 = Column(Float)  # 4-1
    s04s02 = Column(Float)  # 4-2
    s05s00 = Column(Float)  # 5-0
    s05s01 = Column(Float)  # 5-1
    s05s02 = Column(Float)  # 5-2
    s_1sh = Column(Float)  # 主队胜其他
    s_1sd = Column(Float)  # 平局其他
    s_1sa = Column(Float)  # 客队胜其他
    
    # 赔率变化
    s00s00f = Column(Integer)  # 0-0 变化
    s00s01f = Column(Integer)  # 0-1 变化
    s00s02f = Column(Integer)  # 0-2 变化
    s00s03f = Column(Integer)  # 0-3 变化
    s00s04f = Column(Integer)  # 0-4 变化
    s00s05f = Column(Integer)  # 0-5 变化
    s01s00f = Column(Integer)  # 1-0 变化
    s01s01f = Column(Integer)  # 1-1 变化
    s01s02f = Column(Integer)  # 1-2 变化
    s01s03f = Column(Integer)  # 1-3 变化
    s01s04f = Column(Integer)  # 1-4 变化
    s01s05f = Column(Integer)  # 1-5 变化
    s02s00f = Column(Integer)  # 2-0 变化
    s02s01f = Column(Integer)  # 2-1 变化
    s02s02f = Column(Integer)  # 2-2 变化
    s02s03f = Column(Integer)  # 2-3 变化
    s02s04f = Column(Integer)  # 2-4 变化
    s02s05f = Column(Integer)  # 2-5 变化
    s03s00f = Column(Integer)  # 3-0 变化
    s03s01f = Column(Integer)  # 3-1 变化
    s03s02f = Column(Integer)  # 3-2 变化
    s03s03f = Column(Integer)  # 3-3 变化
    s04s00f = Column(Integer)  # 4-0 变化
    s04s01f = Column(Integer)  # 4-1 变化
    s04s02f = Column(Integer)  # 4-2 变化
    s05s00f = Column(Integer)  # 5-0 变化
    s05s01f = Column(Integer)  # 5-1 变化
    s05s02f = Column(Integer)  # 5-2 变化
    s_1shf = Column(Integer)  # 主队胜其他 变化
    s_1sdf = Column(Integer)  # 平局其他 变化
    s_1saf = Column(Integer)  # 客队胜其他 变化
    
    goal_line = Column(String(20))  # 让球数
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 赔率历史 - 让球胜平负赔率（hhadList）
class TczqOddsHistoryHhad(Base):
    __tablename__ = 'tczq_odds_history_hhad'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tczq_odds_history.id'), nullable=False)
    
    h = Column(Float)  # 主队胜赔率
    d = Column(Float)  # 平局赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    df = Column(Integer)  # 平局赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    goal_line = Column(String(20))  # 让球数
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 赔率历史 - 总进球数赔率（ttgList）
class TczqOddsHistoryTtg(Base):
    __tablename__ = 'tczq_odds_history_ttg'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tczq_odds_history.id'), nullable=False)
    
    s0 = Column(Float)  # 0球赔率
    s1 = Column(Float)  # 1球赔率
    s2 = Column(Float)  # 2球赔率
    s3 = Column(Float)  # 3球赔率
    s4 = Column(Float)  # 4球赔率
    s5 = Column(Float)  # 5球赔率
    s6 = Column(Float)  # 6球赔率
    s7 = Column(Float)  # 7+球赔率
    
    s0f = Column(Integer)  # 0球赔率变化
    s1f = Column(Integer)  # 1球赔率变化
    s2f = Column(Integer)  # 2球赔率变化
    s3f = Column(Integer)  # 3球赔率变化
    s4f = Column(Integer)  # 4球赔率变化
    s5f = Column(Integer)  # 5球赔率变化
    s6f = Column(Integer)  # 6球赔率变化
    s7f = Column(Integer)  # 7+球赔率变化
    
    goal_line = Column(String(20))  # 让球数
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 赔率历史 - 胜平负赔率（hadList）
class TczqOddsHistoryHad(Base):
    __tablename__ = 'tczq_odds_history_had'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tczq_odds_history.id'), nullable=False)
    
    h = Column(Float)  # 主队胜赔率
    d = Column(Float)  # 平局赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    df = Column(Integer)  # 平局赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    goal_line = Column(String(20))  # 让球数
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 赔率历史 - 半全场赔率（hafuList）
class TczqOddsHistoryHafu(Base):
    __tablename__ = 'tczq_odds_history_hafu'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tczq_odds_history.id'), nullable=False)
    
    hh = Column(Float)  # 主胜主胜赔率
    hd = Column(Float)  # 主胜平局赔率
    ha = Column(Float)  # 主胜客胜赔率
    
    dh = Column(Float)  # 平局主胜赔率
    dd = Column(Float)  # 平局平局赔率
    da = Column(Float)  # 平局客胜赔率
    
    ah = Column(Float)  # 客胜主胜赔率
    ad = Column(Float)  # 客胜平局赔率
    aa = Column(Float)  # 客胜客胜赔率
    
    hhf = Column(Integer)  # 主胜主胜赔率变化
    hdf = Column(Integer)  # 主胜平局赔率变化
    haf = Column(Integer)  # 主胜客胜赔率变化
    
    dhf = Column(Integer)  # 平局主胜赔率变化
    ddf = Column(Integer)  # 平局平局赔率变化
    daf = Column(Integer)  # 平局客胜赔率变化
    
    ahf = Column(Integer)  # 客胜主胜赔率变化
    adf = Column(Integer)  # 客胜平局赔率变化
    aaf = Column(Integer)  # 客胜客胜赔率变化
    
    goal_line = Column(String(20))  # 让球数
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 赔率历史 - 单场投注信息（singleList）
class TczqOddsSingle(Base):
    __tablename__ = 'tczq_odds_single'
    id = Column(Integer, primary_key=True, autoincrement=True)
    odds_history_id = Column(Integer, ForeignKey('tczq_odds_history.id'), nullable=False)
    
    single = Column(Integer)  # 单场投注状态
    pool_code = Column(String(20))  # 奖池代码
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 总进球赔率表 (crs)
class TczqCrs(Base):
    __tablename__ = 'tczq_crs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tczq_match.match_id'), unique=True, nullable=False)
    
    # 进球赔率
    s00s00 = Column(Float)  # 0-0
    s00s01 = Column(Float)  # 0-1
    s00s02 = Column(Float)  # 0-2
    s00s03 = Column(Float)  # 0-3
    s00s04 = Column(Float)  # 0-4
    s00s05 = Column(Float)  # 0-5
    
    s01s00 = Column(Float)  # 1-0
    s01s01 = Column(Float)  # 1-1
    s01s02 = Column(Float)  # 1-2
    s01s03 = Column(Float)  # 1-3
    s01s04 = Column(Float)  # 1-4
    s01s05 = Column(Float)  # 1-5
    
    s02s00 = Column(Float)  # 2-0
    s02s01 = Column(Float)  # 2-1
    s02s02 = Column(Float)  # 2-2
    s02s03 = Column(Float)  # 2-3
    s02s04 = Column(Float)  # 2-4
    s02s05 = Column(Float)  # 2-5
    
    s03s00 = Column(Float)  # 3-0
    s03s01 = Column(Float)  # 3-1
    s03s02 = Column(Float)  # 3-2
    s03s03 = Column(Float)  # 3-3
    
    s04s00 = Column(Float)  # 4-0
    s04s01 = Column(Float)  # 4-1
    s04s02 = Column(Float)  # 4-2
    
    s05s00 = Column(Float)  # 5-0
    s05s01 = Column(Float)  # 5-1
    s05s02 = Column(Float)  # 5-2
    
    s1sh = Column(Float)  # 主队胜其他
    s1sd = Column(Float)  # 平局其他
    s1sa = Column(Float)  # 客队胜其他
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 胜平负赔率表 (had)
class TczqHad(Base):
    __tablename__ = 'tczq_had'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tczq_match.match_id'), unique=True, nullable=False)
    
    h = Column(Float)  # 主队胜赔率
    d = Column(Float)  # 平局赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    df = Column(Integer)  # 平局赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 让球胜平负赔率表 (hhad)
class TczqHhad(Base):
    __tablename__ = 'tczq_hhad'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tczq_match.match_id'), unique=True, nullable=False)
    
    goal_line = Column(String(20))  # 让球数
    goal_line_value = Column(Float)  # 让球数值
    
    h = Column(Float)  # 主队胜赔率
    d = Column(Float)  # 平局赔率
    a = Column(Float)  # 客队胜赔率
    
    hf = Column(Integer)  # 主队胜赔率变化
    df = Column(Integer)  # 平局赔率变化
    af = Column(Integer)  # 客队胜赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 半全场赔率表 (hafu)
class TczqHafu(Base):
    __tablename__ = 'tczq_hafu'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tczq_match.match_id'), unique=True, nullable=False)
    
    hh = Column(Float)  # 主胜主胜赔率
    hd = Column(Float)  # 主胜平局赔率
    ha = Column(Float)  # 主胜客胜赔率
    
    dh = Column(Float)  # 平局主胜赔率
    dd = Column(Float)  # 平局平局赔率
    da = Column(Float)  # 平局客胜赔率
    
    ah = Column(Float)  # 客胜主胜赔率
    ad = Column(Float)  # 客胜平局赔率
    aa = Column(Float)  # 客胜客胜赔率
    
    hhf = Column(Integer)  # 主胜主胜赔率变化
    hdf = Column(Integer)  # 主胜平局赔率变化
    haf = Column(Integer)  # 主胜客胜赔率变化
    
    dhf = Column(Integer)  # 平局主胜赔率变化
    ddf = Column(Integer)  # 平局平局赔率变化
    daf = Column(Integer)  # 平局客胜赔率变化
    
    ahf = Column(Integer)  # 客胜主胜赔率变化
    adf = Column(Integer)  # 客胜平局赔率变化
    aaf = Column(Integer)  # 客胜客胜赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新

# 总进球数赔率表 (ttg)
class TczqTtg(Base):
    __tablename__ = 'tczq_ttg'
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('tczq_match.match_id'), unique=True, nullable=False)
    
    s0 = Column(Float)  # 0球赔率
    s1 = Column(Float)  # 1球赔率
    s2 = Column(Float)  # 2球赔率
    s3 = Column(Float)  # 3球赔率
    s4 = Column(Float)  # 4球赔率
    s5 = Column(Float)  # 5球赔率
    s6 = Column(Float)  # 6球赔率
    s7 = Column(Float)  # 7+球赔率
    
    s0f = Column(Integer)  # 0球赔率变化
    s1f = Column(Integer)  # 1球赔率变化
    s2f = Column(Integer)  # 2球赔率变化
    s3f = Column(Integer)  # 3球赔率变化
    s4f = Column(Integer)  # 4球赔率变化
    s5f = Column(Integer)  # 5球赔率变化
    s6f = Column(Integer)  # 6球赔率变化
    s7f = Column(Integer)  # 7+球赔率变化
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（包含日期和时间），自动更新