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
            
            # 1. 查询数据库中需要获取赛果的比赛
            from datetime import timedelta, datetime
            
            # TcbkMatch没有status字段，也没有match_time字段，使用match_date字符串
            # 查询最近7天的比赛（因为无法判断是否已结束）
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            abnormal_cutoff_date = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
            
            pending_matches = localdb.query(TcbkMatch).filter(
                TcbkMatch.match_date >= seven_days_ago
            ).all()
            
            if not pending_matches:
                logger.info('没有需要获取赛果的比赛')
                return []
            
            logger.info(f'找到 {len(pending_matches)} 场需要获取赛果的比赛')
            
            # 2. 检查并标记异常比赛（开赛超过4天且无延期标识）
            abnormal_count = 0
            valid_matches = []
            
            for match in pending_matches:
                # 检查是否开赛超过4天（通过match_date字符串比较）
                if match.match_date and match.match_date < abnormal_cutoff_date:
                    # 检查是否有延期标识（remark或match_status中包含延期相关关键词）
                    has_postpone_flag = False
                    
                    # 检查remark字段
                    if match.remark:
                        postpone_keywords = ['延期', '推迟', '改期', 'postpone', 'delayed']
                        has_postpone_flag = any(keyword in str(match.remark).lower() for keyword in postpone_keywords)
                    
                    # 检查match_status字段
                    if not has_postpone_flag and match.match_status:
                        status_keywords = ['延期', '推迟', '改期', 'postponed', 'delayed', 'cancelled']
                        has_postpone_flag = any(keyword in str(match.match_status).lower() for keyword in status_keywords)
                    
                    if not has_postpone_flag:
                        # 标记为异常状态（使用match_status字段）
                        match.match_status = 'Abnormal'
                        localdb.update(match, close=False)
                        abnormal_count += 1
                        home_name = match.home_team_all_name or match.home_team_abb_name or '未知'
                        away_name = match.away_team_all_name or match.away_team_abb_name or '未知'
                        logger.warning(f"⚠️ 比赛异常: {home_name} vs {away_name}, 比赛日期: {match.match_date}, 已超过4天")
                        continue
                
                valid_matches.append(match)
            
            if abnormal_count > 0:
                logger.info(f'已标记 {abnormal_count} 场异常比赛')
            
            if not valid_matches:
                logger.info('没有有效的比赛需要获取赛果')
                return []
            
            logger.info(f'有效比赛数: {len(valid_matches)}')
            
            # 3. 统计时间范围
            match_dates = [m.match_date for m in valid_matches if m.match_date]
            if not match_dates:
                logger.warning('无法提取比赛日期')
                return []
            
            min_date = min(match_dates)
            max_date = max(match_dates)
            
            logger.info(f'赛果时间范围: {min_date} 到 {max_date}')
            
            # 4. 使用时间范围向 API 请求赛果
            results = self.api.get_basketball_match_results(
                match_begin_date=min_date,
                match_end_date=max_date
            )
            
            if not results:
                logger.info('API 返回的赛果为空')
                return []
            
            logger.info(f'成功获取 {len(results)} 条比赛结果')
            return results
            
        except Exception as e:
            logger.error(f'获取比赛结果失败：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _match_game_by_name_and_time(self, result_data: dict) -> TcbkMatch:
        """
        通过队名和开赛时间匹配数据库中的比赛
        
        Args:
            result_data: API 返回的赛果数据
            
        Returns:
            TcbkMatch: 匹配到的比赛记录，未找到返回 None
        """
        from datetime import datetime
        
        # 获取 API 返回的信息
        home_team_name = result_data.get('allHomeTeam') or result_data.get('homeTeam')
        away_team_name = result_data.get('allAwayTeam') or result_data.get('awayTeam')
        match_date_str = result_data.get('matchDate')
        
        if not all([home_team_name, away_team_name, match_date_str]):
            logger.warning(f"赛果数据缺少必要字段")
            return None
        
        try:
            # 解析比赛日期
            match_date = datetime.strptime(match_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"无法解析比赛日期: {match_date_str}")
            return None
        
        # 查询数据库中该日期的所有比赛（TcbkMatch没有status字段，直接按日期查询）
        matches = localdb.query(TcbkMatch).filter(
            TcbkMatch.match_date == match_date_str
        ).all()
        
        if not matches:
            logger.debug(f"未在数据库中找到 {match_date_str} 的比赛")
            return None
        
        # 遍历匹配队名
        for match in matches:
            db_home_team_name = match.home_team_all_name or match.home_team_abb_name
            db_away_team_name = match.away_team_all_name or match.away_team_abb_name
            
            if not db_home_team_name or not db_away_team_name:
                continue
            
            # 匹配主队名称
            home_match = (
                db_home_team_name == home_team_name or
                (match.home_team_abb_name and match.home_team_abb_name == home_team_name)
            )
            
            # 匹配客队名称
            away_match = (
                db_away_team_name == away_team_name or
                (match.away_team_abb_name and match.away_team_abb_name == away_team_name)
            )
            
            if home_match and away_match:
                logger.debug(f"成功匹配比赛: {home_team_name} vs {away_team_name}, match_id={match.match_id}")
                return match
        
        logger.debug(f"未找到匹配的比赛: {home_team_name} vs {away_team_name}, 日期: {match_date_str}")
        return None
    
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
        matched_count = 0
        unmatched_count = 0
        
        for result_data in results:
            try:
                # 通过队名和开赛时间匹配数据库中的比赛
                match = self._match_game_by_name_and_time(result_data)
                
                if not match:
                    unmatched_count += 1
                    logger.debug(f"赛果无法匹配到数据库中的比赛，跳过")
                    continue
                
                matched_count += 1
                match_id = match.match_id
                
                # 检查 API 返回的比赛状态
                match_result_status = result_data.get('matchResultStatus', '')
                result_status = result_data.get('resultStatus', '')
                pool_status = result_data.get('poolStatus', '')
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = False
                abnormal_reason = ''
                
                # 检查比分是否为异常值
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                if home_score == '取消' or away_score == '取消' or home_score == 'N/A' or home_score == 0:
                    is_abnormal = True
                    abnormal_reason = '比赛取消'
                elif result_status == '取消' or result_status == '延期' or result_status == '腰斩':
                    is_abnormal = True
                    abnormal_reason = f'比赛{result_status}'
                elif pool_status == 'Cancelled' or pool_status == 'Postponed':
                    is_abnormal = True
                    abnormal_reason = f'比赛{pool_status}'
                
                # 转换 API 字段名为数据库字段名
                db_result_data = {}
                for key, value in result_data.items():
                    db_key = self._convert_api_field_to_db(key)
                    
                    if hasattr(TcbkResult, db_key):
                        db_result_data[db_key] = value
                
                # 保存或更新赛果记录
                existing_result = localdb.query(TcbkResult).filter_by(match_id=match_id).first()
                
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
                
                if is_abnormal:
                    # 异常比赛：标记match_status为Abnormal
                    match.match_status = 'Abnormal'
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, match_id={match_id}")
                
                logger.info(f"✅ 保存赛果成功: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, 比分: {result_data.get('homeScore')}-{result_data.get('awayScore')}")
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"赛果统计 - 总数: {len(results)}, 匹配: {matched_count}, 未匹配: {unmatched_count}, 保存: {saved_count}")
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
