# -*- coding: utf-8 -*-
"""
北京单场赛果获取器
实现获取比赛结果并保存到数据库的功能
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.common.req_sporttery_api import SportteryAPI
from app.log import bjdc_log as logger
from app.database import (
    localdb,
    BjdcMatch,
    BjdcMatchResult
)


class BjdcResultCollector:
    """
    北京单场赛果获取器
    """
    
    def __init__(self):
        """
        初始化赛果获取器实例
        """
        self.api = SportteryAPI()
        self.nowtime = datetime.now()
    
    def _convert_api_field_to_db(self, api_field: str) -> str:
        """
        将 API 返回的字段名转换为数据库模型字段名
        
        Args:
            api_field: API 字段名 (如 matchId)
            
        Returns:
            str: 数据库字段名 (如 match_id)
        """
        # 简单的驼峰转下划线转换
        result = ''
        for i, char in enumerate(api_field):
            if char.isupper() and i > 0:
                result += '_'
            result += char.lower()
        return result
    
    def fetch_match_results(self) -> List[Dict]:
        """
        获取比赛结果数据
        
        Returns:
            list: 比赛结果列表
        """
        try:
            logger.info('开始获取北京单场比赛结果...')
            
            # 从 API 获取比赛结果（获取最近 7 天的比赛）
            end_date = self.nowtime
            start_date = end_date - timedelta(days=7)
            
            results = self.api.get_football_match_result(
                match_begin_date=start_date.strftime('%Y-%m-%d'),
                match_end_date=end_date.strftime('%Y-%m-%d')
            )
            
            if not results:
                logger.info('获取到的比赛结果为空')
                return []
            
            logger.info(f'成功获取 {len(results)} 条比赛结果')
            return results
            
        except Exception as e:
            logger.error(f'获取比赛结果失败：{e}')
            import traceback
            logger.error(traceback.format_exc())
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
                existing_result = localdb.query(BjdcMatchResult).filter_by(match_id=match_id).first()
                
                if existing_result:
                    # 更新现有记录
                    for key, value in result_data.items():
                        # 将 API 字段名转换为数据库字段名
                        db_key = self._convert_api_field_to_db(key)
                        if hasattr(existing_result, db_key):
                            setattr(existing_result, db_key, value)
                    localdb.update(existing_result, close=False)
                    logger.debug(f"更新赛果：match_id={match_id}")
                else:
                    # 创建新记录 - 先转换字段名
                    db_result_data = {}
                    for key, value in result_data.items():
                        db_key = self._convert_api_field_to_db(key)
                        if hasattr(BjdcMatchResult, db_key):
                            db_result_data[db_key] = value
                    
                    if db_result_data:  # 只有有有效字段才创建
                        new_result = BjdcMatchResult(**db_result_data)
                        localdb.add(new_result, close=False)
                        logger.debug(f"新增赛果：match_id={match_id}")
                
                # 同时更新比赛表的状态
                match = localdb.query(BjdcMatch).filter_by(match_id=match_id).first()
                if match:
                    match.status = 1  # 标记为已结束
                    localdb.update(match, close=False)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败：{str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        return saved_count
    
    def get_and_save_results(self) -> bool:
        """
        获取并保存比赛结果
        
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        try:
            logger.info('开始获取并保存北京单场比赛结果...')
            
            # 获取比赛结果
            results = self.fetch_match_results()
            
            if not results:
                logger.warning('没有获取到比赛结果')
                return False
            
            # 保存到数据库
            saved_count = self.save_results_to_db(results)
            
            logger.info(f'成功保存 {saved_count} 条赛果记录')
            return saved_count > 0
            
        except Exception as e:
            logger.error(f'获取并保存赛果异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return False
