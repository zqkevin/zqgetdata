# -*- coding: utf-8 -*-
"""
日志模块入口
提供统一的日志访问接口
"""
from app.log.logger import (
    tczq_log,
    bjdc_log,
    jcbk_log,
    lottery_log,
    api_log,
    get_logger,
    cleanup_old_logs,
    LOG_ROOT
)

__all__ = [
    'tczq_log',
    'bjdc_log',
    'jcbk_log',
    'lottery_log',
    'api_log',
    'get_logger',
    'cleanup_old_logs',
    'LOG_ROOT'
]
