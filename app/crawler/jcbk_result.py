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
    
    def fetch_match_results(self) -> tuple:
        """
        获取比赛结果数据
        
        Returns:
            list: 比赛结果列表
        """
        try:
            # logger.info('开始获取竞彩篮球比赛结果...')  # 减少日志输出
            
            # 1. 查询数据库中需要获取赛果的比赛
            from datetime import timedelta, datetime
            
            # TcbkMatch使用match_status字段
            # 关键修复：筛选条件应该是
            # 1. 最近7天的比赛（match_date >= seven_days_ago）
            # 2. 且未获取赛果（match_status != 8 AND match_status != 9）
            #    - match_status=8: 已获取赛果（正常完成）→ 不需要获取
            #    - match_status=9: 异常状态（延期、取消、腰斩等）→ 不需要获取
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            abnormal_cutoff_date = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
            
            pending_matches = localdb.query(TcbkMatch).filter(
                TcbkMatch.match_date >= seven_days_ago,
                TcbkMatch.match_status != 8,  # 排除已获取赛果
                TcbkMatch.match_status != 9   # 排除异常状态
            ).all()
            
            if not pending_matches:
                logger.info('没有需要获取赛果的比赛')
                return [], []
            
            # 2. 过滤未开场比赛并检查异常比赛
            abnormal_count = 0
            not_started_count = 0
            valid_matches = []
            now = datetime.now()
            
            for match in pending_matches:
                # 检查比赛是否已经开始（开赛时间距离现在不超过4小时的不获取赛果）
                if match.match_date and match.match_time:
                    try:
                        # 组合日期和时间字符串
                        match_datetime_str = f"{match.match_date} {match.match_time}"
                        # 尝试解析为datetime对象
                        match_datetime = datetime.strptime(match_datetime_str, '%Y-%m-%d %H:%M')
                        
                        # 计算距离开赛的时间差（小时）
                        hours_until_match = (match_datetime - now).total_seconds() / 3600
                        
                        # 如果距离开赛还有超过-4小时（即还没开赛或开赛不到4小时），跳过
                        if hours_until_match > -4:
                            not_started_count += 1
                            home_name = match.home_team_all_name or match.home_team_abb_name or '未知'
                            away_name = match.away_team_all_name or match.away_team_abb_name or '未知'
                            logger.debug(f"⏰ 比赛未结束: {home_name} vs {away_name}, 开赛时间: {match_datetime_str}, 距离开赛还有 {hours_until_match:.1f} 小时")
                            continue
                    except ValueError as e:
                        logger.warning(f"无法解析比赛时间: {match.match_date} {match.match_time}, 错误: {e}")
                        # 如果无法解析时间，继续处理（可能是旧数据）
                
                # 检查是否开赛超过4天且无延期标识（异常比赛）
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
                        # 标记为异常状态 (status=2)
                        match.match_status = 2
                        localdb.update(match, close=False)
                        abnormal_count += 1
                        home_name = match.home_team_all_name or match.home_team_abb_name or '未知'
                        away_name = match.away_team_all_name or match.away_team_abb_name or '未知'
                        logger.warning(f"⚠️ 比赛异常: {home_name} vs {away_name}, 比赛日期: {match.match_date}, 已超过4天")
                        continue
                
                valid_matches.append(match)
            
            if abnormal_count > 0:
                logger.info(f'已标记 {abnormal_count} 场异常比赛')
            
            if not_started_count > 0:
                logger.debug(f'跳过 {not_started_count} 场未结束的比赛')
            
            # 输出最终需要获取赛果的比赛数
            logger.info(f'需要获取赛果的比赛: {len(valid_matches)} 场')
            
            if not valid_matches:
                logger.info('没有有效的比赛需要获取赛果')
                return [], []
            
            # 3. 统计时间范围
            match_dates = [m.match_date for m in valid_matches if m.match_date]
            if not match_dates:
                logger.warning('无法提取比赛日期')
                return [], []
            
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
                return [], []
            
            logger.debug(f'成功获取 {len(results)} 条比赛结果')  # 改为DEBUG级别
            return results, valid_matches
            
        except Exception as e:
            logger.error(f'获取比赛结果失败：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return [], []
    
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
    
    def save_results_to_db(self, results: list, pending_matches: list = None) -> int:
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
        
        # 如果没有传入 pending_matches，则使用原来的逻辑（向后兼容）
        if pending_matches is None:
            logger.warning("未传入待匹配比赛列表，使用旧逻辑")
            return self._save_results_old_logic(results)
        
        saved_count = 0
        matched_count = 0
        unmatched_api_count = 0
        
        # 构建 API 赛果的快速查找字典
        api_results_map = {}
        for result_data in results:
            home_team = result_data.get('allHomeTeam') or result_data.get('homeTeam', '')
            away_team = result_data.get('allAwayTeam') or result_data.get('awayTeam', '')
            match_date = result_data.get('matchDate', '')
            
            if home_team and away_team and match_date:
                key = (match_date, home_team, away_team)
                api_results_map[key] = result_data
        
        # 遍历需要获取赛果的比赛，去 API 结果中查找匹配
        for match in pending_matches:
            try:
                home_name = match.home_team_all_name or match.home_team_abb_name or ''
                away_name = match.away_team_all_name or match.away_team_abb_name or ''
                match_date_str = match.match_date or ''
                
                if not all([home_name, away_name, match_date_str]):
                    logger.debug(f"比赛信息不完整，跳过: match_id={match.match_id}")
                    continue
                
                # 在 API 结果中查找匹配
                api_result = api_results_map.get((match_date_str, home_name, away_name))
                
                if not api_result:
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
                
                # 检查异常状态
                match_result_status = result_data.get('matchResultStatus', '')
                result_status = result_data.get('resultStatus', '')
                pool_status = result_data.get('poolStatus', '')
                api_status = result_data.get('status')  # 篮球API的status字段 (1=进行中, 2=已完成)
                
                # 使用统一的状态映射函数转换为内部状态码
                from app.common.match_status import map_to_internal_status, get_status_desc
                internal_status = map_to_internal_status('jcbk', api_status) if api_status is not None else 8  # 默认已完成
                
                is_abnormal = False
                abnormal_reason = ''
                
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 关键修复：根据 status 判断比赛状态
                # status=1: 进行中/未结束（比分可能是0-0），不应该获取赛果
                # status=2: 已完成，应该获取赛果
                if api_status == 1:
                    # 比赛未结束，跳过不处理
                    logger.debug(f"⏰ 比赛未结束: {home_name} vs {away_name}, status={api_status}, 比分={home_score}-{away_score}")
                    continue  # 跳过这场比赛，不保存赛果
                elif api_status == 2:
                    # 比赛已完成，正常处理
                    pass
                else:
                    # 未知状态，检查是否有明确的取消标识
                    if result_status in ['取消', '延期', '腰斩']:
                        is_abnormal = True
                        abnormal_reason = f'比赛{result_status}'
                    elif pool_status in ['Cancelled', 'Postponed']:
                        is_abnormal = True
                        abnormal_reason = f'比赛{pool_status}'
                
                # 转换字段
                db_result_data = {}
                for key, value in result_data.items():
                    db_key = self._convert_api_field_to_db(key)
                    if hasattr(TcbkResult, db_key):
                        db_result_data[db_key] = value
                
                # 保存或更新赛果记录
                existing_result = localdb.query(TcbkResult).filter_by(match_id=match_id).first()
                
                if existing_result:
                    for key, value in db_result_data.items():
                        setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                else:
                    if db_result_data:
                        new_result = TcbkResult(**db_result_data)
                        localdb.add(new_result, close=False)
                
                if is_abnormal:
                    # 异常比赛：使用映射后的状态码
                    match.match_status = internal_status
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {home_name} vs {away_name}, match_id={match_id}")
                else:
                    # 正常比赛：标记状态为2（已完成，已获取赛果）
                    match.match_status = 2
                    localdb.update(match, close=False)
                
                logger.debug(f"✅ 保存赛果成功: {home_name} vs {away_name}, 比分: {home_score}-{away_score}")  # 改为DEBUG级别
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败 (match_id={match.match_id}): {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        # 输出赛果获取统计
        if len(pending_matches) > 0:
            success_rate = (saved_count / len(pending_matches) * 100) if pending_matches else 0
            logger.info(f"赛果获取完成 - 需获取: {len(pending_matches)}场, 成功: {saved_count}场, 未匹配: {unmatched_api_count}场, 成功率: {success_rate:.1f}%")
        return saved_count
    
    def _save_results_old_logic(self, results: list) -> int:
        """旧的保存逻辑（向后兼容）"""
        saved_count = 0
        matched_count = 0
        unmatched_count = 0
        
        for result_data in results:
            try:
                match = self._match_game_by_name_and_time(result_data)
                
                if not match:
                    unmatched_count += 1
                    logger.debug(f"赛果无法匹配到数据库中的比赛，跳过")
                    continue
                
                matched_count += 1
                match_id = match.match_id
                
                match_result_status = result_data.get('matchResultStatus', '')
                result_status = result_data.get('resultStatus', '')
                pool_status = result_data.get('poolStatus', '')
                api_status = result_data.get('status')
                
                is_abnormal = False
                abnormal_reason = ''
                
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 关键修复：根据 status 判断比赛状态
                if api_status == 1:
                    # 比赛未结束，跳过不处理
                    logger.debug(f"⏰ 比赛未结束: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, status={api_status}")
                    continue  # 跳过这场比赛
                elif api_status == 2:
                    # 比赛已完成，正常处理
                    pass
                else:
                    # 未知状态，检查是否有明确的取消标识
                    if result_status in ['取消', '延期', '腰斩']:
                        is_abnormal = True
                        abnormal_reason = f'比赛{result_status}'
                    elif pool_status in ['Cancelled', 'Postponed']:
                        is_abnormal = True
                        abnormal_reason = f'比赛{pool_status}'
                
                db_result_data = {}
                for key, value in result_data.items():
                    db_key = self._convert_api_field_to_db(key)
                    if hasattr(TcbkResult, db_key):
                        db_result_data[db_key] = value
                
                existing_result = localdb.query(TcbkResult).filter_by(match_id=match_id).first()
                
                if existing_result:
                    for key, value in db_result_data.items():
                        setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                else:
                    if db_result_data:
                        new_result = TcbkResult(**db_result_data)
                        localdb.add(new_result, close=False)
                
                if is_abnormal:
                    # 异常比赛：标记状态为2（延期/取消等）
                    match.match_status = 2
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, match_id={match_id}")
                else:
                    # 正常比赛：标记状态为8（已完成，已获取赛果）
                    match.match_status = 8
                    localdb.update(match, close=False)
                
                logger.debug(f"✅ 保存赛果成功: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, 比分: {home_score}-{away_score}")  # 改为DEBUG级别
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
        # logger.info('开始获取并保存竞彩篮球比赛结果...')  # 减少日志输出，由调用方统一记录
        try:
                
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
                        
            if saved_count > 0:
                logger.info(f'成功保存 {saved_count} 条赛果记录')
            return saved_count > 0
                
        except Exception as e:
            logger.error(f'获取并保存赛果异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return False
