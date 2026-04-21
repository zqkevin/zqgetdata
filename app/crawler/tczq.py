# -*- coding: utf-8 -*-
"""
体彩足球数据采集器
实现获取当前赛事信息、处理联赛信息和采集比赛数据的功能
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.common.req_sporttery_api import SportteryAPI
from app.log import tczq_log as logger
from app.common._utils import handle_league_name, handle_team_name, get_or_create_league, get_or_create_team
from app.database import (
    localdb,
    League, Team, MatchTypeEnum,
    TczqMatch,
    TczqSpfOdds,
    TczqHandicapSpfOdds,
    TczqScoreOdds,
    TczqTotalGoalOdds,
    TczqHalfTimeFullTimeOdds
)


class TczqDataCollector:
    """
    体彩足球数据采集器
    """
    
    def __init__(self):
        """
        初始化数据采集器实例
        """
        self.api = SportteryAPI()
    
    def _process_league_info(self, league_list: List[Dict[str, str]]) -> None:
        """
        处理联赛信息，若不存在则新增到数据库
            
        Args:
            league_list: 联赛信息列表，每个元素包含 leagueId, leagueName, leagueNameAbbr
        """
        from app.common._utils import get_or_create_league
        
        logger.info(f'开始处理 {len(league_list)} 个联赛信息')
        processed_leagues = set()  # 缓存已处理的联赛名称，避免重复处理
        failed_count = 0
        
        for league_info in league_list:
            logger.debug(f"联赛信息：{json.dumps(league_info, ensure_ascii=False)}")
            
            league_name = league_info.get('leagueName', '')
            league_name_abbr = league_info.get('leagueNameAbbr', '')
                
            if not league_name:
                logger.warning("联赛名称为空，跳过")
                continue
                
            # 如果联赛已经处理过，跳过
            if league_name in processed_leagues:
                continue
                    
            try:
                # 使用统一的 get_or_create_league 函数
                league_db_id = get_or_create_league(league_name, league_name_abbr)
                if league_db_id:
                    logger.debug(f"联赛处理成功：{league_name} (DB ID: {league_db_id})")
                    processed_leagues.add(league_name)
                else:
                    logger.error(f"处理联赛失败：{league_name}")
                    failed_count += 1
            except Exception as e:
                logger.error(f"处理联赛失败 (league_name={league_name}): {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                failed_count += 1
        
        if failed_count > 0:
            logger.warning(f'联赛信息处理完成，成功 {len(processed_leagues)} 个，失败 {failed_count} 个')
        else:
            logger.info(f'联赛信息处理完成，共处理 {len(processed_leagues)} 个联赛')
    
    def _find_match_by_league_and_time(self, league_id: int, match_date: str, match_time: str,
                                       home_team_name: str, away_team_name: str, 
                                       league_full_name: str = None, source_type: str = 'tczq'):
        """
        通过比赛时间查找BJDC中已存在的比赛，并将当前队名作为别名添加
        
        Args:
            league_id: TCZQ联赛ID（未使用）
            match_date: 比赛日期 (YYYY-MM-DD)
            match_time: 比赛时间 (HH:MM:SS)
            home_team_name: 主队名称
            away_team_name: 客队名称
            league_full_name: TCZQ联赛全称（用于补充BJDC联赛记录）
            source_type: 数据来源类型
            
        Returns:
            BjdcMatch对象如果找到，否则返回None
        """
        from app.database import Team, TeamAlias, BjdcMatch, League
        from datetime import datetime, timedelta
        
        try:
            # 1. 通过比赛时间查找BJDC中的比赛（允许±30分钟误差）
            match_datetime_str = f"{match_date} {match_time}"
            try:
                match_datetime = datetime.strptime(match_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                logger.warning(f"时间格式错误：{match_datetime_str}")
                return None
            
            # 查找同一天的BJDC比赛
            from sqlalchemy import and_
            existing_matches = localdb.query(BjdcMatch).filter(
                and_(
                    BjdcMatch.match_time >= datetime.strptime(match_date, "%Y-%m-%d"),
                    BjdcMatch.match_time < datetime.strptime(match_date, "%Y-%m-%d") + timedelta(days=1)
                )
            ).all()
            
            for existing_match in existing_matches:
                # 检查时间是否接近（±30分钟）
                if existing_match.match_time:
                    try:
                        time_diff = abs((match_datetime - existing_match.match_time).total_seconds())
                        
                        if time_diff <= 1800:  # 30分钟 = 1800秒
                            # 检查队名是否相似（前4个字符）
                            bjdc_home = localdb.query(Team).filter_by(id=existing_match.home_team_id).first()
                            bjdc_away = localdb.query(Team).filter_by(id=existing_match.away_team_id).first()
                            
                            if not bjdc_home or not bjdc_away:
                                continue
                            
                            # 模糊匹配队名（前4个字符）
                            home_match = (
                                home_team_name[:4] in bjdc_home.team_full_name or
                                bjdc_home.team_full_name[:4] in home_team_name
                            )
                            away_match = (
                                away_team_name[:4] in bjdc_away.team_full_name or
                                bjdc_away.team_full_name[:4] in away_team_name
                            )
                            
                            if home_match and away_match:
                                logger.info(f"✓ 匹配到BJDC比赛: {bjdc_home.team_full_name} vs {bjdc_away.team_full_name} (时间差:{time_diff/60:.0f}分钟)")
                                
                                # 补充联赛全称（如果TCZQ提供了全称且BJDC联赛还没有全称）
                                if league_full_name:
                                    bjdc_league = localdb.query(League).filter_by(id=existing_match.league_id).first()
                                    if bjdc_league and not bjdc_league.league_name:
                                        bjdc_league.league_name = league_full_name
                                        localdb.update(bjdc_league, close=False)
                                        logger.info(f"✓ 补充联赛全称: league_id={bjdc_league.id}, full_name={league_full_name}")
                                
                                # 将当前队名作为别名添加到已存在的球队
                                if bjdc_home.team_full_name != home_team_name:
                                    self._add_team_alias_if_not_exists(
                                        existing_match.home_team_id, home_team_name, source_type
                                    )
                                
                                if bjdc_away.team_full_name != away_team_name:
                                    self._add_team_alias_if_not_exists(
                                        existing_match.away_team_id, away_team_name, source_type
                                    )
                                
                                return existing_match
                    except Exception as e:
                        logger.debug(f"时间比较失败：{e}")
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"查找比赛失败：{e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _add_team_alias_if_not_exists(self, team_id: int, alias_name: str, source_type: str):
        """
        为球队添加别名（如果不存在）
        
        Args:
            team_id: 球队ID
            alias_name: 别名名称
            source_type: 数据来源类型
        """
        from app.database import TeamAlias
        
        try:
            # 检查是否已存在该别名
            existing_alias = localdb.query(TeamAlias).filter_by(
                team_id=team_id,
                source_type=source_type,
                alias_name=alias_name
            ).first()
            
            if not existing_alias:
                # 添加新别名
                new_alias = TeamAlias(
                    team_id=team_id,
                    alias_name=alias_name,
                    source_type=source_type,
                    is_primary=0,
                    remark=f"自动添加 - {source_type} 数据源（通过联赛+时间匹配）"
                )
                localdb.add(new_alias, close=False)
                logger.info(f"✓ 添加球队别名: team_id={team_id}, alias={alias_name}, source={source_type}")
            else:
                logger.debug(f"别名已存在：{alias_name} (team_id={team_id})")
                
        except Exception as e:
            logger.error(f"添加别名失败：{e}")
    
    def _process_match_info(self, match_list: List[Dict[str, str]], league_map: Dict[int, str] = None) -> List[Dict[str, str]]:
        """
        处理比赛信息，更新或新增比赛记录
        
        Args:
            match_list: 比赛信息列表
            league_map: 联赛 ID 到名称的映射字典 {league_id: league_name}
            
        Returns:
            处理后的比赛信息列表
        """
        matches = []
                
        for match_info in match_list:
            match_id = match_info.get('matchId', '')
            
            try:
                match_id = int(match_id) if match_id else 0
            except ValueError:
                logger.warning(f"match_id 格式错误：{match_id}")
                continue
                
            match_num_str = match_info.get('matchNum', '')
            # 确保 match_num_str 是字符串类型
            match_num_str = str(match_num_str)
            # 从 match_num_str 中提取数字部分作为 match_num
            match_num = int(''.join(filter(str.isdigit, match_num_str))) if match_num_str else 0
            match_num_date = match_info.get('matchNumDate', '')
            match_week = match_info.get('matchWeek', '')
            match_date_str = match_info.get('matchDate', '')
            match_time = match_info.get('matchTime', '')
            business_date = match_info.get('businessDate', '')
            tax_date_no = match_info.get('taxDateNo', '')
            
            league_id = int(match_info.get('leagueId', '0'))
            
            # 解析球队信息
            home_team_full_name = match_info.get('homeTeamAllName', '')
            home_team_short_name = match_info.get('homeTeamAbbName', '')
            home_team_code = match_info.get('homeTeamCode', '')
            home_team_abb_en_name = match_info.get('homeTeamAbbEnName', '')
            home_rank = match_info.get('homeRank', '')
            
            away_team_full_name = match_info.get('awayTeamAllName', '')
            away_team_short_name = match_info.get('awayTeamAbbName', '')
            away_team_code = match_info.get('awayTeamCode', '')
            away_team_abb_en_name = match_info.get('awayTeamAbbEnName', '')
            away_rank = match_info.get('awayRank', '')
            
            # 解析比赛其他信息
            base_home_team_id = int(match_info.get('baseHomeTeamId', '0'))
            base_away_team_id = int(match_info.get('baseAwayTeamId', '0'))
            match_name = match_info.get('matchName', '')
            group_name = match_info.get('groupName', '')
            line_num = match_info.get('lineNum', '')
            
            # 解析投注信息
            betting_single = int(match_info.get('bettingSingle', '0'))
            betting_all_up = int(match_info.get('bettingAllUp', '0'))
            
            if not all([match_id, league_id, home_team_full_name, away_team_full_name, match_date_str]):
                logger.warning(f"比赛信息不完整，跳过：match_id={match_id}, league_id={league_id}")
                continue
            
            # 处理比赛时间
            try:
                match_date = datetime.strptime(match_date_str, "%Y-%m-%d")
                match_datetime = datetime.strptime(f"{match_date_str} {match_time}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                logger.warning(f"比赛时间格式错误，跳过：{match_date_str} {match_time}")
                continue
            
            # 先处理联赛信息 - 根据名称查询或创建，获取数据库主键 ID
            try:
                # 优先从 league_map 中获取联赛名称和简称
                api_league_id = int(match_info.get('leagueId', '0'))
                if league_map and api_league_id in league_map:
                    league_name_from_api, league_abbr_from_api = league_map[api_league_id]
                else:
                    # 如果 map 中没有，尝试从比赛信息中获取
                    league_name_from_api = match_info.get('leagueName', '')
                    league_abbr_from_api = match_info.get('leagueNameAbbr', '')
                
                if not league_name_from_api:
                    logger.warning(f"比赛缺少联赛名称，跳过 (match_id={match_id})")
                    continue
                    
                # 使用封装函数获取或创建联赛，返回数据库主键 ID
                league_db_id = get_or_create_league(league_name_from_api, league_abbr_from_api)
                if not league_db_id:
                    logger.error(f"处理联赛失败，跳过比赛 (match_id={match_id}, league={league_name_from_api})")
                    continue
                    
                logger.debug(f"联赛处理结果：{league_name_from_api} -> DB ID: {league_db_id}")
            except Exception as e:
                logger.error(f"处理联赛信息失败 (match_id={match_id}): {str(e)}")
                import traceback
                traceback.print_exc()
                continue
            
            # 处理球队信息
            try:
                # 关键优化：先尝试通过联赛+比赛时间匹配BJDC中已存在的比赛
                # 从 league_map 中获取TCZQ的联赛全称
                tczq_league_full_name = None
                if league_map and api_league_id in league_map:
                    tczq_league_full_name, _ = league_map[api_league_id]
                
                matched_match = self._find_match_by_league_and_time(
                    league_db_id, match_date_str, match_time,
                    home_team_full_name, away_team_full_name, 
                    league_full_name=tczq_league_full_name, source_type='tczq'
                )
                
                if matched_match:
                    logger.info(f"✓ 通过联赛+时间匹配到BJDC比赛: match_id={matched_match.match_id}")
                    # 使用BJDC比赛的球队ID，并将TCZQ队名添加为别名
                    home_team_id = matched_match.home_team_id
                    away_team_id = matched_match.away_team_id
                    
                    # 将TCZQ的队名添加为别名（如果不同）
                    from app.database import Team
                    bjdc_home_team = localdb.query(Team).filter_by(id=home_team_id).first()
                    bjdc_away_team = localdb.query(Team).filter_by(id=away_team_id).first()
                    
                    if bjdc_home_team and bjdc_home_team.team_full_name != home_team_full_name:
                        self._add_team_alias_if_not_exists(home_team_id, home_team_full_name, 'tczq')
                    
                    if bjdc_away_team and bjdc_away_team.team_full_name != away_team_full_name:
                        self._add_team_alias_if_not_exists(away_team_id, away_team_full_name, 'tczq')
                else:
                    # 没有匹配到BJDC比赛，正常创建/查找球队
                    home_team_id = get_or_create_team(home_team_full_name, home_team_short_name, home_team_code, source_type='tczq')
                    away_team_id = get_or_create_team(away_team_full_name, away_team_short_name, away_team_code, source_type='tczq')
                    
                    if not home_team_id or not away_team_id:
                        logger.error(f"处理球队信息失败，跳过比赛 (match_id={match_id})")
                        continue
                
                logger.debug(f"处理球队结果：home_team_id={home_team_id}, away_team_id={away_team_id}")
            except Exception as e:
                logger.error(f"处理球队信息失败：{str(e)}")
                import traceback
                traceback.print_exc()
                continue
            
            # 处理期数：对于 tczq，使用比赛的年 - 月 - 日作为期数
            period = match_date_str  # 格式："2024-08-10"
                        
            # 查询数据库中是否已存在该比赛
            try:
                existing_match = localdb.query(TczqMatch).filter_by(match_id=match_id).first()
                            
                if not home_team_id or not away_team_id:
                    logger.error(f"处理球队信息失败，跳过比赛")
                    continue
                
                match_info_dict = {
                    'match_id': match_id,
                    'match_num_str': match_num_str,
                    'match_num_date': match_num_date,
                    'match_week': match_week,
                    'match_date': match_date_str,
                    'match_time': match_time,
                    'business_date': business_date,
                    'tax_date_no': tax_date_no,
                    'league_id': league_db_id,  # 使用数据库主键 ID
                    'home_team_id': home_team_id,  # 使用数据库主键 ID
                    'home_team_code': home_team_code,
                    'home_team_all_name': home_team_full_name,
                    'home_team_abb_name': home_team_short_name,
                    'home_team_abb_en_name': home_team_abb_en_name,
                    'home_rank': home_rank,
                    'away_team_id': away_team_id,  # 使用数据库主键 ID
                    'away_team_code': away_team_code,
                    'away_team_all_name': away_team_full_name,
                    'away_team_abb_name': away_team_short_name,
                    'away_team_abb_en_name': away_team_abb_en_name,
                    'away_rank': away_rank,
                    'base_home_team_id': base_home_team_id,
                    'base_away_team_id': base_away_team_id,
                    'match_name': match_name,
                    'group_name': group_name,
                    'line_num': line_num,
                    'betting_single': betting_single,
                    'betting_all_up': betting_all_up,
                    'period': period
                }
                
                matches.append(match_info_dict)
                
            except Exception as e:
                logger.error(f"处理比赛信息失败 (match_id={match_id}): {str(e)}")
                import traceback
                traceback.print_exc()
        
        return matches
    
    def collect_matches(self):
        """
        采集体彩足球比赛数据
            
        Returns:
            bool: 采集成功返回 True，否则返回 False
        """
        try:
            logger.info('开始采集体彩足球比赛数据...')
                
            # 获取比赛列表
            try:
                match_data = self.api.get_football_match_list()
                logger.info(f'成功获取比赛数据，类型: {type(match_data)}')
            except Exception as e:
                logger.error(f'获取足球比赛列表失败：{e}')
                return False
            
            # 处理API返回的字典结构
            if isinstance(match_data, dict):
                match_info_list = match_data.get('match_info_list', [])
                league_list_raw = match_data.get('league_list', [])
                
                # 提取所有子比赛（subMatchList）
                all_matches = []
                for date_group in match_info_list:
                    sub_matches = date_group.get('subMatchList', [])
                    all_matches.extend(sub_matches)
                
                logger.info(f'共获取 {len(all_matches)} 场比赛')
                
                if not all_matches:
                    logger.info('获取到的比赛列表为空')
                    return False
                
                # 处理联赛信息
                logger.info(f'开始处理 {len(league_list_raw)} 个联赛信息')
                self._process_league_info(league_list_raw)
                logger.info('联赛信息处理完成')
                
                # 构建联赛 ID 到名称和简称的映射
                league_map = {}
                for lg in league_list_raw:
                    try:
                        lg_id = int(lg.get('leagueId', 0))
                        lg_name = lg.get('leagueName', '')
                        lg_abbr = lg.get('leagueNameAbbr', '')
                        if lg_id and lg_name:
                            league_map[lg_id] = (lg_name, lg_abbr)  # 存储为元组
                    except (ValueError, TypeError):
                        continue
                logger.debug(f'构建联赛映射: {len(league_map)} 个')
                    
                # 处理比赛信息
                logger.info(f'开始处理 {len(all_matches)} 条比赛数据')
                matches = self._process_match_info(all_matches, league_map)
                
            if not matches:
                logger.warning('没有有效的比赛数据')
                return False
                
            # 批量保存到数据库
            saved_count = 0
            for match_data in matches:
                try:
                    existing_match = localdb.query(TczqMatch).filter_by(match_id=match_data['match_id']).first()
                        
                    if existing_match:
                        # 更新现有记录
                        for key, value in match_data.items():
                            if hasattr(existing_match, key):
                                setattr(existing_match, key, value)
                        localdb.update(existing_match, close=False)
                    else:
                        # 创建新记录
                        new_match = TczqMatch(**match_data)
                        localdb.add(new_match, close=False)
                        
                    saved_count += 1
                        
                except Exception as e:
                    logger.error(f"保存比赛数据失败 (match_id={match_data['match_id']}): {str(e)}")
                    continue
                
            logger.info(f'成功保存 {saved_count} 条比赛记录')
            return saved_count > 0
                
        except Exception as e:
            logger.error(f'采集比赛数据异常：traceback.format_exc()')
            return False
    
    def get_current_matches(self):
        """
        获取当前比赛数据（带赔率）
            
        Returns:
            list: 比赛数据列表
        """
        try:
            logger.info('开始获取当前比赛数据（带赔率）...')
                
            # 获取比赛列表
            match_data = self.api.get_football_match_list()
            
            # 处理API返回的字典结构
            if isinstance(match_data, dict):
                match_info_list = match_data.get('match_info_list', [])
                league_list_raw = match_data.get('league_list', [])
                
                # 提取所有子比赛（subMatchList）
                all_matches = []
                for date_group in match_info_list:
                    sub_matches = date_group.get('subMatchList', [])
                    all_matches.extend(sub_matches)
                
                logger.info(f'共获取 {len(all_matches)} 场比赛')
                    
                if not all_matches:
                    logger.info('获取到的比赛列表为空')
                    return []
                    
                # 处理联赛和比赛信息
                self._process_league_info(league_list_raw)
                localdb.commit()  # 提交联赛数据
                logger.info(f'联赛数据处理完成，共 {len(league_list_raw)} 个联赛')
                
                # 构建联赛 ID 到名称和简称的映射
                league_map = {}
                for lg in league_list_raw:
                    try:
                        lg_id = int(lg.get('leagueId', 0))
                        lg_name = lg.get('leagueName', '')
                        lg_abbr = lg.get('leagueNameAbbr', '')
                        if lg_id and lg_name:
                            league_map[lg_id] = (lg_name, lg_abbr)  # 存储为元组
                    except (ValueError, TypeError):
                        continue
                logger.debug(f'构建联赛映射: {len(league_map)} 个')
                
                matches = self._process_match_info(all_matches, league_map)
                    
                if not matches:
                    logger.warning('没有有效的比赛数据')
                    return []
                
                # 保存比赛信息到数据库
                saved_count = 0
                for match_data in matches:
                    try:
                        existing_match = localdb.query(TczqMatch).filter_by(match_id=match_data['match_id']).first()
                        
                        # 只提取数据库模型中存在的字段
                        db_fields = {
                            'match_id': match_data.get('match_id'),
                            'issue': match_data.get('period', ''),  # period -> issue
                            'match_num': int(''.join(filter(str.isdigit, str(match_data.get('match_num_str', '0'))))),
                            'match_num_str': match_data.get('match_num_str', ''),
                            'match_week': match_data.get('match_week', ''),
                            'match_time': f"{match_data.get('match_date', '')} {match_data.get('match_time', '')}",
                            'match_date': match_data.get('match_date', ''),
                            'league_id': match_data.get('league_id'),
                            'home_team_id': match_data.get('home_team_id'),
                            'away_team_id': match_data.get('away_team_id'),
                            'status': 0  # 默认未开始
                        }
                        
                        if existing_match:
                            # 更新现有记录
                            for key, value in db_fields.items():
                                if hasattr(existing_match, key):
                                    setattr(existing_match, key, value)
                            localdb.update(existing_match, close=False)
                        else:
                            # 创建新记录
                            new_match = TczqMatch(**db_fields)
                            localdb.add(new_match, close=False)
                        
                        saved_count += 1
                    except Exception as e:
                        logger.error(f"保存比赛数据失败 (match_id={match_data.get('match_id')}): {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                        continue
                
                logger.info(f'成功保存 {saved_count} 条比赛记录')
                localdb.commit()  # 提交事务
                    
                # 处理赔率数据（赔率已经在 all_matches 中）
                logger.info(f'开始处理 {len(all_matches)} 条赔率数据')
                self._process_odds_data(all_matches)
                logger.info('赔率数据处理完成')
                    
                return matches
            else:
                logger.error(f'未知的数据类型: {type(match_data)}')
                return []
                
        except Exception as e:
            logger.error(f'获取比赛数据异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _process_odds_data(self, odds_data):
        """
        处理赔率数据
        
        Args:
            odds_data: 赔率数据列表
        """
        try:
            for match_odds in odds_data:
                match_id = match_odds.get('matchId')
                if not match_id:
                    continue
                
                # 保存各种赔率数据到数据库
                self._save_odds_to_db(match_id, match_odds)
                
        except Exception as e:
            logger.error(f'处理赔率数据失败：{str(e)}')
    
    def _save_odds_to_db(self, match_id: int, odds_data: Dict):
        """
        保存赔率数据到数据库，并记录赔率变化
        
        Args:
            match_id: 比赛 ID
            odds_data: 赔率数据（包含 had, hhad, ttg, hafu, crs 等）
        """
        from app.database import TczqOddsChangeLog
        from datetime import datetime
        
        try:
            # 保存胜平负赔率 (had)
            if 'had' in odds_data and odds_data['had']:
                api_data = odds_data['had']
                # 字段映射：API -> 数据库
                db_data = {
                    'win_pl': float(api_data.get('h', 0)),
                    'draw_pl': float(api_data.get('d', 0)),
                    'lose_pl': float(api_data.get('a', 0))
                }
                
                existing = localdb.query(TczqSpfOdds).filter_by(match_id=match_id).first()
                if existing:
                    # 记录赔率变化
                    self._log_odds_change(
                        match_id, 'tczq_spf_odds', existing.id, db_data, existing,
                        ['win_pl', 'draw_pl', 'lose_pl']
                    )
                    # 更新现有记录
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                else:
                    # 新增记录
                    new_odds = TczqSpfOdds(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
            
            # 保存让球胜平负赔率 (hhad)
            if 'hhad' in odds_data and odds_data['hhad']:
                api_data = odds_data['hhad']
                db_data = {
                    'handicap': float(api_data.get('goalLineValue', 0)),
                    'win_pl': float(api_data.get('h', 0)),
                    'draw_pl': float(api_data.get('d', 0)),
                    'lose_pl': float(api_data.get('a', 0))
                }
                
                existing = localdb.query(TczqHandicapSpfOdds).filter_by(match_id=match_id).first()
                if existing:
                    self._log_odds_change(
                        match_id, 'tczq_handicap_spf_odds', existing.id, db_data, existing,
                        ['handicap', 'win_pl', 'draw_pl', 'lose_pl']
                    )
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                else:
                    new_odds = TczqHandicapSpfOdds(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
            
            # 保存总进球赔率 (ttg)
            if 'ttg' in odds_data and odds_data['ttg']:
                api_data = odds_data['ttg']
                db_data = {
                    'goal_0': float(api_data.get('s0', 0)),
                    'goal_1': float(api_data.get('s1', 0)),
                    'goal_2': float(api_data.get('s2', 0)),
                    'goal_3': float(api_data.get('s3', 0)),
                    'goal_4': float(api_data.get('s4', 0)),
                    'goal_5': float(api_data.get('s5', 0)),
                    'goal_6': float(api_data.get('s6', 0)),
                    'goal_about': float(api_data.get('s7', 0))
                }
                
                existing = localdb.query(TczqTotalGoalOdds).filter_by(match_id=match_id).first()
                if existing:
                    self._log_odds_change(
                        match_id, 'tczq_total_goal_odds', existing.id, db_data, existing,
                        ['goal_0', 'goal_1', 'goal_2', 'goal_3', 'goal_4', 'goal_5', 'goal_6', 'goal_about']
                    )
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                else:
                    new_odds = TczqTotalGoalOdds(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
            
            # 保存半全场赔率 (hafu)
            if 'hafu' in odds_data and odds_data['hafu']:
                api_data = odds_data['hafu']
                db_data = {
                    'half_win_full_win': float(api_data.get('hh', 0)),      # 半胜全胜
                    'half_win_full_draw': float(api_data.get('hd', 0)),     # 半胜全平
                    'half_win_full_lose': float(api_data.get('ha', 0)),     # 半胜全负
                    'half_draw_full_win': float(api_data.get('dh', 0)),     # 半平全胜
                    'half_draw_full_draw': float(api_data.get('dd', 0)),    # 半平全平
                    'half_draw_full_lose': float(api_data.get('da', 0)),    # 半平全负
                    'half_lose_full_win': float(api_data.get('ah', 0)),     # 半负全胜
                    'half_lose_full_draw': float(api_data.get('ad', 0)),    # 半负全平
                    'half_lose_full_lose': float(api_data.get('aa', 0))     # 半负全负
                }
                
                existing = localdb.query(TczqHalfTimeFullTimeOdds).filter_by(match_id=match_id).first()
                if existing:
                    self._log_odds_change(
                        match_id, 'tczq_ht_ft_odds', existing.id, db_data, existing,
                        ['half_win_full_win', 'half_win_full_draw', 'half_win_full_lose',
                         'half_draw_full_win', 'half_draw_full_draw', 'half_draw_full_lose',
                         'half_lose_full_win', 'half_lose_full_draw', 'half_lose_full_lose']
                    )
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                else:
                    new_odds = TczqHalfTimeFullTimeOdds(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
            
            # 保存比分赔率 (crs)
            if 'crs' in odds_data and odds_data['crs']:
                api_data = odds_data['crs']
                db_data = {}
                # 比分赔率字段映射 (API: s_x_y -> DB: score_x_y)
                for key, value in api_data.items():
                    if key.startswith('s_'):
                        db_key = key.replace('s_', 'score_')
                        db_data[db_key] = float(value)
                
                existing = localdb.query(TczqScoreOdds).filter_by(match_id=match_id).first()
                if existing:
                    self._log_odds_change(
                        match_id, 'tczq_score_odds', existing.id, db_data, existing,
                        list(db_data.keys())
                    )
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                else:
                    new_odds = TczqScoreOdds(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
                    
        except Exception as e:
            logger.error(f"保存赔率数据失败 (match_id={match_id}): {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _log_odds_change(self, match_id: int, odds_table: str, odds_record_id: int,
                         new_data: dict, existing_record, fields: list):
        """
        记录赔率变化日志（带阈值判断）
        
        Args:
            match_id: 比赛ID
            odds_table: 赔率表名
            odds_record_id: 赔率记录ID
            new_data: 新数据字典
            existing_record: 现有记录对象
            fields: 需要检查变化的字段列表
        """
        from app.database import TczqOddsChangeLog
        from datetime import datetime
        from app.common._utils import should_log_odds_change
        
        try:
            for field in fields:
                if field not in new_data:
                    continue
                
                new_value = new_data[field]
                
                # 使用通用函数判断是否应该记录
                should_log, current_value, diff = should_log_odds_change(
                    odds_record_id=odds_record_id,
                    field_name=field,
                    new_value=float(new_value),
                    odds_table=odds_table,
                    sport_type='tczq',  # 体彩足球
                    threshold=0.05  # 波动阈值 ±0.05
                )
                
                if should_log:
                    # 获取比赛信息用于日志输出
                    match_info = ""
                    try:
                        from app.database import TczqMatch
                        match = localdb.query(TczqMatch).filter_by(match_id=match_id).first()
                        if match:
                            home_name = match.home_team.team_full_name if match.home_team else '未知'
                            away_name = match.away_team.team_full_name if match.away_team else '未知'
                            match_num = match.match_num or ''
                            match_info = f"[{match_num} {home_name} vs {away_name}] "
                    except Exception:
                        pass
                    
                    change_log = TczqOddsChangeLog(
                        match_id=match_id,
                        odds_table=odds_table,
                        odds_record_id=odds_record_id,
                        odds_field=field,
                        old_value=float(current_value) if current_value != 0.0 else float(getattr(existing_record, field, 0)),
                        new_value=float(new_value),
                        change_time=datetime.now()
                    )
                    localdb.add(change_log, close=False)
                    logger.info(f"✓ {match_info}{field}赔率变化: {current_value:.3f} -> {new_value:.3f} (波动{diff:+.3f})")
                else:
                    logger.debug(f"⊘ 忽略小幅波动: {odds_table}.{field} "
                               f"{current_value:.3f} -> {new_value:.3f} (diff={diff:.3f})")
        except Exception as e:
            logger.error(f"记录赔率变化失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
