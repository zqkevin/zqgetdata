# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 足球比赛主表
class Football(Base):
    __tablename__ = 'football'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fid = Column(Integer, unique=True, nullable=False, index=True)  # 比赛ID
    dcqs = Column(String(20), nullable=False, index=True)  # 期数
    index = Column(Integer, nullable=False)  # 比赛编号
    matchtime = Column(DateTime, nullable=False, index=True)  # 比赛时间
    leaguename = Column(String(100), nullable=False)  # 联赛名称
    homename = Column(String(100), nullable=False)  # 主队名称
    awayname = Column(String(100), nullable=False)  # 客队名称
    result_statu = Column(Integer, default=0, index=True)  # 结果状态 0-未开始 1-已结束等
    homegoal = Column(Integer, default=-1)  # 主队进球数
    awaygoal = Column(Integer, default=-1)  # 客队进球数
    half_homegoal = Column(Integer, default=-1)  # 主队半场进球数
    half_awaygoal = Column(Integer, default=-1)  # 客队半场进球数
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    pl = relationship('FootballPL', backref='football', uselist=False, lazy=True)
    pl_offset = relationship('FootballPLOffset', backref='football', uselist=False, lazy=True)

# 足球赔率表
class FootballPL(Base):
    __tablename__ = 'football_pl'
    id = Column(Integer, primary_key=True, autoincrement=True)
    football_id = Column(Integer, ForeignKey('football.id'), unique=True, nullable=False)
    
    # 胜平负赔率
    win_pl = Column(Float, default=0)  # 主队胜赔率
    draw_pl = Column(Float, default=0)  # 平局赔率
    lose_pl = Column(Float, default=0)  # 客队胜赔率
    rangqiu = Column(Float, default=0)  # 让球数
    winpl_eu = Column(Float, default=0)  # 欧洲平均胜赔率
    drawpl_eu = Column(Float, default=0)  # 欧洲平均平赔率
    losepl_eu = Column(Float, default=0)  # 欧洲平均负赔率
    
    # 总进球赔率
    goal_0 = Column(Float, default=0)  # 总进球0
    goal_1 = Column(Float, default=0)  # 总进球1
    goal_2 = Column(Float, default=0)  # 总进球2
    goal_3 = Column(Float, default=0)  # 总进球3
    goal_4 = Column(Float, default=0)  # 总进球4
    goal_5 = Column(Float, default=0)  # 总进球5
    goal_6 = Column(Float, default=0)  # 总进球6
    goal_about = Column(Float, default=0)  # 总进球7+
    
    # 比分赔率
    score_0_0 = Column(Float, default=0)  # 比分0:0
    score_0_1 = Column(Float, default=0)  # 比分0:1
    score_0_2 = Column(Float, default=0)  # 比分0:2
    score_0_3 = Column(Float, default=0)  # 比分0:3
    score_0_4 = Column(Float, default=0)  # 比分0:4
    score_0_5 = Column(Float, default=0)  # 比分0:5
    score_1_0 = Column(Float, default=0)  # 比分1:0
    score_1_1 = Column(Float, default=0)  # 比分1:1
    score_1_2 = Column(Float, default=0)  # 比分1:2
    score_1_3 = Column(Float, default=0)  # 比分1:3
    score_1_4 = Column(Float, default=0)  # 比分1:4
    score_1_5 = Column(Float, default=0)  # 比分1:5
    score_2_0 = Column(Float, default=0)  # 比分2:0
    score_2_1 = Column(Float, default=0)  # 比分2:1
    score_2_2 = Column(Float, default=0)  # 比分2:2
    score_2_3 = Column(Float, default=0)  # 比分2:3
    score_2_4 = Column(Float, default=0)  # 比分2:4
    score_2_5 = Column(Float, default=0)  # 比分2:5
    score_3_0 = Column(Float, default=0)  # 比分3:0
    score_3_1 = Column(Float, default=0)  # 比分3:1
    score_3_2 = Column(Float, default=0)  # 比分3:2
    score_3_3 = Column(Float, default=0)  # 比分3:3
    score_3_4 = Column(Float, default=0)  # 比分3:4
    score_3_5 = Column(Float, default=0)  # 比分3:5
    score_4_0 = Column(Float, default=0)  # 比分4:0
    score_4_1 = Column(Float, default=0)  # 比分4:1
    score_4_2 = Column(Float, default=0)  # 比分4:2
    score_4_3 = Column(Float, default=0)  # 比分4:3
    score_4_4 = Column(Float, default=0)  # 比分4:4
    score_4_5 = Column(Float, default=0)  # 比分4:5
    score_win_about = Column(Float, default=0)  # 胜其他
    score_lose_about = Column(Float, default=0)  # 负其他
    score_draw_about = Column(Float, default=0)  # 平其他
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 足球赔率历史偏移表
class FootballPLOffset(Base):
    __tablename__ = 'football_pl_offset'
    id = Column(Integer, primary_key=True, autoincrement=True)
    football_id = Column(Integer, ForeignKey('football.id'), unique=True, nullable=False)
    
    # 胜平负赔率历史
    win_pl = Column(Text, default='{}')  # 主队胜赔率历史
    draw_pl = Column(Text, default='{}')  # 平局赔率历史
    lose_pl = Column(Text, default='{}')  # 客队胜赔率历史
    rangqiu = Column(Text, default='{}')  # 让球数历史
    winpl_eu = Column(Text, default='{}')  # 欧洲平均胜赔率历史
    drawpl_eu = Column(Text, default='{}')  # 欧洲平均平赔率历史
    losepl_eu = Column(Text, default='{}')  # 欧洲平均负赔率历史
    
    # 总进球赔率历史
    goal_0 = Column(Text, default='{}')  # 总进球0赔率历史
    goal_1 = Column(Text, default='{}')  # 总进球1赔率历史
    goal_2 = Column(Text, default='{}')  # 总进球2赔率历史
    goal_3 = Column(Text, default='{}')  # 总进球3赔率历史
    goal_4 = Column(Text, default='{}')  # 总进球4赔率历史
    goal_5 = Column(Text, default='{}')  # 总进球5赔率历史
    goal_6 = Column(Text, default='{}')  # 总进球6赔率历史
    goal_about = Column(Text, default='{}')  # 总进球7+赔率历史
    
    # 比分赔率历史
    score_0_0 = Column(Text, default='{}')  # 比分0:0赔率历史
    score_0_1 = Column(Text, default='{}')  # 比分0:1赔率历史
    score_0_2 = Column(Text, default='{}')  # 比分0:2赔率历史
    score_0_3 = Column(Text, default='{}')  # 比分0:3赔率历史
    score_0_4 = Column(Text, default='{}')  # 比分0:4赔率历史
    score_0_5 = Column(Text, default='{}')  # 比分0:5赔率历史
    score_1_0 = Column(Text, default='{}')  # 比分1:0赔率历史
    score_1_1 = Column(Text, default='{}')  # 比分1:1赔率历史
    score_1_2 = Column(Text, default='{}')  # 比分1:2赔率历史
    score_1_3 = Column(Text, default='{}')  # 比分1:3赔率历史
    score_1_4 = Column(Text, default='{}')  # 比分1:4赔率历史
    score_1_5 = Column(Text, default='{}')  # 比分1:5赔率历史
    score_2_0 = Column(Text, default='{}')  # 比分2:0赔率历史
    score_2_1 = Column(Text, default='{}')  # 比分2:1赔率历史
    score_2_2 = Column(Text, default='{}')  # 比分2:2赔率历史
    score_2_3 = Column(Text, default='{}')  # 比分2:3赔率历史
    score_2_4 = Column(Text, default='{}')  # 比分2:4赔率历史
    score_2_5 = Column(Text, default='{}')  # 比分2:5赔率历史
    score_3_0 = Column(Text, default='{}')  # 比分3:0赔率历史
    score_3_1 = Column(Text, default='{}')  # 比分3:1赔率历史
    score_3_2 = Column(Text, default='{}')  # 比分3:2赔率历史
    score_3_3 = Column(Text, default='{}')  # 比分3:3赔率历史
    score_3_4 = Column(Text, default='{}')  # 比分3:4赔率历史
    score_3_5 = Column(Text, default='{}')  # 比分3:5赔率历史
    score_4_0 = Column(Text, default='{}')  # 比分4:0赔率历史
    score_4_1 = Column(Text, default='{}')  # 比分4:1赔率历史
    score_4_2 = Column(Text, default='{}')  # 比分4:2赔率历史
    score_4_3 = Column(Text, default='{}')  # 比分4:3赔率历史
    score_4_4 = Column(Text, default='{}')  # 比分4:4赔率历史
    score_4_5 = Column(Text, default='{}')  # 比分4:5赔率历史
    score_win_about = Column(Text, default='{}')  # 胜其他赔率历史
    score_lose_about = Column(Text, default='{}')  # 负其他赔率历史
    score_draw_about = Column(Text, default='{}')  # 平其他赔率历史
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)