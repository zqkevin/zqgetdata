# -*- coding: utf-8 -*-

# 从db_core导入数据库操作类
from .db_core import mydb

from .digital_lottery_models import DigitalLotteryType, DigitalLotteryDraw, DigitalLotteryPrize, DigitalLotteryTermList
from .tcbk_models import (
    TcbkMatch, TcbkMatchResult, TcbkLeague, TcbkSpf, TcbkRfsf, TcbkDxf, TcbkSfc, TcbkResult,
    TcbkOddsHistory, TcbkOddsHistorySpf, TcbkOddsHistoryRfsf, TcbkOddsHistoryDxf, TcbkOddsHistorySfc
)
from .tczq_models import TczqMatch, TczqLeague
from .bjdc_models import Football, FootballPL, FootballPLOffset
__all__ = ['DigitalLotteryType', 'DigitalLotteryDraw', 'DigitalLotteryPrize', 'DigitalLotteryTermList',
           'TcbkMatch', 'TcbkMatchResult', 'TcbkLeague', 'TczqMatch', 'TczqLeague',
           'TcbkSpf', 'TcbkRfsf', 'TcbkDxf', 'TcbkSfc', 'TcbkResult',
           'TcbkOddsHistory', 'TcbkOddsHistorySpf', 'TcbkOddsHistoryRfsf', 'TcbkOddsHistoryDxf', 'TcbkOddsHistorySfc',
           'Football', 'FootballPL', 'FootballPLOffset']