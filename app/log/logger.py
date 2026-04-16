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


def get_log_dir(log_type: str, create_monthly_folder: bool = True) -> Path:
    """
    获取指定类型的日志目录
    
    Args:
        log_type: 日志类型 (tczq, bjdc, lottery, jcbk, api)
        create_monthly_folder: 是否创建按月分类的文件夹
        
    Returns:
        Path: 日志文件所在目录
    """
    if create_monthly_folder:
        # 按年月创建子文件夹
        year_month = datetime.now().strftime('%Y-%m')
        log_dir = LOG_ROOT / log_type / year_month
    else:
        log_dir = LOG_ROOT / log_type
    
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
        name: 日志记录器名称
        log_type: 日志类型 (tczq, bjdc, lottery, jcbk, api)
        level: 日志级别
        console_output: 是否同时输出到控制台
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 获取日志目录
    log_dir = get_log_dir(log_type)
    
    # 日志文件名
    log_file = log_dir / f"{log_type}_data.log"
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # 添加到记录器
    logger.addHandler(file_handler)
    
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
    清理指定月数之前的日志文件
    
    Args:
        months_to_keep: 保留最近几个月的日志
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=months_to_keep * 30)
    cutoff_year_month = cutoff_date.strftime('%Y-%m')
    
    for log_type in ['tczq', 'bjdc', 'jcbk', 'lottery', 'api']:
        type_dir = LOG_ROOT / log_type
        if not type_dir.exists():
            continue
        
        # 遍历所有年月文件夹
        for folder in type_dir.iterdir():
            if not folder.is_dir():
                continue
            
            try:
                # 尝试解析文件夹名称为年月格式
                folder_date = datetime.strptime(folder.name, '%Y-%m')
                
                # 如果早于截止日期，删除整个文件夹
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
