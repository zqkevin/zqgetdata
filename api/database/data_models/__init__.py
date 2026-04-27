# -*- coding: utf-8 -*-
"""
体育数据模型（soccer_data 数据库）
包含比赛、赔率、联赛、球队等数据模型
"""

from .base_models import League, Team, TeamAlias, MatchTypeEnum
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
from .tcbk_models import (
    TcbkMatch, TcbkMatchResult, TcbkLeague, TcbkSpf, TcbkRfsf, TcbkDxf, TcbkSfc, TcbkResult,
    TcbkOddsHistory, TcbkOddsHistorySpf, TcbkOddsHistoryRfsf, TcbkOddsHistoryDxf, TcbkOddsHistorySfc,
    TcbkOddsChangeLog
)
from .digital_lottery_models import (
    DigitalLotteryType, DigitalLotteryDraw, DigitalLotteryPrize, DigitalLotteryTermList
)

# 向后兼容别名
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
    # 向后兼容别名
    'FootballMatch', 'SpfOdds', 'HandicapSpfOdds', 'ScoreOdds',
    'TotalGoalOdds', 'HalfTimeFullTimeOdds', 'OddsChangeLog', 'MatchResult',
]
