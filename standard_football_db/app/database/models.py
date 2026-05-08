# -*- coding: utf-8 -*-
"""
标准足球数据库 - 基础模型
包含字典表和通用基类
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db_core import Base


# ==================== 字典表 ====================

class Position(Base):
    """球员位置字典表"""
    __tablename__ = 'sf_positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name_en = Column(String(50), nullable=False)
    name_zh = Column(String(50))
    category = Column(Enum('GOALKEEPER', 'DEFENDER', 'MIDFIELDER', 'FORWARD'), nullable=False)
    sort_order = Column(Integer, default=0)
    
    # 关系
    players = relationship('Player', back_populates='position')
    
    def __repr__(self):
        return f"<Position(code='{self.code}', name='{self.name_zh or self.name_en}')>"


# ==================== 核心实体表 ====================

class Area(Base):
    """国家/地区表"""
    __tablename__ = 'sf_areas'
    
    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False)
    name_zh = Column(String(100))
    code = Column(String(10), index=True)
    flag_url = Column(Text)
    parent_area_id = Column(Integer, ForeignKey('sf_areas.id'))
    area_type = Column(Enum('WORLD', 'CONTINENT', 'COUNTRY', 'REGION'), default='COUNTRY')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 自引用关系（父子区域）
    parent = relationship('Area', remote_side=[id], backref='children')
    
    # 关联关系
    leagues = relationship('League', back_populates='area')
    teams = relationship('Team', back_populates='area')
    players = relationship('Player', back_populates='nationality_area')
    coaches = relationship('Coach', back_populates='nationality_area')
    
    def __repr__(self):
        return f"<Area(id={self.id}, name='{self.name_zh or self.name_en}')>"


class Venue(Base):
    """球场表"""
    __tablename__ = 'sf_venues'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    name_zh = Column(String(200))
    city = Column(String(100), index=True)
    country = Column(String(100), index=True)
    address = Column(Text)
    capacity = Column(Integer)
    surface = Column(String(50))
    image_url = Column(Text)
    latitude = Column(Integer)  # 使用Integer存储，避免DECIMAL问题
    longitude = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    teams = relationship('Team', back_populates='venue')
    
    def __repr__(self):
        return f"<Venue(id={self.id}, name='{self.name}')>"


class League(Base):
    """联赛表"""
    __tablename__ = 'sf_leagues'
    
    id = Column(Integer, primary_key=True)
    name_en_full = Column(String(200), nullable=False)
    name_en_short = Column(String(100))
    name_zh_full = Column(String(200))
    name_zh_short = Column(String(100))
    code = Column(String(20), index=True)
    type = Column(Enum('LEAGUE', 'CUP', 'SUPER_CUP', 'OTHER'), default='LEAGUE')
    emblem_url = Column(Text)
    logo_url = Column(Text)
    area_id = Column(Integer, ForeignKey('sf_areas.id'), nullable=False, index=True)
    current_season_start = Column(DateTime)
    current_season_end = Column(DateTime)
    current_matchday = Column(Integer)
    source_platform = Column(Enum('FOOTBALL_DATA', 'API_FOOTBALL', 'THESPORTSDB'), default='THESPORTSDB')
    source_id = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    area = relationship('Area', back_populates='leagues')
    team_leagues = relationship('TeamLeague', back_populates='league')
    
    def __repr__(self):
        return f"<League(id={self.id}, name='{self.name_zh_full or self.name_en_full}')>"


class Team(Base):
    """球队表"""
    __tablename__ = 'sf_teams'
    
    id = Column(Integer, primary_key=True)
    name_en_full = Column(String(200), nullable=False, index=True)
    name_en_short = Column(String(100))
    name_zh_full = Column(String(200), index=True)
    name_zh_short = Column(String(100))
    short_code = Column(String(10))
    tla = Column(String(10))
    founded_year = Column(Integer)
    club_colors = Column(String(100))
    website = Column(String(500))
    facebook_url = Column(String(500))
    twitter_url = Column(String(500))
    instagram_url = Column(String(500))
    youtube_url = Column(String(500))
    crest_url = Column(Text)
    badge_url = Column(Text)
    logo_url = Column(Text)
    banner_url = Column(Text)
    equipment_url = Column(Text)
    fanart1_url = Column(Text)
    fanart2_url = Column(Text)
    fanart3_url = Column(Text)
    fanart4_url = Column(Text)
    area_id = Column(Integer, ForeignKey('sf_areas.id'), index=True)
    venue_id = Column(Integer, ForeignKey('sf_venues.id'))
    api_football_id = Column(String(50), index=True)
    espn_id = Column(String(50))
    thesportsdb_id = Column(String(50), index=True)
    source_platform = Column(Enum('FOOTBALL_DATA', 'API_FOOTBALL', 'THESPORTSDB'), default='THESPORTSDB')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    area = relationship('Area', back_populates='teams')
    venue = relationship('Venue', back_populates='teams')
    player_teams = relationship('PlayerTeam', back_populates='team')
    team_leagues = relationship('TeamLeague', back_populates='team')
    team_coaches = relationship('TeamCoach', back_populates='team')
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name_zh_full or self.name_en_full}')>"


class Player(Base):
    """球员表"""
    __tablename__ = 'sf_players'
    
    id = Column(Integer, primary_key=True)
    name_en_full = Column(String(200), nullable=False, index=True)
    first_name_en = Column(String(100))
    last_name_en = Column(String(100))
    name_zh_full = Column(String(200), index=True)
    first_name_zh = Column(String(100))
    last_name_zh = Column(String(100))
    date_of_birth = Column(DateTime)
    age = Column(Integer)  # 应用层计算
    nationality = Column(String(100))
    nationality_area_id = Column(Integer, ForeignKey('sf_areas.id'), index=True)
    position_id = Column(Integer, ForeignKey('sf_positions.id'), index=True)
    position_detail = Column(String(50))
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    preferred_foot = Column(Enum('LEFT', 'RIGHT', 'BOTH'))
    shirt_number = Column(Integer)
    photo_url = Column(Text)
    api_football_id = Column(String(50))
    thesportsdb_id = Column(String(50))
    source_platform = Column(Enum('FOOTBALL_DATA', 'API_FOOTBALL', 'THESPORTSDB'), default='THESPORTSDB')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    nationality_area = relationship('Area', back_populates='players')
    position = relationship('Position', back_populates='players')
    player_teams = relationship('PlayerTeam', back_populates='player')
    
    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.name_zh_full or self.name_en_full}')>"


class Coach(Base):
    """教练表"""
    __tablename__ = 'sf_coaches'
    
    id = Column(Integer, primary_key=True)
    name_en = Column(String(200), nullable=False, index=True)
    name_zh = Column(String(200), index=True)
    date_of_birth = Column(DateTime)
    nationality = Column(String(100))
    nationality_area_id = Column(Integer, ForeignKey('sf_areas.id'), index=True)
    photo_url = Column(Text)
    api_football_id = Column(String(50))
    thesportsdb_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    nationality_area = relationship('Area', back_populates='coaches')
    team_coaches = relationship('TeamCoach', back_populates='coach')
    
    def __repr__(self):
        return f"<Coach(id={self.id}, name='{self.name_zh or self.name_en}')>"


# ==================== 关联表 ====================

class PlayerTeam(Base):
    """球员-球队关联表"""
    __tablename__ = 'sf_player_teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('sf_players.id', ondelete='CASCADE'), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey('sf_teams.id', ondelete='CASCADE'), nullable=False, index=True)
    shirt_number = Column(Integer)
    join_date = Column(DateTime)
    leave_date = Column(DateTime)
    is_current = Column(Integer, default=1)  # SQLite不支持Boolean，用Integer
    contract_until = Column(DateTime)
    market_value_eur = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    player = relationship('Player', back_populates='player_teams')
    team = relationship('Team', back_populates='player_teams')
    
    def __repr__(self):
        return f"<PlayerTeam(player_id={self.player_id}, team_id={self.team_id})>"


class TeamLeague(Base):
    """球队-联赛关联表"""
    __tablename__ = 'sf_team_leagues'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('sf_teams.id', ondelete='CASCADE'), nullable=False, index=True)
    league_id = Column(Integer, ForeignKey('sf_leagues.id', ondelete='CASCADE'), nullable=False, index=True)
    season_year = Column(Integer)
    is_primary = Column(Integer, default=0)
    joined_date = Column(DateTime)
    left_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    team = relationship('Team', back_populates='team_leagues')
    league = relationship('League', back_populates='team_leagues')
    
    def __repr__(self):
        return f"<TeamLeague(team_id={self.team_id}, league_id={self.league_id})>"


class TeamCoach(Base):
    """球队-教练关联表"""
    __tablename__ = 'sf_team_coaches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('sf_teams.id', ondelete='CASCADE'), nullable=False, index=True)
    coach_id = Column(Integer, ForeignKey('sf_coaches.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_current = Column(Integer, default=1)
    role = Column(String(50), default='HEAD_COACH')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    team = relationship('Team', back_populates='team_coaches')
    coach = relationship('Coach', back_populates='team_coaches')
    
    def __repr__(self):
        return f"<TeamCoach(team_id={self.team_id}, coach_id={self.coach_id})>"


class Translation(Base):
    """翻译缓存表"""
    __tablename__ = 'sf_translations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_text = Column(String(500), nullable=False)
    translated_text = Column(String(500), nullable=False)
    from_lang = Column(String(2), default='en')
    to_lang = Column(String(2), default='zh')
    context = Column(String(50), index=True)
    md5_hash = Column(String(32), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Translation(id={self.id}, text='{self.source_text[:30]}...')>"
