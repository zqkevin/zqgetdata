# -*- coding: utf-8 -*-
"""
竞彩篮球赛果获取器
实现获取篮球比赛结果并保存到数据库的功能
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.req_sporttery_api import SportteryAPI
from app.log import jcbk_log as logger
from app.database import localdb, TcbkMatch, TcbkResult


class JcbkResultCollector:
    """
    竞彩篮球赛果获取器
    """
    
    def __init__(self):
        self.api = SportteryAPI()
    
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
    
    def fetch_match_results(self) -> list:
        """
        获取比赛结果数据
        
        Returns:
            list: 比赛结果列表
        """
        try:
            logger.info('开始获取竞彩篮球比赛结果...')
            
            # 从 API 获取比赛结果（获取最近 7 天的比赛）
            from datetime import timedelta
            from datetime import datetime
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            results = self.api.get_basketball_match_results(
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
    
    def save_results_to_db(self, results: list) -> int:
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
                    logger.warning(f"比赛 ID 为空，跳过")
                    continue
                
                # 检查是否已存在赛果记录
                existing_result = localdb.query(TcbkResult).filter_by(match_id=match_id).first()
                
                # 转换 API 字段名为数据库字段名
                db_result_data = {}
                for key, value in result_data.items():
                    db_key = self._convert_api_field_to_db(key)
                    
                    if hasattr(TcbkResult, db_key):
                        db_result_data[db_key] = value
                
                if existing_result:
                    # 更新现有记录
                    for key, value in db_result_data.items():
                        setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                    logger.debug(f"更新赛果：match_id={match_id}")
                else:
                    # 创建新记录
                    if db_result_data:
                        new_result = TcbkResult(**db_result_data)
                        localdb.add(new_result, close=False)
                        logger.debug(f"新增赛果：match_id={match_id}")
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败 (match_id={match_id}): {str(e)}")
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
            logger.info('开始获取并保存竞彩篮球比赛结果...')
                
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
