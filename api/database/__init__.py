# -*- coding: utf-8 -*-

# 从 db_core 导入数据库操作类
from .db_core import DataDB, SelfDB, mydb

# 创建数据库操作实例
datadb = DataDB()  # 体育数据数据库（soccer_data）
selfdb = SelfDB()  # API 服务数据库（soccer_server）

# 为了向后兼容，保留 localdb 别名
localdb = datadb

# 导入体育数据模型（soccer_data 数据库）
from .data_models import (
    # 基础模型
    League, Team, TeamAlias, MatchTypeEnum,
    # 体彩足球
    TczqMatch, TczqSpfOdds, TczqHandicapSpfOdds, TczqTotalGoalOdds,
    TczqScoreOdds, TczqHalfTimeFullTimeOdds, TczqMatchResult, TczqOddsChangeLog,
    # 北京单场
    BjdcMatch, BjdcSpfOdds, BjdcHandicapSpfOdds, BjdcTotalGoalOdds,
    BjdcScoreOdds, BjdcHalfTimeFullTimeOdds, BjdcUpDownOdds, BjdcMatchResult, BjdcOddsChangeLog,
    # 体彩篮球
    TcbkMatch, TcbkMatchResult, TcbkLeague,
    TcbkSpf, TcbkRfsf, TcbkDxf, TcbkSfc, TcbkResult,
    TcbkOddsHistory, TcbkOddsHistorySpf, TcbkOddsHistoryRfsf, TcbkOddsHistoryDxf, TcbkOddsHistorySfc,
    TcbkOddsChangeLog,
    # 数字彩票
    DigitalLotteryType, DigitalLotteryDraw, DigitalLotteryPrize, DigitalLotteryTermList,
    # 向后兼容别名
    FootballMatch, SpfOdds, HandicapSpfOdds, ScoreOdds,
    TotalGoalOdds, HalfTimeFullTimeOdds, OddsChangeLog, MatchResult,
)

# 导入 API 服务模型（soccer_server 数据库）
from .server_models import (
    # 用户相关
    User, UserLevelConfig, UserBalanceLog,
    # 投注相关
    BetRecord, BetOrder,
    # 收藏/关注相关
    UserFavorite, UserFollow,
    # 系统相关
    QueryLog, ApiToken, SystemConfig,
)

# 为了向后兼容，保留旧的 FootballMatch 引用 (指向 TczqMatch)
FootballMatch = TczqMatch
SpfOdds = TczqSpfOdds
HandicapSpfOdds = TczqHandicapSpfOdds
ScoreOdds = TczqScoreOdds
TotalGoalOdds = TczqTotalGoalOdds
HalfTimeFullTimeOdds = TczqHalfTimeFullTimeOdds
OddsChangeLog = TczqOddsChangeLog
MatchResult = TczqMatchResult

__all__ = [
    # 基础模型
    'League', 'Team', 'TeamAlias', 'MatchTypeEnum',
    # 体彩足球
    'TczqMatch', 'TczqSpfOdds', 'TczqHandicapSpfOdds', 'TczqTotalGoalOdds', 
    'TczqScoreOdds', 'TczqHalfTimeFullTimeOdds', 'TczqMatchResult', 'TczqOddsChangeLog',
    # 北京单场
    'BjdcMatch', 'BjdcSpfOdds', 'BjdcHandicapSpfOdds', 'BjdcTotalGoalOdds',
    'BjdcScoreOdds', 'BjdcHalfTimeFullTimeOdds', 'BjdcUpDownOdds', 'BjdcMatchResult', 'BjdcOddsChangeLog',
    # 体彩篮球
    'TcbkMatch', 'TcbkMatchResult', 'TcbkLeague',
    'TcbkSpf', 'TcbkRfsf', 'TcbkDxf', 'TcbkSfc', 'TcbkResult',
    'TcbkOddsHistory', 'TcbkOddsHistorySpf', 'TcbkOddsHistoryRfsf', 'TcbkOddsHistoryDxf', 'TcbkOddsHistorySfc',
    'TcbkOddsChangeLog',
    # 数字彩票
    'DigitalLotteryType', 'DigitalLotteryDraw', 'DigitalLotteryPrize', 'DigitalLotteryTermList',
    # API 服务模型 - 用户相关
    'User', 'UserLevelConfig', 'UserBalanceLog',
    # API 服务模型 - 投注相关
    'BetRecord', 'BetOrder',
    # API 服务模型 - 收藏/关注相关
    'UserFavorite', 'UserFollow',
    # API 服务模型 - 系统相关
    'QueryLog', 'ApiToken', 'SystemConfig',
    # 向后兼容别名
    'FootballMatch', 'SpfOdds', 'HandicapSpfOdds', 'ScoreOdds',
    'TotalGoalOdds', 'HalfTimeFullTimeOdds', 'OddsChangeLog', 'MatchResult',
    # 数据库操作类和实例
    'DataDB', 'SelfDB', 'mydb', 'datadb', 'selfdb', 'localdb'
]
