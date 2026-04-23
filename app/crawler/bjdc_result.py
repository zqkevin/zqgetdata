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
                    
                    # 提取全场比分（从td[5]的div.pk中的三个a标签）
                    pk_td = match_row.find_all('td')[5] if len(match_row.find_all('td')) > 5 else None
                    home_score = None
                    away_score = None
                    
                    if pk_td:
                        pk_div = pk_td.find('div', class_='pk')
                        if pk_div:
                            anchors = pk_div.find_all('a')
                            if len(anchors) >= 3:
                                try:
                                    home_score = int(anchors[0].get_text(strip=True))
                                    away_score = int(anchors[2].get_text(strip=True))
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
            # logger.info('开始获取北京单场比赛结果...')  # 减少日志输出，由调用方统一记录
            
            # 1. 查询数据库中需要获取赛果的比赛
            from sqlalchemy import func
            
            cutoff_time = self.nowtime - timedelta(hours=4)
            abnormal_cutoff_time = self.nowtime - timedelta(days=4)
            
            pending_matches = localdb.query(BjdcMatch).filter(
                BjdcMatch.status == 0,  # 只查询待开赛的比賽 (status=0)
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
            # 注意：500.com 完场页面以每天上午10点为界
            # 例如：网页 2026-04-21 显示的比赛时间范围：04-21 12:00 到 04-22 09:10（次日10点前）
            #      网页 2026-04-22 显示的比赛时间范围：04-22 12:00 到 04-23 09:10
            # 规则：比赛时间 < 10:00 → 前一天的网页；比赛时间 >= 10:00 → 当天的网页
            match_dates = set()
            for m in valid_matches:
                if m.match_time:
                    # 如果比赛时间在10点之前，页面日期需要-1天
                    if m.match_time.hour < 10:
                        page_date = (m.match_time.date() - timedelta(days=1))
                    else:
                        page_date = m.match_time.date()
                    match_dates.add(page_date)
            
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
        from app.database import TeamAlias
        
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
                    self._add_team_alias_if_not_exists(db_home_team.id, home_team_name, 'bjdc_web')
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
    
    def _add_team_alias_if_not_exists(self, team_id: int, alias_name: str, source_type: str = 'bjdc'):
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
                # 注意：500.com 完场页面以每天10点为界
                # 规则：比赛时间 < 10:00 → 前一天的网页；比赛时间 >= 10:00 → 当天的网页
                if match.match_time:
                    if match.match_time.hour < 10:
                        page_date = (match.match_time.date() - timedelta(days=1)).strftime('%Y-%m-%d')
                    else:
                        page_date = match.match_time.date().strftime('%Y-%m-%d')
                else:
                    page_date = ''
                
                if not all([home_name, away_name, page_date]):
                    logger.debug(f"比赛信息不完整，跳过: match_id={match.match_id}")
                    continue
                
                pending_matches_dict[match.match_id] = {
                    'home_name': home_name,
                    'away_name': away_name,
                    'match_date': page_date,  # 使用页面日期而非比赛日期
                    'home_team_id': match.home_team_id,
                    'away_team_id': match.away_team_id,
                    'match_obj': match
                }
            except Exception as e:
                logger.error(f"处理比赛信息失败 (match_id={match.match_id}): {e}")
                continue
        
        logger.info(f"待匹配比赛: {len(pending_matches_dict)} 场")
        
        # ========== 第二步：直接使用 Match ID 匹配 ==========
        matched_match_ids = set()  # 记录已匹配的 match_id
        
        for result_data in results:
            try:
                # 从爬虫数据中获取 Match ID
                web_match_id = result_data.get('matchId')
                if not web_match_id:
                    continue
                
                # 转换为整数（网页中的matchId是字符串）
                try:
                    web_match_id_int = int(web_match_id)
                except ValueError:
                    continue
                
                # 直接通过 Match ID 查找待匹配比赛
                if web_match_id_int not in pending_matches_dict:
                    continue
                
                # 如果已经匹配过，跳过
                if web_match_id_int in matched_match_ids:
                    continue
                
                matched_match_id = web_match_id_int
                matched_count += 1
                matched_match_ids.add(matched_match_id)
                
                # ========== 第三步：保存赛果 ==========
                match_info = pending_matches_dict[matched_match_id]
                match = match_info['match_obj']
                
                # 检查比分是否为None（比分缺失）
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 如果比分缺失，跳过不保存，保持 status=0，等下次再尝试获取
                if home_score is None or away_score is None:
                    logger.debug(f"⊘ 比分缺失，跳过: {match_info['home_name']} vs {match_info['away_name']}, match_id={matched_match_id}")
                    # 从已匹配列表中移除，保持 status=0
                    matched_match_ids.remove(matched_match_id)
                    matched_count -= 1
                    continue
                
                # 检查比赛状态（网页爬取的 status 字段）
                result_status = result_data.get('status', '')  # '完' 表示结束
                
                # 使用统一的状态映射函数转换为内部状态码
                from app.common.match_status import map_to_internal_status, get_status_desc
                internal_status = map_to_internal_status('bjdc', result_status)
                
                # 判断是否为异常状态
                is_abnormal = internal_status in [3, 4, 5]  # 延期/取消/腰斩/中断
                abnormal_reason = ''
                
                if is_abnormal:
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
                
                # 更新比赛状态为映射后的内部状态码
                match.status = internal_status
                localdb.update(match, close=False)
                
                if is_abnormal:
                    logger.warning(f"⚠️ {abnormal_reason} ({get_status_desc(internal_status)}): {match_info['home_name']} vs {match_info['away_name']}, match_id={matched_match_id}")
                
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
                
                logger.debug(f"✅ 保存赛果成功: {match_info['home_name']} vs {match_info['away_name']}, 比分: {home_score}-{away_score}")  # 改为DEBUG级别
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存赛果失败: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        # 统计未匹配的比赛
        unmatched_count = len(pending_matches_dict) - len(matched_match_ids)
        
        # 只输出匹配成功的统计
        if matched_count > 0:
            logger.info(f"赛果统计 - 待匹配: {len(pending_matches_dict)}, 网页爬取: {len(results)}, 匹配成功: {matched_count}, 保存: {saved_count}")
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
                
                # 检查比分是否为None（比分缺失）
                home_score = result_data.get('homeScore')
                away_score = result_data.get('awayScore')
                
                # 如果比分缺失，跳过不保存，保持 status=0，等下次再尝试获取
                if home_score is None or away_score is None:
                    logger.debug(f"⊘ 比分缺失，跳过: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, match_id={match_id}")
                    matched_count -= 1
                    unmatched_count += 1
                    continue
                
                # 检查比赛状态（网页爬取的 status 字段）
                result_status = result_data.get('status', '')  # '完' 表示结束
                
                # 使用 BJDC 网页状态映射转换为内部状态码
                from app.common.match_status import BJDC_WEB_STATUS_MAP
                internal_status = BJDC_WEB_STATUS_MAP.get(result_status, 2)  # 默认已完成
                
                # 判断是否为异常状态（延期、腰斩、取消等）
                is_abnormal = internal_status in [3, 4, 5]  # 延期/取消/腰斩/中断
                abnormal_reason = ''
                
                if is_abnormal:
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
                    # 异常比赛：使用映射后的状态码（3=延期/取消, 4=腰斩, 5=中断）
                    match.status = internal_status
                    localdb.update(match, close=False)
                    logger.warning(f"⚠️ {abnormal_reason}: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, match_id={match_id}")
                else:
                    # 正常比赛：标记状态为2（已完成，已获取赛果）
                    match.status = 2
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
                
                logger.debug(f"✅ 保存赛果成功: {result_data.get('homeTeam')} vs {result_data.get('awayTeam')}, 比分: {home_score}-{away_score}")  # 改为DEBUG级别
                
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
        # logger.info('开始获取并保存北京单场比赛结果...')  # 减少日志输出，由调用方统一记录
        try:
            
            # 获取比赛结果和待匹配列表
            results, pending_matches = self.fetch_match_results()
            
            if not pending_matches:
                logger.warning('没有需要获取赛果的比赛')
                return False
            
            if not results:
                logger.warning('网页未爬取到赛果数据')
                return False
            
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
