# -*- coding: utf-8 -*-
"""
北京单场赛果获取器
从 500 彩票网爬取北京单场比赛结果并保存到数据库
"""
import os
import sys
import re
from datetime import datetime, timedelta
from typing import Dict, List
from bs4 import BeautifulSoup

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.common._utils import req_info, handle_team_name
from app.log import bjdc_log as logger
from app.database import (
    localdb,
    League, Team,
    BjdcMatch,
    BjdcMatchResult
)


class BjdcResultCollector:
    """
    北京单场赛果获取器（网页爬虫）
    """
    
    def __init__(self):
        """
        初始化赛果获取器实例
        """
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
    
    def _parse_match_results_from_html(self, soup: BeautifulSoup, date_str: str) -> List[Dict]:
        """
        从 HTML 页面中解析比赛结果数据
        
        Args:
            soup: BeautifulSoup 对象
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            list: 比赛结果列表
        """
        results = []
        
        try:
            # 查找所有包含球队名称的元素（主队或客队）
            home_names = soup.find_all('span', class_='mainName')
            away_names = soup.find_all('span', class_='clientName')
            
            # 每场比赛有一个主队和一个客队
            match_count = min(len(home_names), len(away_names))
            
            for i in range(match_count):
                try:
                    home_span = home_names[i]
                    away_span = away_names[i]
                    
                    # 向上找到比赛行 tr
                    match_row = home_span.find_parent('tr')
                    if not match_row:
                        continue
                    
                    # 提取比赛 ID（从 tr 的 id 属性）
                    tr_id = match_row.get('id', '')  # 例如: a1405831
                    match_id = tr_id.replace('a', '') if tr_id.startswith('a') else tr_id
                    
                    # 提取联赛名称
                    league_td = match_row.find('td', class_='ssbox_01')
                    league_name = league_td.get_text(strip=True) if league_td else ''
                    
                    # 提取时间
                    time_td = match_row.find_all('td')[2] if len(match_row.find_all('td')) > 2 else None
                    time_text = time_td.get_text(strip=True) if time_td else ''  # 例如: 04-13 13:00
                    
                    # 提取状态
                    status_td = match_row.find_all('td')[3] if len(match_row.find_all('td')) > 3 else None
                    status_text = status_td.get_text(strip=True) if status_td else ''  # '完' 表示结束
                    
                    # 提取主队名称
                    home_team_name = home_span.get_text(strip=True)
                    
                    # 提取客队名称
                    away_team_name = away_span.get_text(strip=True)
                    
                    # 提取全场比分
                    score_td = match_row.find_all('td')[5] if len(match_row.find_all('td')) > 5 else None
                    full_score = score_td.get_text(strip=True) if score_td else ''  # 例如: 2-2
                    
                    # 解析比分
                    home_score = None
                    away_score = None
                    if '-' in full_score:
                        parts = full_score.split('-')
                        if len(parts) == 2:
                            try:
                                home_score = int(parts[0].strip())
                                away_score = int(parts[1].strip())
                            except ValueError:
                                pass
                    
                    # 提取半场比分
                    half_score_td = match_row.find_all('td')[7] if len(match_row.find_all('td')) > 7 else None
                    half_score_text = half_score_td.get_text(strip=True) if half_score_td else ''  # 例如: 0 - 0
                    
                    half_home_score = None
                    half_away_score = None
                    if '-' in half_score_text:
                        parts = half_score_text.split('-')
                        if len(parts) == 2:
                            try:
                                half_home_score = int(parts[0].strip())
                                half_away_score = int(parts[1].strip())
                            except ValueError:
                                pass
                    
                    # 构建结果字典
                    result_data = {
                        'matchId': match_id,
                        'leagueName': league_name,
                        'homeTeam': home_team_name,
                        'awayTeam': away_team_name,
                        'matchDate': date_str,
                        'matchTime': time_text,
                        'status': status_text,
                        'homeScore': home_score,
                        'awayScore': away_score,
                        'halfHomeScore': half_home_score,
                        'halfAwayScore': half_away_score,
                    }
                    
                    results.append(result_data)
                    
                except Exception as e:
                    logger.debug(f"解析第 {i+1} 场比赛失败: {e}")
                    continue
            
            logger.debug(f"{date_str}: 解析到 {len(results)} 场比赛")
            
        except Exception as e:
            logger.error(f"解析 HTML 失败 ({date_str}): {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return results
    
    def fetch_match_results(self) -> tuple:
        """
        从 500 彩票网爬取比赛结果数据
        
        Returns:
            tuple: (results, pending_matches) - 爬取的赛果列表和待匹配的比赛列表
        """
        try:
            logger.info('开始获取北京单场比赛结果...')
            
            # 1. 查询数据库中需要获取赛果的比赛
            from sqlalchemy import func
            
            cutoff_time = self.nowtime - timedelta(hours=4)
            abnormal_cutoff_time = self.nowtime - timedelta(days=4)
            
            pending_matches = localdb.query(BjdcMatch).filter(
                BjdcMatch.status == 0,  # 未结束
                BjdcMatch.match_time < cutoff_time  # 比赛已结束4小时以上
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
            
            # 3. 统计时间范围，确定需要爬取的日期
            match_dates = set()
            for m in valid_matches:
                if m.match_time:
                    match_dates.add(m.match_time.date())
            
            if not match_dates:
                logger.warning('无法提取比赛日期')
                return [], []
            
            logger.info(f'赛果时间范围: {min(match_dates)} 到 {max(match_dates)}, 共 {len(match_dates)} 天')
            
            # 4. 从 500 彩票网爬取每天的赛果
            all_results = []
            for match_date in sorted(match_dates):
                date_str = match_date.strftime('%Y-%m-%d')
                logger.info(f'爬取 {date_str} 的赛果...')
                
                url = f'https://live.500.com/wanchang.php?e={date_str}'
                soup = req_info(url)
                
                if not soup:
                    logger.warning(f'爬取 {date_str} 失败')
                    continue
                
                # 解析页面中的比赛数据
                day_results = self._parse_match_results_from_html(soup, date_str)
                all_results.extend(day_results)
                logger.info(f'{date_str}: 爬取到 {len(day_results)} 场比赛')
            
            logger.info(f'总共爬取到 {len(all_results)} 条比赛结果')
            return all_results, valid_matches
            
        except Exception as e:
            logger.error(f'获取比赛结果失败：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return [], []
    
    def _find_team_by_alias(self, api_team_name: str, match_date_str: str, is_home: bool = True) -> 'Team':
        """
        通过 API 返回的队名，在数据库中查找对应的球队（支持别名匹配）
        
        Args:
            api_team_name: API 返回的球队名称
            match_date_str: 比赛日期字符串
            is_home: 是否为主队（用于日志）
            
        Returns:
            Team: 找到的球队对象，未找到返回 None
        """
        from app.database import Team, TeamAlias
        from sqlalchemy import func
        
        if not api_team_name:
            return None
        
        # 关键修复：确保事务有效
        try:
            if localdb.session and not localdb.session.is_active:
                logger.warning("检测到无效事务，执行回滚 (_find_team_by_alias)")
                localdb.rollback()
        except Exception:
            pass
        
        try:
            # 1. 先尝试通过全称或简称直接匹配
            team = localdb.query(Team).filter(
                (Team.team_full_name == api_team_name) | 
                (Team.team_short_name == api_team_name)
            ).first()
            
            if team:
                logger.debug(f"直接匹配成功: {api_team_name} -> {team.team_full_name}")
                return team
            
            # 2. 通过别名表匹配
            alias = localdb.query(TeamAlias).filter(
                TeamAlias.alias_name == api_team_name
            ).first()
            
            if alias:
                team = localdb.query(Team).filter_by(id=alias.team_id).first()
                if team:
                    logger.debug(f"别名匹配成功: {api_team_name} -> {team.team_full_name} (来源:{alias.source_type})")
                    return team
            
            # 3. 模糊匹配别名（包含关系）
            if len(api_team_name) >= 2:
                aliases = localdb.query(TeamAlias).filter(
                    TeamAlias.alias_name.like(f'%{api_team_name}%')
                ).all()
                
                for alias in aliases:
                    team = localdb.query(Team).filter_by(id=alias.team_id).first()
                    if team:
                        logger.debug(f"模糊别名匹配: {api_team_name} ~ {alias.alias_name} -> {team.team_full_name}")
                        return team
            
            return None
        except Exception as e:
            logger.error(f"_find_team_by_alias 出错: {e}")
            try:
                localdb.rollback()
            except:
                pass
            return None
    
    def _normalize_team_name(self, team_name: str) -> str:
        """
        标准化队名，去除常见后缀和特殊字符，提高匹配率
        
        Args:
            team_name: 原始队名
            
        Returns:
            str: 标准化后的队名
        """
        if not team_name:
            return ''
        
        normalized = team_name.strip()
        
        # 只有当队名长度>4时才尝试去除后缀，避免“曼联”变成“曼”
        if len(normalized) > 4:
            # 去除常见后缀
            suffixes = [
                '足球俱乐部', '足球俱乐部', '俱乐部',
                '竞技', '联盟', '体育',
                'United', 'City', 'FC', 'CF', 'AC', 'SC'
            ]
            
            for suffix in suffixes:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)].strip()
                    break
            
            # 单独处理“联”、“队”等单字后缀（只在去除其他后缀后且长度仍>3时）
            if len(normalized) > 3 and (normalized.endswith('联') or normalized.endswith('队')):
                # 检查是否是常见球队简称的一部分
                common_short_names = ['曼联', '国联', '西联', '北联']  # 这些不应该去掉“联”
                if normalized not in common_short_names:
                    normalized = normalized[:-1].strip()
        
        return normalized
    
    def _is_team_name_similar(self, name1: str, name2: str) -> bool:
        """
        判断两个队名是否相似（支持模糊匹配）
        
        Args:
            name1: 队名1
            name2: 队名2
            
        Returns:
            bool: 是否相似
        """
        if not name1 or not name2:
            return False
        
        # 完全匹配
        if name1 == name2:
            return True
        
        # 标准化后匹配
        norm1 = self._normalize_team_name(name1)
        norm2 = self._normalize_team_name(name2)
        
        if norm1 == norm2:
            return True
        
        # 包含关系匹配（短名称至少2个字符）
        if len(norm1) >= 2 and len(norm2) >= 2:
            if norm1 in norm2 or norm2 in norm1:
                return True
        
        # 常见球队名称映射表（全称 -> 简称/变体）
        common_team_mappings = {
            '曼彻斯特联': ['曼联', '曼聯'],
            '曼彻斯特城': ['曼城'],
            '皇家马德里': ['皇马', '皇馬'],
            '巴塞罗那': ['巴萨', '巴薩'],
            '拜仁慕尼黑': ['拜仁'],
            '巴黎圣日耳曼': ['巴黎', 'PSG', '巴黎圣日尔曼'],  # 耳/尔差异
            '尤文图斯': ['尤文', '祖雲達斯'],
            '国际米兰': ['国米', '國米', '國際米蘭'],
            'AC米兰': ['米兰', '米蘭'],
            '利物浦': ['利物鳥'],
            '切尔西': ['車路士'],
            '阿森纳': ['阿仙奴'],
            '托特纳姆热刺': ['热刺', '熱刺'],
            '多特蒙德': ['多特'],
            '马德里竞技': ['马竞', '馬競'],
            '那不勒斯': ['拿玻里'],
            # 一字之差的变体
            '朴茨茅斯': ['朴次茅斯'],  # 茨/次
            '南安普顿': ['南安普敦'],  # 顿/敦
            '里斯本竞技': ['葡萄牙体育'],
            '利勒斯特伦': ['利勒斯特罗姆'],  # 伦/罗姆
            '吉波': ['吉普'],  # 波/普
        }
        
        # 检查是否在映射表中
        for full_name, short_names in common_team_mappings.items():
            # name1 是全称，name2 是简称
            if (name1 == full_name or norm1 == full_name) and name2 in short_names:
                return True
            # name2 是全称，name1 是简称
            if (name2 == full_name or norm2 == full_name) and name1 in short_names:
                return True
        
        # 编辑距离匹配：如果长度相同且只有一个字符不同，认为是相似的
        if len(norm1) == len(norm2) and len(norm1) >= 2:
            diff_count = sum(1 for c1, c2 in zip(norm1, norm2) if c1 != c2)
            if diff_count == 1:
                logger.debug(f"编辑距离匹配: {norm1} ≈ {norm2} (差异字符数: {diff_count})")
                return True
        
        return False
    
    def _match_game_by_name_and_time(self, result_data: Dict) -> BjdcMatch:
        """
        通过队名和开赛时间匹配数据库中的比赛
        
        Args:
            result_data: API 返回的赛果数据
            
        Returns:
            BjdcMatch: 匹配到的比赛记录，未找到返回 None
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
        
        # 查询数据库中该日期的所有未结束比赛
        from sqlalchemy import func
        matches = localdb.query(BjdcMatch).filter(
            func.date(BjdcMatch.match_time) == match_date,
            BjdcMatch.status == 0  # 只查询未结束的比赛
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
    
    def save_results_to_db(self, results: List[Dict], pending_matches: List[BjdcMatch] = None) -> int:
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
        unmatched_count = 0  # 无法匹配的 BJDC 比赛数
        
        # 如果没有传入 pending_matches，则使用原来的逻辑（向后兼容）
        if pending_matches is None:
            logger.warning("未传入待匹配比赛列表，使用旧逻辑")
            return self._save_results_old_logic(results)
        
        # 关键修复：在遍历前先检查并回滚无效事务
        try:
            if localdb.session and not localdb.session.is_active:
                logger.warning("检测到无效事务，执行回滚 (save_results_to_db)")
                localdb.rollback()
        except Exception:
            pass
        
        # ========== 第一步：构建待匹配比赛的字典索引 ==========
        # key = match_id, value = {home_name, away_name, date, home_team_id, away_team_id, match_obj}
        pending_matches_dict = {}
        
        for match in pending_matches:
            try:
                home_name = match.home_team.team_full_name if match.home_team else ''
                away_name = match.away_team.team_full_name if match.away_team else ''
                match_date_str = match.match_time.strftime('%Y-%m-%d') if match.match_time else ''
                
                if not all([home_name, away_name, match_date_str]):
                    logger.debug(f"比赛信息不完整，跳过: match_id={match.match_id}")
                    continue
                
                pending_matches_dict[match.match_id] = {
                    'home_name': home_name,
                    'away_name': away_name,
                    'match_date': match_date_str,
                    'home_team_id': match.home_team_id,
                    'away_team_id': match.away_team_id,
                    'match_obj': match
                }
            except Exception as e:
                logger.error(f"处理比赛信息失败 (match_id={match.match_id}): {e}")
                continue
        
        logger.info(f"待匹配比赛: {len(pending_matches_dict)} 场")
        
        # ========== 第二步：遍历爬取的赛果，尝试匹配 ==========
        matched_match_ids = set()  # 记录已匹配的 match_id
        
        for result_data in results:
            try:
                # 爬虫返回的字段名
                api_home = result_data.get('homeTeam', '')
                api_away = result_data.get('awayTeam', '')
                api_date = result_data.get('matchDate', '')
                
                if not all([api_home, api_away, api_date]):
                    continue
                
                # 尝试匹配到待比赛列表中的某一场
                matched_match_id = None
                
                for match_id, match_info in pending_matches_dict.items():
                    # 如果已经匹配过，跳过
                    if match_id in matched_match_ids:
                        continue
                    
                    db_home = match_info['home_name']
                    db_away = match_info['away_name']
                    db_date = match_info['match_date']
                    
                    # 日期必须一致
                    if api_date != db_date:
                        continue
                    
                    # 1. 精确匹配
                    if api_home == db_home and api_away == db_away:
                        matched_match_id = match_id
                        logger.debug(f"精确匹配: {db_home} vs {db_away}")
                        break
                    
                    # 2. 主客场互换
                    if api_home == db_away and api_away == db_home:
                        matched_match_id = match_id
                        logger.info(f"🔄 主客场互换: {db_home} vs {db_away}")
                        break
                    
                    # 3. 模糊匹配（队名相似）
                    if (self._is_team_name_similar(api_home, db_home) and 
                        self._is_team_name_similar(api_away, db_away)):
                        matched_match_id = match_id
                        logger.info(f"🔍 模糊匹配: {api_home}≈{db_home}, {api_away}≈{db_away}")
                        break
                    
                    # 4. 反向模糊匹配
                    if (self._is_team_name_similar(api_home, db_away) and 
                        self._is_team_name_similar(api_away, db_home)):
                        matched_match_id = match_id
                        logger.info(f"🔍 模糊匹配(反向): {api_home}≈{db_away}, {api_away}≈{db_home}")
                        break
                
                if not matched_match_id:
                    # API 赛果无法匹配到任何 BJDC 比赛
                    continue
                
                # 标记为已匹配
                matched_match_ids.add(matched_match_id)
                matched_count += 1
                
                # ========== 第三步：保存赛果 ==========
                match_info = pending_matches_dict[matched_match_id]
                match = match_info['match_obj']
                
                # 检查比赛状态（网页爬取的 status 字段）
                result_status = result_data.get('status', '')  # '完' 表示结束
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = False
                abnormal_reason = ''
                
                # 检查比分是否为异常值
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 网页爬取的比分已经是整数或 None，不需要处理 'N/A'、'取消' 等字符串
                if home_score is None or away_score is None:
                    is_abnormal = True
                    abnormal_reason = '比分缺失'
                elif result_status in ['取消', '延期', '腰斩', '中断']:
                    is_abnormal = True
                    abnormal_reason = f'比赛{result_status}'
                
                # 构建数据库字段数据（直接使用爬虫解析后的数据）
                db_result_data = {
                    'match_id': matched_match_id,
                    'home_team_goals': home_score,
                    'away_team_goals': away_score,
                    'half_time_home_goals': result_data.get('halfHomeScore'),
                    'half_time_away_goals': result_data.get('halfAwayScore'),
                }
                
                # 过滤掉 None 值的字段（只添加有值的字段）
                db_result_data = {k: v for k, v in db_result_data.items() if v is not None}
                
                if is_abnormal:
                    # 异常比赛：标记状态为2，但仍保存赛果记录
                    match.status = 2
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {match_info['home_name']} vs {match_info['away_name']}, match_id={matched_match_id}")
                else:
                    # 正常比赛：标记状态为1
                    match.status = 1
                    localdb.update(match, close=False)
                
                # 保存或更新赛果记录
                existing_result = localdb.query(BjdcMatchResult).filter_by(match_id=matched_match_id).first()
                
                if existing_result:
                    # 更新现有记录
                    for key, value in db_result_data.items():
                        setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                    logger.debug(f"更新赛果：match_id={matched_match_id}")
                else:
                    # 创建新记录
                    if db_result_data:
                        new_result = BjdcMatchResult(**db_result_data)
                        localdb.add(new_result, close=False)
                        logger.debug(f"新增赛果：match_id={matched_match_id}")
                
                logger.info(f"✅ 保存赛果成功: {match_info['home_name']} vs {match_info['away_name']}, 比分: {home_score}-{away_score}")
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        # 统计未匹配的比赛
        unmatched_count = len(pending_matches_dict) - len(matched_match_ids)
        
        logger.info(f"赛果统计 - 待匹配: {len(pending_matches_dict)}, API返回: {len(results)}, 匹配成功: {matched_count}, 未匹配: {unmatched_count}, 保存: {saved_count}")
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
                
                # 检查比赛状态（网页爬取的 status 字段）
                result_status = result_data.get('status', '')  # '完' 表示结束
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = False
                abnormal_reason = ''
                
                # 检查比分是否为异常值
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 网页爬取的比分已经是整数或 None，不需要处理 'N/A'、'取消' 等字符串
                if home_score is None or away_score is None:
                    is_abnormal = True
                    abnormal_reason = '比分缺失'
                elif result_status in ['取消', '延期', '腰斩', '中断']:
                    is_abnormal = True
                    abnormal_reason = f'比赛{result_status}'
                
                # 构建数据库字段数据（直接使用爬虫解析后的数据）
                db_result_data = {
                    'match_id': match_id,
                    'home_team_goals': home_score,
                    'away_team_goals': away_score,
                    'half_time_home_goals': result_data.get('halfHomeScore'),
                    'half_time_away_goals': result_data.get('halfAwayScore'),
                }
                
                # 过滤掉 None 值的字段（只添加有值的字段）
                db_result_data = {k: v for k, v in db_result_data.items() if v is not None}
                
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
                existing_result = localdb.query(BjdcMatchResult).filter_by(match_id=match_id).first()
                
                if existing_result:
                    # 更新现有记录
                    for key, value in db_result_data.items():
                        setattr(existing_result, key, value)
                    localdb.update(existing_result, close=False)
                    logger.debug(f"更新赛果：match_id={match_id}")
                else:
                    # 创建新记录
                    if db_result_data:
                        new_result = BjdcMatchResult(**db_result_data)
                        localdb.add(new_result, close=False)
                        logger.debug(f"新增赛果：match_id={match_id}")
                
                logger.info(f"✅ 保存赛果成功: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, 比分: {home_score}-{away_score}")
                
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
            logger.info('开始获取并保存北京单场比赛结果...')
            
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
            
            logger.info(f'成功保存 {saved_count} 条赛果记录')
            return saved_count > 0
            
        except Exception as e:
            logger.error(f'获取并保存赛果异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return False
