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
            # logger.info('开始获取体彩足球比赛结果...')  # 减少日志输出
            
            # 1. 查询数据库中需要获取赛果的比赛
            from datetime import timedelta, datetime
            from sqlalchemy import func
            
            cutoff_time = datetime.now() - timedelta(hours=4)
            abnormal_cutoff_time = datetime.now() - timedelta(days=4)
            
            # 关键修复：只有 status < 2 的比赛才需要获取赛果
            # - status=0: 待开赛（实际已开赛但未更新状态）
            # - status=1: 进行中
            # - status>=2: 已有明确结果或已获取赛果，不需要再获取
            pending_matches = localdb.query(TczqMatch).filter(
                TczqMatch.match_time < cutoff_time,  # 比赛已结束4小时以上
                TczqMatch.status < 2  # 只获取 status < 2 的比赛（排除已完成和异常的）
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
                        # 标记为异常状态 (status=9)
                        match.status = 9
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
            logger.debug(f'需要获取赛果的比赛: {len(valid_matches)} 场')
            
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
            
            logger.debug(f'赛果时间范围: {min_date} 到 {max_date}')
            
            # 4. 使用时间范围向 API 请求赛果
            try:
                results = self.api.get_football_match_result(
                    match_begin_date=min_date.strftime('%Y-%m-%d'),
                    match_end_date=max_date.strftime('%Y-%m-%d')
                )
            except Exception as e:
                logger.warning(f'API 请求失败，跳过本次赛果获取: {e}')
                return [], valid_matches
            
            if not results:
                logger.info('API 返回的赛果为空')
                return [], valid_matches
            
            logger.debug(f'成功获取 {len(results)} 条比赛结果')
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
        from app.database import TeamAlias
        
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
        
        # 查询数据库中该日期的所有未获取赛果的比赛
        from sqlalchemy import func
        matches = localdb.query(TczqMatch).filter(
            func.date(TczqMatch.match_time) == match_date,
            TczqMatch.status < 2  # 只匹配 status < 2 的比赛（排除已完成和异常的）
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
            
            # 匹配主队名称（支持全称、简称、别名）
            home_match = self._match_team_name(db_home_team, home_team_name)
            
            # 匹配客队名称（支持全称、简称、别名）
            away_match = self._match_team_name(db_away_team, away_team_name)
            
            if home_match and away_match:
                logger.debug(f"成功匹配比赛: {home_team_name} vs {away_team_name}, match_id={match.match_id}")
                return match
        
        # 主队名匹配失败，尝试用客队名+时间反向匹配
        logger.debug(f"主队名匹配失败，尝试反向匹配: {home_team_name} vs {away_team_name}")
        for match in matches:
            db_home_team = match.home_team
            db_away_team = match.away_team
            
            if not db_home_team or not db_away_team:
                continue
            
            # 只匹配客队名
            away_match = self._match_team_name(db_away_team, away_team_name)
            
            if away_match:
                # 客队名匹配成功，认为是同一场比赛
                logger.info(f"✓ 通过客队名+时间反向匹配成功: {away_team_name}, match_id={match.match_id}")
                
                # 为未匹配的主队添加别名
                if db_home_team:
                    self._add_team_alias_if_not_exists(db_home_team.id, home_team_name, 'tczq_api')
                    logger.info(f"✓ 为主队添加别名: {db_home_team.team_full_name} <- {home_team_name}")
                
                return match
        
        logger.debug(f"未找到匹配的比赛: {home_team_name} vs {away_team_name}, 日期: {match_date_str}")
        return None
    
    def _match_team_name(self, team, team_name: str) -> bool:
        """
        匹配球队名称（按优先级：全称 -> 简称 -> 别名）
        
        Args:
            team: Team对象
            team_name: 待匹配的队名
            
        Returns:
            bool: 是否匹配成功
        """
        if not team or not team_name:
            return False
        
        # 1. 匹配全称
        if team.team_full_name == team_name:
            return True
        
        # 2. 匹配简称
        if team.team_short_name == team_name:
            return True
        
        # 3. 匹配英文简称
        if team.team_short_en_name and team.team_short_en_name == team_name:
            return True
        
        # 4. 匹配别名表
        from app.database import TeamAlias
        alias = localdb.query(TeamAlias).filter_by(
            team_id=team.id,
            alias_name=team_name
        ).first()
        
        if alias:
            return True
        
        return False
    
    def _add_team_alias_if_not_exists(self, team_id: int, alias_name: str, source_type: str = 'tczq'):
        """
        为球队添加别名（如果不存在）
        
        Args:
            team_id: 球队ID
            alias_name: 别名
            source_type: 来源类型
        """
        from app.database import TeamAlias
        
        # 检查别名是否已存在
        existing = localdb.query(TeamAlias).filter_by(
            team_id=team_id,
            alias_name=alias_name
        ).first()
        
        if not existing:
            # 添加新别名
            new_alias = TeamAlias(
                team_id=team_id,
                alias_name=alias_name,
                source_type=source_type,
                is_primary=0
            )
            localdb.add(new_alias, close=False)
            logger.debug(f"添加球队别名: team_id={team_id}, alias={alias_name}")
    
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
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 使用统一的状态映射函数转换为内部状态码
                from app.common.match_status import map_to_internal_status, get_status_desc
                internal_status = map_to_internal_status('tczq', match_result_status)
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = False
                abnormal_reason = ''
                
                # 关键修复：根据 matchResultStatus 判断比赛状态
                # '1' = 进行中/未结束（比分可能是 'N/A'），不应该获取赛果
                # '2' = 已完成，应该获取赛果
                # '3' = 异常
                if match_result_status == '1':
                    # 比赛未结束，跳过不处理
                    logger.debug(f"⏰ 比赛未结束: {home_name} vs {away_name}, matchResultStatus={match_result_status}, 比分={home_score}-{away_score}")
                    continue  # 跳过这场比赛，不保存赛果
                elif match_result_status == '2':
                    # 比赛已完成，正常处理
                    pass
                elif match_result_status == '3':
                    # 异常状态
                    is_abnormal = True
                    abnormal_reason = f'比赛异常 (matchResultStatus={match_result_status})'
                else:
                    # 未知状态，默认为已完成
                    logger.debug(f"未知状态 matchResultStatus={match_result_status}, 按已完成处理")
                
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
                    # 异常比赛：使用映射后的状态码
                    match.status = internal_status
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {home_name} vs {away_name}, match_id={match_id}")
                else:
                    # 正常比赛：成功保存赛果后，标记状态为8（已获取赛果）
                    match.status = 8
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
                
                logger.debug(f"✅ 保存赛果成功: {home_name} vs {away_name}, 比分: {home_score}-{away_score}")  # 改为DEBUG级别
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败 (match_id={match.match_id}): {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        # 输出赛果获取统计（总结性）
        if len(pending_matches) > 0:
            summary_parts = []
            if saved_count > 0:
                summary_parts.append(f"获取{saved_count}场")
            if unmatched_api_count > 0:
                summary_parts.append(f"未匹配{unmatched_api_count}场")
            
            if summary_parts:
                logger.info(f"竞彩足球赛果: {', '.join(summary_parts)}")
            else:
                logger.info("竞彩足球赛果: 无变化")
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
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 使用统一的状态映射函数转换为内部状态码
                from app.common.match_status import map_to_internal_status, get_status_desc
                internal_status = map_to_internal_status('tczq', match_result_status)
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = False
                abnormal_reason = ''
                
                # 关键修复：根据 matchResultStatus 判断比赛状态
                if match_result_status == '1':
                    # 比赛未结束，跳过不处理
                    logger.debug(f"⏰ 比赛未结束: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, matchResultStatus={match_result_status}")
                    continue  # 跳过这场比赛
                elif match_result_status == '2':
                    # 比赛已完成，正常处理
                    pass
                elif match_result_status == '3':
                    # 异常状态
                    is_abnormal = True
                    abnormal_reason = f'比赛异常 (matchResultStatus={match_result_status})'
                else:
                    # 未知状态，默认为已完成
                    logger.debug(f"未知状态 matchResultStatus={match_result_status}, 按已完成处理")
                
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
                    # 异常比赛：使用映射后的状态码
                    match.status = internal_status
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, match_id={match_id}")
                else:
                    # 正常比赛：成功保存赛果后，标记状态为8（已获取赛果）
                    match.status = 8
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
                
                logger.debug(f"✅ 保存赛果成功: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, 比分: {result_data.get('homeScore')}-{result_data.get('awayScore')}")  # 改为DEBUG级别
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        # 输出赛果获取统计
        if len(results) > 0:
            success_rate = (saved_count / len(results) * 100) if results else 0
            logger.info(f"赛果获取完成 - API返回: {len(results)}场, 成功: {saved_count}场, 未匹配: {unmatched_count}场, 成功率: {success_rate:.1f}%")
        return saved_count
    
    def get_and_save_results(self) -> bool:
        """
        获取并保存比赛结果
            
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        # logger.info('开始获取并保存体彩足球比赛结果...')  # 减少日志输出，由调用方统一记录
        try:
                
            # 获取比赛结果和待匹配列表
            results, pending_matches = self.fetch_match_results()
                
            if not pending_matches:
                logger.warning('没有需要获取赛果的比赛')
                return False
                
            if not results:
                logger.warning('API 未返回赛果数据')
                return False
            
            # 保存到数据库（传入待匹配列表）
            saved_count = self.save_results_to_db(results, pending_matches)
            
            return saved_count > 0
                
        except Exception as e:
            logger.error(f'获取并保存赛果异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return False
