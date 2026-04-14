# -*- coding: utf-8 -*-
"""
体彩足球赛果获取器
实现获取比赛结果并保存到数据库的功能
"""
import os
import sys
from datetime import datetime
from typing import Dict, List

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.common.req_sporttery_api import SportteryAPI
from app.log import tczq_log as logger
from app.database import (
    localdb,
    TczqMatch,
    TczqMatchResult
)


class TczqResultCollector:
    """
    体彩足球赛果获取器
    """
    
    def __init__(self):
        """
        初始化赛果获取器实例
        """
        self.api = SportteryAPI()
    
    def fetch_match_results(self) -> List[Dict]:
        """
        获取比赛结果数据
        
        Returns:
            list: 比赛结果列表
        """
        try:
            logger.info('开始获取体彩足球比赛结果...')
            
            # 从 API 获取比赛结果
            results = self.api.get_football_match_results()
            
            if results is None or results.empty:
                logger.info('获取到的比赛结果为空')
                return []
            
            logger.info(f'成功获取 {len(results)} 条比赛结果')
            return results.to_dict('records')
            
        except Exception as e:
            logger.error(f'获取比赛结果失败：{e}')
            return []
    
    def save_results_to_db(self, results: List[Dict]) -> int:
        """
        保存比赛结果到数据库
        
        Args:
            results: 比赛结果列表
            
        Returns:
            int: 成功保存的记录数
        """
        if not results:
            return 0
        
        saved_count = 0
        
        for result_data in results:
            try:
                match_id = result_data.get('matchId')
                if not match_id:
                    logger.warning(f"比赛 ID 为空，跳过：{result_data}")
                    continue
                
                # 检查是否已存在赛果记录
                existing_result = localdb.query(TczqMatchResult).filter_by(match_id=match_id).first()
                
                if existing_result:
                    # 更新现有记录
                    for key, value in result_data.items():
                        if hasattr(existing_result, key):
                            setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                else:
                    # 创建新记录
                    new_result = TczqMatchResult(**result_data)
                    localdb.add(new_result, close=False)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败 (match_id={result_data.get('match_id')}): {str(e)}")
                continue
        
        return saved_count
    
    def get_and_save_results(self) -> bool:
        """
        获取并保存比赛结果
            
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        try:
            logger.info('开始获取并保存体彩足球比赛结果...')
                
            # 获取比赛结果
            results = self.fetch_match_results()
                
            if not results:
                logger.warning('没有获取到比赛结果')
                return False
                
            logger.info(f'成功获取 {len(results)} 条比赛结果')
                
            # 保存到数据库
            saved_count = self.save_results_to_db(results)
                
            logger.info(f'成功保存 {saved_count} 条赛果记录')
            return saved_count > 0
                
        except Exception as e:
            logger.error(f'获取并保存赛果异常：traceback.format_exc()')
            return False
