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
    
    def fetch_match_results(self) -> tuple:
        """
        获取比赛结果数据
        
        Returns:
            tuple: (results, pending_matches) - API返回的赛果列表和待匹配的比赛列表
        """
        try:
            logger.info('开始获取体彩足球比赛结果...')
            
            # 1. 查询数据库中需要获取赛果的比赛
            from datetime import timedelta, datetime
            from sqlalchemy import func
            
            cutoff_time = datetime.now() - timedelta(hours=4)
            abnormal_cutoff_time = datetime.now() - timedelta(days=4)
            
            pending_matches = localdb.query(TczqMatch).filter(
                TczqMatch.status == 0,  # 未结束
                TczqMatch.match_time < cutoff_time  # 比赛已结束4小时以上
            ).all()
            
            if not pending_matches:
                logger.info('没有需要获取赛果的比赛')
                return [], []
            
            # 2. 检查并标记异常比赛（开赛超过4天且无延期标识）
            abnormal_count = 0
            valid_matches = []
            
            for match in pending_matches:
                # 检查是否开赛超过4天
                if match.match_time and match.match_time < abnormal_cutoff_time:
                    # 检查是否有延期标识（remark中包含延期相关关键词）
                    has_postpone_flag = False
                    if match.remark:
                        postpone_keywords = ['延期', '推迟', '改期', 'postpone', 'delayed']
                        has_postpone_flag = any(keyword in str(match.remark).lower() for keyword in postpone_keywords)
                    
                    if not has_postpone_flag:
                        # 标记为异常状态 (status=2)
                        match.status = 2
                        localdb.update(match, close=False)
                        abnormal_count += 1
                        home_name = match.home_team.team_full_name if match.home_team else '未知'
                        away_name = match.away_team.team_full_name if match.away_team else '未知'
                        logger.warning(f"⚠️ 比赛异常: {home_name} vs {away_name}, 开赛时间: {match.match_time}, 已超过4天")
                        continue
                
                valid_matches.append(match)
            
            if abnormal_count > 0:
                logger.info(f'已标记 {abnormal_count} 场异常比赛')
            
            # 输出最终需要获取赛果的比赛数
            logger.info(f'需要获取赛果的比赛: {len(valid_matches)} 场')
            
            if not valid_matches:
                logger.info('没有有效的比赛需要获取赛果')
                return [], []
            
            # 3. 统计时间范围
            match_dates = [m.match_time.date() for m in valid_matches if m.match_time]
            if not match_dates:
                logger.warning('无法提取比赛日期')
                return [], []
            
            min_date = min(match_dates)
            max_date = max(match_dates)
            
            logger.info(f'赛果时间范围: {min_date} 到 {max_date}')
            
            # 4. 使用时间范围向 API 请求赛果
            results = self.api.get_football_match_result(
                match_begin_date=min_date.strftime('%Y-%m-%d'),
                match_end_date=max_date.strftime('%Y-%m-%d')
            )
            
            if not results:
                logger.info('API 返回的赛果为空')
                return [], valid_matches
            
            logger.info(f'成功获取 {len(results)} 条比赛结果')
            return results, valid_matches
            
        except Exception as e:
            logger.error(f'获取比赛结果失败：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return [], []
    
    def _match_game_by_name_and_time(self, result_data: Dict) -> TczqMatch:
        """
        通过队名和开赛时间匹配数据库中的比赛
        
        Args:
            result_data: API 返回的赛果数据
            
        Returns:
            TczqMatch: 匹配到的比赛记录，未找到返回 None
        """
        from datetime import datetime
        
        # 获取 API 返回的信息
        home_team_name = result_data.get('allHomeTeam') or result_data.get('homeTeam')
        away_team_name = result_data.get('allAwayTeam') or result_data.get('awayTeam')
        match_date_str = result_data.get('matchDate')
        
        if not all([home_team_name, away_team_name, match_date_str]):
            logger.warning(f"赛果数据缺少必要字段: {result_data}")
            return None
        
        try:
            # 解析比赛日期
            match_date = datetime.strptime(match_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"无法解析比赛日期: {match_date_str}")
            return None
        
        # 查询数据库中该日期的所有未结束比赛
        from sqlalchemy import func
        matches = localdb.query(TczqMatch).filter(
            func.date(TczqMatch.match_time) == match_date,
            TczqMatch.status == 0  # 只查询未结束的比赛
        ).all()
        
        if not matches:
            logger.debug(f"未在数据库中找到 {match_date_str} 的未结束比赛")
            return None
        
        # 遍历匹配队名
        for match in matches:
            db_home_team = match.home_team
            db_away_team = match.away_team
            
            if not db_home_team or not db_away_team:
                continue
            
            # 匹配主队名称（支持全称和简称）
            home_match = (
                db_home_team.team_full_name == home_team_name or
                db_home_team.team_short_name == home_team_name
            )
            
            # 匹配客队名称（支持全称和简称）
            away_match = (
                db_away_team.team_full_name == away_team_name or
                db_away_team.team_short_name == away_team_name
            )
            
            if home_match and away_match:
                logger.debug(f"成功匹配比赛: {home_team_name} vs {away_team_name}, match_id={match.match_id}")
                return match
        
        logger.debug(f"未找到匹配的比赛: {home_team_name} vs {away_team_name}, 日期: {match_date_str}")
        return None
    
    def save_results_to_db(self, results: List[Dict], pending_matches: List[TczqMatch] = None) -> int:
        """
        保存比赛结果到数据库
        
        Args:
            results: API 返回的比赛结果列表
            pending_matches: 需要获取赛果的比赛列表（从 fetch_match_results 传入）
            
        Returns:
            int: 成功保存的记录数
        """
        if not results:
            return 0
        
        saved_count = 0
        matched_count = 0
        unmatched_api_count = 0  # API 返回但无法匹配的
        
        # 如果没有传入 pending_matches，则使用原来的逻辑（向后兼容）
        if pending_matches is None:
            logger.warning("未传入待匹配比赛列表，使用旧逻辑")
            return self._save_results_old_logic(results)
        
        # 构建 API 赛果的快速查找字典：key = (日期, 主队名, 客队名)
        api_results_map = {}
        for result_data in results:
            home_team = result_data.get('allHomeTeam') or result_data.get('homeTeam', '')
            away_team = result_data.get('allAwayTeam') or result_data.get('awayTeam', '')
            match_date = result_data.get('matchDate', '')
            
            if home_team and away_team and match_date:
                key = (match_date, home_team, away_team)
                api_results_map[key] = result_data
        
        logger.info(f"API 返回 {len(results)} 条赛果，构建索引 {len(api_results_map)} 条")
        
        # 遍历需要获取赛果的比赛，去 API 结果中查找匹配
        for match in pending_matches:
            try:
                # 构建匹配键
                home_name = match.home_team.team_full_name if match.home_team else ''
                away_name = match.away_team.team_full_name if match.away_team else ''
                match_date_str = match.match_time.strftime('%Y-%m-%d') if match.match_time else ''
                
                if not all([home_name, away_name, match_date_str]):
                    logger.debug(f"比赛信息不完整，跳过: match_id={match.match_id}")
                    continue
                
                # 在 API 结果中查找匹配
                api_result = api_results_map.get((match_date_str, home_name, away_name))
                
                if not api_result:
                    # 尝试反向匹配（主客场互换）
                    api_result = api_results_map.get((match_date_str, away_name, home_name))
                    if api_result:
                        logger.debug(f"主客场互换匹配: {home_name} vs {away_name}")
                
                if not api_result:
                    unmatched_api_count += 1
                    logger.debug(f"未找到赛果: {home_name} vs {away_name} ({match_date_str})")
                    continue
                
                matched_count += 1
                match_id = match.match_id
                result_data = api_result
                
                # 检查 API 返回的比赛状态
                match_result_status = result_data.get('matchResultStatus', '')
                result_status = result_data.get('resultStatus', '')
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = False
                abnormal_reason = ''
                
                # 检查比分是否为异常值
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                if home_score == '取消' or away_score == '取消' or home_score == 'N/A':
                    is_abnormal = True
                    abnormal_reason = '比赛取消'
                elif result_status == '取消' or result_status == '延期' or result_status == '腰斩':
                    is_abnormal = True
                    abnormal_reason = f'比赛{result_status}'
                elif match_result_status == '3':  # 假设3表示异常状态
                    is_abnormal = True
                    abnormal_reason = '比赛异常'
                
                # 转换 API 字段名为数据库字段名
                db_result_data = {}
                for key, value in result_data.items():
                    db_key = self._convert_api_field_to_db(key)
                    # 特殊字段映射
                    field_mapping = {
                        'home_score': 'home_team_goals',
                        'away_score': 'away_team_goals',
                        'half_home_score': 'half_time_home_goals',
                        'half_away_score': 'half_time_away_goals'
                    }
                    if db_key in field_mapping:
                        db_key = field_mapping[db_key]
                    
                    # 处理异常比分值：将 'N/A'、'取消' 等转换为 None
                    if db_key in ['home_team_goals', 'away_team_goals', 'half_time_home_goals', 'half_time_away_goals']:
                        if value in ['N/A', '取消', '-', ''] or value is None:
                            value = None
                        else:
                            try:
                                value = int(value) if value else None
                            except (ValueError, TypeError):
                                logger.warning(f"比分格式错误: {key}={value}, 设置为 None")
                                value = None
                    
                    if hasattr(TczqMatchResult, db_key):
                        db_result_data[db_key] = value
                
                if is_abnormal:
                    # 异常比赛：标记状态为2，但仍保存赛果记录
                    match.status = 2
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {home_name} vs {away_name}, match_id={match_id}")
                else:
                    # 正常比赛：标记状态为1
                    match.status = 1
                    localdb.update(match, close=False)
                
                # 保存或更新赛果记录
                existing_result = localdb.query(TczqMatchResult).filter_by(match_id=match_id).first()
                
                if existing_result:
                    # 更新现有记录
                    for key, value in db_result_data.items():
                        setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                    logger.debug(f"更新赛果：match_id={match_id}")
                else:
                    # 创建新记录
                    if db_result_data:
                        new_result = TczqMatchResult(**db_result_data)
                        localdb.add(new_result, close=False)
                        logger.debug(f"新增赛果：match_id={match_id}")
                
                logger.info(f"✅ 保存赛果成功: {home_name} vs {away_name}, 比分: {home_score}-{away_score}")
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败 (match_id={match.match_id}): {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"赛果统计 - 待匹配: {len(pending_matches)}, API返回: {len(results)}, 匹配成功: {matched_count}, 未匹配: {unmatched_api_count}, 保存: {saved_count}")
        return saved_count
    
    def _save_results_old_logic(self, results: List[Dict]) -> int:
        """
        旧的保存逻辑（向后兼容）
        遍历 API 返回的赛果，去数据库中查找匹配
        """
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
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = False
                abnormal_reason = ''
                
                # 检查比分是否为异常值
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                if home_score == '取消' or away_score == '取消' or home_score == 'N/A':
                    is_abnormal = True
                    abnormal_reason = '比赛取消'
                elif result_status == '取消' or result_status == '延期' or result_status == '腰斩':
                    is_abnormal = True
                    abnormal_reason = f'比赛{result_status}'
                elif match_result_status == '3':  # 假设3表示异常状态
                    is_abnormal = True
                    abnormal_reason = '比赛异常'
                
                # 转换 API 字段名为数据库字段名
                db_result_data = {}
                for key, value in result_data.items():
                    db_key = self._convert_api_field_to_db(key)
                    # 特殊字段映射
                    field_mapping = {
                        'home_score': 'home_team_goals',
                        'away_score': 'away_team_goals',
                        'half_home_score': 'half_time_home_goals',
                        'half_away_score': 'half_time_away_goals'
                    }
                    if db_key in field_mapping:
                        db_key = field_mapping[db_key]
                    
                    if hasattr(TczqMatchResult, db_key):
                        db_result_data[db_key] = value
                
                if is_abnormal:
                    # 异常比赛：标记状态为2，但仍保存赛果记录
                    match.status = 2
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, match_id={match_id}")
                else:
                    # 正常比赛：标记状态为1
                    match.status = 1
                    localdb.update(match, close=False)
                
                # 保存或更新赛果记录
                existing_result = localdb.query(TczqMatchResult).filter_by(match_id=match_id).first()
                
                if existing_result:
                    # 更新现有记录
                    for key, value in db_result_data.items():
                        setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                    logger.debug(f"更新赛果：match_id={match_id}")
                else:
                    # 创建新记录
                    if db_result_data:
                        new_result = TczqMatchResult(**db_result_data)
                        localdb.add(new_result, close=False)
                        logger.debug(f"新增赛果：match_id={match_id}")
                
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
            logger.info('开始获取并保存体彩足球比赛结果...')
                
            # 获取比赛结果和待匹配列表
            results, pending_matches = self.fetch_match_results()
                
            if not pending_matches:
                logger.warning('没有需要获取赛果的比赛')
                return False
                
            if not results:
                logger.warning('API 未返回赛果数据')
                return False
                
            logger.info(f'成功获取 {len(results)} 条比赛结果')
                
            # 保存到数据库（传入待匹配列表）
            saved_count = self.save_results_to_db(results, pending_matches)
                
            logger.info(f'成功保存 {saved_count} 条赛果记录')
            return saved_count > 0
                
        except Exception as e:
            logger.error(f'获取并保存赛果异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return False
