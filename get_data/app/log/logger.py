# -*- coding: utf-8 -*-
"""
日志管理模块
提供统一的日志管理功能，支持按彩种分类和按月归档
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path


# 日志根目录：app/log/
LOG_ROOT = Path(__file__).parent

# 确保日志根目录存在
LOG_ROOT.mkdir(exist_ok=True)


def get_log_dir(create_monthly_folder: bool = True) -> Path:
    """
    获取日志目录（所有模块共用）
    
    Args:
        create_monthly_folder: 是否创建按月分类的文件夹
        
    Returns:
        Path: 日志文件所在目录
    """
    if create_monthly_folder:
        # 按年月创建子文件夹
        year_month = datetime.now().strftime('%Y-%m')
        log_dir = LOG_ROOT / year_month
    else:
        log_dir = LOG_ROOT
    
    # 确保目录存在
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger(
    name: str,
    log_type: str,
    level=logging.INFO,
    console_output: bool = False
) -> logging.Logger:
    """
    配置并返回一个日志记录器
    
    Args:
        name: 日志记录器名称（会作为日志中的标识）
        log_type: 日志类型（仅用于兼容，实际不再使用）
        level: 日志级别
        console_output: 是否同时输出到控制台
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置为最低级别，让所有 handler 可以过滤
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 获取统一的日志目录（所有模块共用）
    log_dir = get_log_dir()
    
    # 设置日志格式（包含 logger 名称作为模块标识）
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. INFO 级别日志处理器（只记录 INFO）
    info_file = log_dir / "info.log"
    info_handler = logging.FileHandler(info_file, encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(lambda record: record.levelno == logging.INFO)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)
    
    # 2. WARNING 级别日志处理器（只记录 WARNING）
    warning_file = log_dir / "warning.log"
    warning_handler = logging.FileHandler(warning_file, encoding='utf-8')
    warning_handler.setLevel(logging.WARNING)
    warning_handler.addFilter(lambda record: record.levelno == logging.WARNING)
    warning_handler.setFormatter(formatter)
    logger.addHandler(warning_handler)
    
    # 3. ERROR 级别日志处理器（记录 ERROR 和 CRITICAL）
    error_file = log_dir / "error.log"
    error_handler = logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # 可选：输出到控制台
    if console_output:
        import sys
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        # 设置控制台编码为 UTF-8（解决 Windows 中文乱码问题）
        if hasattr(console_handler.stream, 'reconfigure'):
            console_handler.stream.reconfigure(encoding='utf-8')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# ========== 预定义的日志记录器 ==========

# 体彩足球数据日志
tczq_log = setup_logger('tczq_data', 'tczq')

# 北京单场数据日志
bjdc_log = setup_logger('bjdc_data', 'bjdc')

# 竞彩篮球数据日志
jcbk_log = setup_logger('jcbk_data', 'jcbk')

# 数字彩票数据日志
lottery_log = setup_logger('lottery_data', 'lottery')

# API 请求日志 - 用于记录 API 数据请求情况
api_log = setup_logger('api_request', 'api')

# 向后兼容的 log 变量（默认使用 tczq_log）
log = tczq_log


def get_logger(log_type: str, custom_name: str = None) -> logging.Logger:
    """
    获取指定类型的日志记录器
    
    Args:
        log_type: 日志类型 (tczq, bjdc, lottery, jcbk, api)
        custom_name: 自定义记录器名称后缀
        
    Returns:
        logging.Logger: 日志记录器
    """
    if custom_name:
        name = f"{log_type}_{custom_name}"
    else:
        name = f"{log_type}_data"
    
    return setup_logger(name, log_type)


def cleanup_old_logs(months_to_keep: int = 6):
    """
    清理指定月数之前的日志文件夹
    
    Args:
        months_to_keep: 保留最近几个月的日志
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=months_to_keep * 30)
    cutoff_year_month = cutoff_date.strftime('%Y-%m')
    
    # 遍历所有年月文件夹
    for folder in LOG_ROOT.iterdir():
        if not folder.is_dir():
            continue
        
        try:
            # 尝试解析文件夹名称为年月格式
            folder_date = datetime.strptime(folder.name, '%Y-%m')
            
            # 如果早于截止日期，删除整个文件夹（包括 info/warning/error 日志）
            if folder_date < datetime.strptime(cutoff_year_month, '%Y-%m'):
                import shutil
                shutil.rmtree(folder)
                api_log.info(f"已清理旧日志文件夹：{folder}")
                
        except ValueError:
            # 不是年月格式的文件夹，跳过
            continue


__all__ = [
    'tczq_log',
    'bjdc_log', 
    'jcbk_log',
    'lottery_log',
    'api_log',
    'log',
    'get_logger',
    'cleanup_old_logs',
    'LOG_ROOT'
]
