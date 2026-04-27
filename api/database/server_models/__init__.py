# -*- coding: utf-8 -*-
"""
API 服务数据模型（soccer_server 数据库）
按功能模块组织：用户、投注、收藏、系统等
"""

# 用户相关
from .user_models import User, UserLevelConfig, UserBalanceLog

# 投注相关
from .bet_models import BetRecord, BetOrder

# 收藏/关注相关
from .favorite_models import UserFavorite, UserFollow

# 系统相关
from .system_models import QueryLog, ApiToken, SystemConfig

__all__ = [
    # 用户相关
    'User', 'UserLevelConfig', 'UserBalanceLog',
    # 投注相关
    'BetRecord', 'BetOrder',
    # 收藏/关注相关
    'UserFavorite', 'UserFollow',
    # 系统相关
    'QueryLog', 'ApiToken', 'SystemConfig',
]
