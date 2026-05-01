# -*- coding: utf-8 -*-

# 从 db_core 导入数据库操作类
from .db_core import mydb

# 创建数据库操作实例
localdb = mydb()

# 导入数字彩票模型
from .digital_lottery_models import (
    DigitalLotteryType, DigitalLotteryDraw, DigitalLotteryPrize, DigitalLotteryTermList
)

# 导入体彩篮球模型
from .tcbk_models import (
    TcbkMatch, TcbkMatchResult, TcbkLeague, TcbkSpf, TcbkRfsf, TcbkDxf, TcbkSfc, TcbkResult,
    TcbkOddsHistory, TcbkOddsHistorySpf, TcbkOddsHistoryRfsf, TcbkOddsHistoryDxf, TcbkOddsHistorySfc,
    TcbkOddsChangeLog
)

# 导入基础模型 (联赛、球队等公用表)
from .base_models import League, Team, TeamAlias, MatchTypeEnum

# 导入体彩足球模型
from .tczq_models import (
    TczqMatch,
    TczqSpfOdds,
    TczqHandicapSpfOdds,
    TczqTotalGoalOdds,
    TczqScoreOdds,
    TczqHalfTimeFullTimeOdds,
    TczqMatchResult,
    TczqOddsChangeLog
)

# 导入北京单场模型
from .bjdc_models import (
    BjdcMatch,
    BjdcSpfOdds,
    BjdcHandicapSpfOdds,
    BjdcTotalGoalOdds,
    BjdcScoreOdds,
    BjdcHalfTimeFullTimeOdds,
    BjdcUpDownOdds,
    BjdcMatchResult,
    BjdcOddsChangeLog
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
    # 数字彩票
    'DigitalLotteryType', 'DigitalLotteryDraw', 'DigitalLotteryPrize', 'DigitalLotteryTermList',
    # 体彩篮球
    'TcbkMatch', 'TcbkMatchResult', 'TcbkLeague',
    'TcbkSpf', 'TcbkRfsf', 'TcbkDxf', 'TcbkSfc', 'TcbkResult',
    'TcbkOddsHistory', 'TcbkOddsHistorySpf', 'TcbkOddsHistoryRfsf', 'TcbkOddsHistoryDxf', 'TcbkOddsHistorySfc',
    'TcbkOddsChangeLog',
    'TcbkOddsChangeLog',
    # 基础模型
    'League', 'Team', 'TeamAlias', 'MatchTypeEnum',
    # 体彩足球
    'TczqMatch', 'TczqSpfOdds', 'TczqHandicapSpfOdds', 'TczqTotalGoalOdds', 
    'TczqScoreOdds', 'TczqHalfTimeFullTimeOdds', 'TczqMatchResult', 'TczqOddsChangeLog',
    # 北京单场
    'BjdcMatch', 'BjdcSpfOdds', 'BjdcHandicapSpfOdds', 'BjdcTotalGoalOdds',
    'BjdcScoreOdds', 'BjdcHalfTimeFullTimeOdds', 'BjdcUpDownOdds', 'BjdcMatchResult', 'BjdcOddsChangeLog',
    # 向后兼容别名
    'FootballMatch', 'SpfOdds', 'HandicapSpfOdds', 'ScoreOdds',
    'TotalGoalOdds', 'HalfTimeFullTimeOdds', 'OddsChangeLog', 'MatchResult',
    # 数据库操作
    'localdb'
]
