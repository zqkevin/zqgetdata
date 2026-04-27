# -*- coding: utf-8 -*-
"""
Pydantic 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


# ========== 认证相关模型 ==========

class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class UserCreate(BaseModel):
    """用户创建请求"""
    username: str
    password: str


# ========== 联赛相关模型 ==========

class LeagueResponse(BaseModel):
    """联赛响应"""
    id: int
    league_id: int
    league_name: str
    league_name_abbr: str
    region: Optional[str] = None
    country: Optional[str] = None
    href: str
    
    class Config:
        from_attributes = True


# ========== 球队相关模型 ==========

class TeamResponse(BaseModel):
    """球队响应"""
    id: int
    team_id: int
    team_code: str
    team_full_name: str
    team_short_name: str
    team_short_en_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ========== 比赛相关模型 ==========

class MatchBase(BaseModel):
    """比赛基础信息"""
    match_id: int
    issue: str
    match_num: int
    match_num_str: Optional[str] = None
    match_week: str
    match_time: datetime
    status: int
    remark: Optional[str] = None


class TczqMatchResponse(MatchBase):
    """体彩足球比赛响应"""
    id: int
    league_id: Optional[int] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    bjdc_match_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class BjdcMatchResponse(MatchBase):
    """北京单场比赛响应"""
    id: int
    league_id: Optional[int] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# ========== 赔率相关模型 ==========

class SpfOddsResponse(BaseModel):
    """胜平负赔率响应"""
    id: int
    match_id: int
    win_pl: float
    draw_pl: float
    lose_pl: float
    winpl_eu: float
    drawpl_eu: float
    losepl_eu: float
    
    class Config:
        from_attributes = True


class HandicapSpfOddsResponse(BaseModel):
    """让球胜平负赔率响应"""
    id: int
    match_id: int
    handicap: float
    win_pl: float
    draw_pl: float
    lose_pl: float
    
    class Config:
        from_attributes = True


class TotalGoalOddsResponse(BaseModel):
    """总进球赔率响应"""
    id: int
    match_id: int
    goal_0: float
    goal_1: float
    goal_2: float
    goal_3: float
    goal_4: float
    goal_5: float
    goal_6: float
    goal_about: float
    
    class Config:
        from_attributes = True


class ScoreOddsResponse(BaseModel):
    """比分赔率响应"""
    id: int
    match_id: int
    score_0_0: float
    score_1_0: float
    score_2_0: float
    score_0_1: float
    score_1_1: float
    score_2_1: float
    # ... 其他比分字段可以根据需要添加
    
    class Config:
        from_attributes = True


# ========== 赛果相关模型 ==========

class MatchResultResponse(BaseModel):
    """比赛结果响应"""
    id: int
    match_id: int
    home_team_goals: Optional[int] = 0
    away_team_goals: Optional[int] = 0
    half_time_home_goals: Optional[int] = 0
    half_time_away_goals: Optional[int] = 0
    result_type: Optional[str] = None
    handicap_result: Optional[str] = None
    total_goals: Optional[int] = 0
    
    class Config:
        from_attributes = True


# ========== 通用响应模型 ==========

class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
