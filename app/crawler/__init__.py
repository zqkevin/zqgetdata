# 体彩足球数据采集和赛果获取
from .tczq import TczqDataCollector
from .tczq_result import TczqResultCollector

# 竞彩篮球数据采集和赛果获取
from .jcbk import JcbkDataCollector
from .jcbk_result import JcbkResultCollector

# 北京单场数据采集和赛果获取（待实现）
from .bjdc import BjdcDataCollector
from .bjdc_result import BjdcResultCollector

# 数字彩票数据采集
from .lottery import LotteryDataCollector

__all__ = [
    # 体彩足球
    'TczqDataCollector',
    'TczqResultCollector',
    # 竞彩篮球
    'JcbkDataCollector',
    'JcbkResultCollector',
    # 北京单场
    'BjdcDataCollector',
    'BjdcResultCollector',
    # 数字彩票
    'LotteryDataCollector',
]