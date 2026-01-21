# -*- coding: utf-8 -*-
import sys
import os
import json
import traceback
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.req_sporttery_api import SportteryAPI
from app.common.logger import log as logger
from app.database import localdb
from app.database.tcbk_models import (
    TcbkLeague, TcbkMatch, TcbkSpf, TcbkRfsf, TcbkDxf, TcbkSfc, TcbkResult,
    TcbkOddsHistory, TcbkOddsHistorySpf, TcbkOddsHistoryRfsf, TcbkOddsHistoryDxf, TcbkOddsHistorySfc
)


class get_jcbk_data():
    def __init__(self):
        self.nowtime = datetime.now()
        self.api = SportteryAPI()
        self.logger = logger

    def get_gamedata(self):
        '''
        获取篮球比赛数据，更新到数据库
        包括：
        1. 篮球比赛数据
        2. 篮球胜负赔率
        3. 篮球让分胜负赔率
        4. 篮球大小分赔率
        5. 篮球胜分差赔率
        :return: None
        '''
        try:
            self.logger.info('开始获取篮球比赛数据...')
            
            # 获取篮球比赛列表
            match_list = self.api.get_basketball_match_list()
            self.logger.info(f'获取到篮球比赛列表，共有{len(match_list)}条记录')
            
            if match_list.empty:
                self.logger.info('更新当前篮球比赛数据失败！联网爬取失败')
                return
            
            # 获取篮球比赛计算器信息（包含赔率）
            calculator_data = self.api.get_basketball_match_calculator(['hilo', 'spf', 'rfsf', 'sfc'])
            self.logger.info('获取到篮球比赛计算器信息')
            
            # 处理比赛数据
            self.logger.info('开始处理比赛数据...')
            self._process_match_list(match_list)
            
            # 处理赔率数据
            if 'matchInfoList' in calculator_data:
                self.logger.info(f'开始处理赔率数据，共有{len(calculator_data["matchInfoList"])}条记录')
                self._process_calculator_data(calculator_data['matchInfoList'])
            else:
                self.logger.warning('计算器数据中没有matchInfoList字段')
            
            self.logger.info('篮球比赛数据更新完成')
            
        except Exception as e:
            self.logger.error(f'Error in get_gamedata:{traceback.format_exc()}, e:{e}')

    def _process_match_list(self, match_list):
        '''
        处理篮球比赛列表数据，更新到数据库
        :param match_list: 篮球比赛列表的DataFrame
        :return: None
        '''
        try:
            for index, match in match_list.iterrows():
                self.logger.info(f'Processing match {index}: {match}')
                # 获取或创建联赛记录
                league_id = match.get('leagueId')
                self.logger.info(f'leagueId type: {type(league_id)}, value: {league_id}')
                if not league_id:
                    continue
                    
                league = localdb.query(TcbkLeague, close=False).filter_by(league_id=league_id).first()
                if not league:
                    # 确保league_name不为None
                    league_name = match.get('leagueName')
                    if league_name is None:
                        league_name = f'未知联赛_{league_id}'
                        self.logger.warning(f'League name is None for league_id {league_id}, using default name: {league_name}')
                    
                    league = TcbkLeague(
                        league_id=league_id,
                        league_name=league_name,
                        league_name_abbr=match.get('leagueNameAbbr', '')
                    )
                    localdb.add(league, close=False)  # 添加联赛，不关闭会话
                
                # 获取或创建比赛记录
                match_id = match.get('matchId')
                self.logger.info(f'matchId type: {type(match_id)}, value: {match_id}')
                if not match_id:
                    continue
                    
                match_record = localdb.query(TcbkMatch, close=False).filter_by(match_id=match_id).first()
                if not match_record:
                    match_record = TcbkMatch()
                    match_record.match_id = match_id
                
                # 更新比赛信息
                match_record.match_num = match.get('matchNum')
                match_record.match_num_str = match.get('matchNumStr')
                match_record.match_num_date = match.get('matchNumDate')
                match_record.match_week = match.get('matchWeek')
                match_record.match_date = match.get('matchDate')
                
                # 处理match_time字段，确保它是字符串类型
                match_time = match.get('matchTime')
                if match_time is not None:
                    # 如果是Timestamp对象，转换为字符串
                    if hasattr(match_time, 'strftime'):
                        match_record.match_time = match_time.strftime('%Y-%m-%d %H:%M:%S')
                        self.logger.info(f'Converted match_time from Timestamp to string: {match_record.match_time}')
                    else:
                        match_record.match_time = str(match_time)
                
                match_record.business_date = match.get('businessDate', match.get('matchDate'))
                
                # 转换league_id为整数类型
                try:
                    match_record.league_id = int(league_id)
                    self.logger.info(f'Converted league_id to int: {match_record.league_id}')
                except (ValueError, TypeError) as e:
                    self.logger.error(f'Failed to convert league_id {league_id} to int: {e}')
                    continue
                
                # 处理主队信息 - 支持不同的字段名
                home_team_id = match.get('homeTeamId')
                try:
                    match_record.home_team_id = int(home_team_id) if home_team_id else None
                    self.logger.info(f'Converted home_team_id to int: {match_record.home_team_id}')
                except (ValueError, TypeError) as e:
                    self.logger.error(f'Failed to convert home_team_id {home_team_id} to int: {e}')
                    match_record.home_team_id = None
                
                match_record.home_team_code = match.get('homeTeamCode', '')
                match_record.home_team_all_name = match.get('homeTeamAllName', match.get('homeTeamName', ''))
                match_record.home_team_abb_name = match.get('homeTeamAbbrName', match.get('homeTeamName', ''))
                match_record.home_team_rank = match.get('homeTeamRank', '')
                
                # 处理客队信息 - 支持不同的字段名
                away_team_id = match.get('awayTeamId')
                try:
                    match_record.away_team_id = int(away_team_id) if away_team_id else None
                    self.logger.info(f'Converted away_team_id to int: {match_record.away_team_id}')
                except (ValueError, TypeError) as e:
                    self.logger.error(f'Failed to convert away_team_id {away_team_id} to int: {e}')
                    match_record.away_team_id = None
                
                match_record.away_team_code = match.get('awayTeamCode', '')
                match_record.away_team_all_name = match.get('awayTeamAllName', match.get('awayTeamName', ''))
                match_record.away_team_abb_name = match.get('awayTeamAbbrName', match.get('awayTeamName', ''))
                match_record.away_team_rank = match.get('awayTeamRank', '')
                
                # 处理base_home_team_id和base_away_team_id，确保它们是整数类型或None
                base_home_team_id = match.get('baseHomeTeamId')
                try:
                    match_record.base_home_team_id = int(base_home_team_id) if base_home_team_id else None
                    self.logger.info(f'Converted base_home_team_id to int: {match_record.base_home_team_id}')
                except (ValueError, TypeError) as e:
                    self.logger.error(f'Failed to convert base_home_team_id {base_home_team_id} to int: {e}')
                    match_record.base_home_team_id = None
                
                base_away_team_id = match.get('baseAwayTeamId')
                try:
                    match_record.base_away_team_id = int(base_away_team_id) if base_away_team_id else None
                    self.logger.info(f'Converted base_away_team_id to int: {match_record.base_away_team_id}')
                except (ValueError, TypeError) as e:
                    self.logger.error(f'Failed to convert base_away_team_id {base_away_team_id} to int: {e}')
                    match_record.base_away_team_id = None
                
                match_record.match_name = match.get('matchName', f"{match.get('homeTeamName', '')} vs {match.get('awayTeamName', '')}")
                match_record.group_name = match.get('groupName', '')
                
                match_record.match_status = match.get('matchStatus')
                
                # 处理sell_status，确保它是整数类型
                sell_status = match.get('sellStatus', 1 if match.get('poolStatus') == 'Selling' else 0)
                try:
                    match_record.sell_status = int(sell_status)
                    self.logger.info(f'Converted sell_status to int: {match_record.sell_status}')
                except (ValueError, TypeError) as e:
                    self.logger.error(f'Failed to convert sell_status {sell_status} to int: {e}')
                    match_record.sell_status = 0
                
                # 处理is_hot、is_hide等布尔字段，确保它们是整数类型
                for field in ['isHot', 'isHide', 'bettingSingle', 'bettingAllUp']:
                    value = match.get(field, 0)
                    try:
                        setattr(match_record, field.lower(), int(value))
                        self.logger.info(f'Converted {field} to int: {getattr(match_record, field.lower())}')
                    except (ValueError, TypeError) as e:
                        self.logger.error(f'Failed to convert {field} {value} to int: {e}')
                        setattr(match_record, field.lower(), 0)
                
                match_record.back_color = match.get('backColor', '')
                match_record.remark = match.get('remark', '')
                
                localdb.add(match_record, close=False)  # 更新比赛，不关闭会话
            
            localdb.close()  # 所有记录处理完毕后关闭会话
            self.logger.info(f'更新了{len(match_list)}条篮球比赛记录')
            
        except Exception as e:
            self.logger.error(f'Error in _process_match_list:{traceback.format_exc()}, e:{e}')
            localdb.close()  # 发生异常时也关闭会话

    def _process_calculator_data(self, match_info_list):
        '''
        处理篮球赔率数据，更新到数据库
        :param match_info_list: 篮球赔率数据的列表
        :return: None
        '''
        try:
            updated_count = 0
            for match_info in match_info_list:
                # 检查是否有subMatchList字段（这是实际包含比赛记录的地方）
                sub_match_list = match_info.get('subMatchList', [])
                
                if sub_match_list:
                    # 处理subMatchList中的每个比赛记录
                    for sub_match in sub_match_list:
                        match_id = sub_match.get('matchId')
                        
                        # 检查matchId是否有效
                        if not match_id:
                            self.logger.warning('跳过matchId为空的赔率记录')
                            continue
                            
                        # 获取对应的比赛记录
                        match_record = localdb.query(TcbkMatch).filter_by(match_id=match_id).first()
                        if not match_record:
                            self.logger.warning(f'未找到比赛ID为{match_id}的记录，跳过赔率更新')
                            continue
                            
                        # 处理赔率数据
                        # 检查sub_match中是否有赔率相关字段
                        odds_data = {}
                        
                        # 检查是否有直接的赔率字段（如hilo, spf, rfsf）
                        if 'hilo' in sub_match:
                            hilo_odds = sub_match['hilo']
                            odds_data['HILO'] = hilo_odds
                            
                        if 'spf' in sub_match:
                            spf_odds = sub_match['spf']
                            odds_data['SPF'] = spf_odds
                            
                        if 'rfsf' in sub_match:
                            rfsf_odds = sub_match['rfsf']
                            odds_data['RFSF'] = rfsf_odds
                            
                        if 'sfc' in sub_match:
                            sfc_odds = sub_match['sfc']
                            odds_data['SFC'] = sfc_odds
                            
                        # 检查是否有oddsList字段
                        if 'oddsList' in sub_match:
                            for odds in sub_match['oddsList']:
                                pool_code = odds.get('poolCode')
                                if pool_code:
                                    odds_data[pool_code] = odds
                                    
                        # 处理大小分赔率
                        if 'HILO' in odds_data:
                            hilo_odds = odds_data['HILO']
                            goal_line = hilo_odds.get('goalLine')
                            if goal_line is not None:
                                self._process_dxf_data(match_id, hilo_odds, goal_line)
                            else:
                                self.logger.warning(f'比赛ID为{match_id}的大小分赔率缺少盘口数据')
                        
                        # 处理胜负赔率
                        if 'SPF' in odds_data:
                            spf_odds = odds_data['SPF']
                            self._process_spf_data(match_id, spf_odds)
                        
                        # 处理让分胜负赔率
                        if 'RFSF' in odds_data:
                            rfsf_odds = odds_data['RFSF']
                            let_num = rfsf_odds.get('goalLine')
                            if let_num is not None:
                                self._process_rfsf_data(match_id, rfsf_odds, let_num)
                            else:
                                self.logger.warning(f'比赛ID为{match_id}的让分胜负赔率缺少让分数据')
                        
                        # 处理胜分差赔率
                        if 'SFC' in odds_data:
                            sfc_odds = odds_data['SFC']
                            self._process_sfc_data(match_id, sfc_odds)
                        
                        updated_count += 1
                else:
                    # 兼容原来的格式
                    match_id = match_info.get('matchId')
                    
                    # 检查matchId是否有效
                    if not match_id:
                        self.logger.warning('跳过matchId为空的赔率记录')
                        continue
                        
                    # 获取对应的比赛记录
                    match_record = localdb.query(TcbkMatch).filter_by(match_id=match_id).first()
                    if not match_record:
                        self.logger.warning(f'未找到比赛ID为{match_id}的记录，跳过赔率更新')
                        continue
                        
                    # 处理赔率列表
                    odds_list = match_info.get('oddsList', [])
                    pool_list = match_info.get('poolList', [])
                    
                    # 创建一个字典来存储各玩法的赔率数据
                    odds_data = {}
                    for odds in odds_list:
                        pool_code = odds.get('poolCode')
                        if pool_code:
                            odds_data[pool_code] = odds
                            
                    # 处理大小分赔率
                    if 'HILO' in odds_data:
                        hilo_odds = odds_data['HILO']
                        goal_line = hilo_odds.get('goalLine')
                        if goal_line is not None:
                            self._process_dxf_data(match_id, hilo_odds, goal_line)
                        else:
                            self.logger.warning(f'比赛ID为{match_id}的大小分赔率缺少盘口数据')
                    
                    # 处理胜负赔率
                    if 'SPF' in odds_data:
                        spf_odds = odds_data['SPF']
                        self._process_spf_data(match_id, spf_odds)
                    
                    # 处理让分胜负赔率
                    if 'RFSF' in odds_data:
                        rfsf_odds = odds_data['RFSF']
                        let_num = rfsf_odds.get('goalLine')
                        if let_num is not None:
                            self._process_rfsf_data(match_id, rfsf_odds, let_num)
                        else:
                            self.logger.warning(f'比赛ID为{match_id}的让分胜负赔率缺少让分数据')
                    
                    # 处理胜分差赔率
                    if 'SFC' in odds_data:
                        sfc_odds = odds_data['SFC']
                        self._process_sfc_data(match_id, sfc_odds)
                    
                    updated_count += 1
            
            localdb.close()  # 所有记录处理完毕后关闭会话
            self.logger.info(f'更新了{updated_count}条篮球比赛赔率记录')
            
        except Exception as e:
            self.logger.error(f'Error in _process_calculator_data:{traceback.format_exc()}, e:{e}')
            localdb.close()  # 发生异常时也关闭会话

    def _process_spf_data(self, match_id, odds):
        '''
        处理篮球胜负赔率数据
        :param match_id: 比赛ID
        :param odds: 胜负赔率数据
        :return: None
        '''
        try:
            # 获取或创建胜负赔率记录
            spf = localdb.query(TcbkSpf).filter_by(match_id=match_id).first()
            
            # 检查赔率是否变化
            odds_changed = False
            if spf and (spf.h != odds.get('h') or spf.a != odds.get('a')):
                odds_changed = True
            elif not spf:
                odds_changed = True
            
            if not spf:
                spf = TcbkSpf(match_id=match_id)
            
            # 更新赔率信息
            spf.h = odds.get('h')
            spf.a = odds.get('a')
            
            # 更新时间信息
            spf.update_time = self.nowtime
            
            localdb.add(spf, close=False)
            
            # 如果赔率有变化，记录到历史表
            if odds_changed:
                self._save_odds_history(match_id, 'spf', odds)
            
        except Exception as e:
            self.logger.error(f'Error in _process_spf_data for match {match_id}:{traceback.format_exc()}, e:{e}')

    def _process_rfsf_data(self, match_id, odds, let_num):
        '''
        处理篮球让分胜负赔率数据
        :param match_id: 比赛ID
        :param odds: 让分胜负赔率数据
        :param let_num: 让分数值
        :return: None
        '''
        try:
            # 获取或创建让分胜负赔率记录
            rfsf = localdb.query(TcbkRfsf).filter_by(match_id=match_id).first()
            
            # 检查赔率是否变化
            odds_changed = False
            if rfsf and (
                rfsf.h != odds.get('h') or 
                rfsf.a != odds.get('a') or 
                rfsf.goal_line != let_num
            ):
                odds_changed = True
            elif not rfsf:
                odds_changed = True
            
            if not rfsf:
                rfsf = TcbkRfsf(match_id=match_id)
            
            # 更新赔率信息
            rfsf.goal_line = let_num
            rfsf.goal_line_str = str(let_num)
            rfsf.h = odds.get('h')
            rfsf.a = odds.get('a')
            
            # 更新时间信息
            rfsf.update_time = self.nowtime
            
            localdb.add(rfsf, close=False)
            
            # 如果赔率有变化，记录到历史表
            if odds_changed:
                # 将让分数值添加到赔率数据中，以便保存到历史表
                odds_copy = odds.copy() if isinstance(odds, dict) else {}
                odds_copy['goal_line'] = let_num
                self._save_odds_history(match_id, 'rfsf', odds_copy)
            
        except Exception as e:
            self.logger.error(f'Error in _process_rfsf_data for match {match_id}:{traceback.format_exc()}, e:{e}')

    def _process_dxf_data(self, match_id, odds, goal_line):
        '''
        处理篮球大小分赔率数据
        :param match_id: 比赛ID
        :param odds: 大小分赔率数据
        :param goal_line: 大小分盘口
        :return: None
        '''
        try:
            # 获取或创建大小分赔率记录
            dxf = localdb.query(TcbkDxf).filter_by(match_id=match_id).first()
            
            # 检查赔率是否变化
            odds_changed = False
            if dxf and (
                dxf.over != odds.get('h') or 
                dxf.under != odds.get('a') or 
                dxf.goal_line != goal_line
            ):
                odds_changed = True
            elif not dxf:
                odds_changed = True
            
            if not dxf:
                dxf = TcbkDxf(match_id=match_id)
            
            # 更新赔率信息
            dxf.goal_line = goal_line
            dxf.goal_line_str = str(goal_line)
            dxf.over = odds.get('h')  # 大分对应h
            dxf.under = odds.get('a')  # 小分对应a
            
            # 更新时间信息
            dxf.update_time = self.nowtime
            
            localdb.add(dxf, close=False)
            
            # 如果赔率有变化，记录到历史表
            if odds_changed:
                # 将大小分盘口添加到赔率数据中，以便保存到历史表
                odds_copy = odds.copy() if isinstance(odds, dict) else {}
                odds_copy['goal_line'] = goal_line
                odds_copy['over'] = odds.get('h')  # 大分对应h
                odds_copy['under'] = odds.get('a')  # 小分对应a
                self._save_odds_history(match_id, 'dxf', odds_copy)
            
        except Exception as e:
            self.logger.error(f'Error in _process_dxf_data for match {match_id}:{traceback.format_exc()}, e:{e}')

    def _process_sfc_data(self, match_id, odds):
        '''
        处理篮球胜分差赔率数据
        :param match_id: 比赛ID
        :param odds: 胜分差赔率数据
        :return: None
        '''
        try:
            # 获取或创建胜分差赔率记录
            sfc = localdb.query(TcbkSfc).filter_by(match_id=match_id).first()
            
            # 检查赔率是否变化
            odds_changed = False
            if not sfc:
                odds_changed = True
            # 由于API可能不直接返回sfc的详细赔率，暂时不进行赔率变化检查
            
            if not sfc:
                sfc = TcbkSfc(match_id=match_id)
            
            # 更新赔率信息 - 根据实际API返回格式调整
            # 这里可能需要根据实际返回的胜分差赔率结构进行调整
            # 目前API可能不直接返回sfc的详细赔率，所以暂时跳过
            self.logger.warning(f'胜分差赔率数据格式可能不匹配，暂时跳过比赛ID {match_id}')
            
            localdb.add(sfc, close=False)
            
            # 如果赔率有变化，记录到历史表
            if odds_changed and odds:
                self._save_odds_history(match_id, 'sfc', odds)
            
        except Exception as e:
            self.logger.error(f'Error in _process_sfc_data for match {match_id}:{traceback.format_exc()}, e:{e}')

    def _save_odds_history(self, match_id, odds_type, odds_data):
        '''
        保存赔率历史记录
        :param match_id: 比赛ID
        :param odds_type: 赔率类型 ('spf', 'rfsf', 'dxf', 'sfc')
        :param odds_data: 赔率数据字典
        :return: None
        '''
        try:
            # 获取比赛信息
            match = localdb.query(TcbkMatch).filter_by(match_id=match_id).first()
            if not match:
                self.logger.warning(f'未找到比赛ID为{match_id}的记录，无法保存赔率历史')
                return
            
            # 创建赔率历史主记录
            odds_history = TcbkOddsHistory(
                match_id=match_id,
                home_team_id=match.home_team_id,
                away_team_id=match.away_team_id,
                home_team_all_name=match.home_team_all_name,
                home_team_abb_name=match.home_team_abb_name,
                away_team_all_name=match.away_team_all_name,
                away_team_abb_name=match.away_team_abb_name,
                league_id=match.league_id
            )
            
            localdb.add(odds_history, close=False)
            
            # 根据赔率类型创建相应的赔率历史详情记录
            if odds_type == 'spf':
                spf_history = TcbkOddsHistorySpf(
                    odds_history_id=odds_history.id,
                    h=odds_data.get('h'),
                    a=odds_data.get('a')
                )
                localdb.add(spf_history, close=False)
                
            elif odds_type == 'rfsf':
                rfsf_history = TcbkOddsHistoryRfsf(
                    odds_history_id=odds_history.id,
                    goal_line=odds_data.get('goal_line'),
                    goal_line_str=str(odds_data.get('goal_line')),
                    h=odds_data.get('h'),
                    a=odds_data.get('a')
                )
                localdb.add(rfsf_history, close=False)
                
            elif odds_type == 'dxf':
                dxf_history = TcbkOddsHistoryDxf(
                    odds_history_id=odds_history.id,
                    goal_line=odds_data.get('goal_line'),
                    goal_line_str=str(odds_data.get('goal_line')),
                    over=odds_data.get('over'),
                    under=odds_data.get('under')
                )
                localdb.add(dxf_history, close=False)
                
            elif odds_type == 'sfc':
                sfc_history = TcbkOddsHistorySfc(
                    odds_history_id=odds_history.id,
                    # 胜分差赔率 - 主队胜
                    h1=odds_data.get('h1'),
                    h2=odds_data.get('h2'),
                    h3=odds_data.get('h3'),
                    h4=odds_data.get('h4'),
                    h5=odds_data.get('h5'),
                    h6=odds_data.get('h6'),
                    # 胜分差赔率 - 客队胜
                    a1=odds_data.get('a1'),
                    a2=odds_data.get('a2'),
                    a3=odds_data.get('a3'),
                    a4=odds_data.get('a4'),
                    a5=odds_data.get('a5'),
                    a6=odds_data.get('a6')
                )
                localdb.add(sfc_history, close=False)
                
            self.logger.info(f'保存了比赛ID {match_id} 的{odds_type}赔率历史记录')
            
        except Exception as e:
            self.logger.error(f'Error in _save_odds_history for match {match_id} ({odds_type}):{traceback.format_exc()}, e:{e}')

    def get_match_result(self, match_date):
        '''
        获取指定日期的篮球比赛赛果
        :param match_date: 比赛日期，格式为YYYY-MM-DD
        :return: None
        '''
        try:
            result_data = self.api.get_basketball_match_result(match_date)
            
            if 'matchResultList' in result_data:
                self._process_result_data(result_data['matchResultList'])
                self.logger.info(f'篮球比赛赛果更新完成，日期：{match_date}')
            else:
                self.logger.info(f'未获取到{match_date}的篮球比赛赛果数据')
                
        except Exception as e:
            self.logger.error(f'Error in get_match_result:{traceback.format_exc()}, e:{e}')
    
    def get_match_results(self):
        '''
        查询数据库，根据比赛时间判断哪些比赛需要获取结果，并更新到数据库
        '''
        try:
            # 获取当前完整的日期时间
            current_datetime = datetime.now()
            current_time = current_datetime.strftime('%H:%M:%S')
            current_date = current_datetime.strftime('%Y-%m-%d')
            
            self.logger.info(f"获取篮球比赛结果...")
            self.logger.info(f"当前时间: {current_time}")
            self.logger.info(f"当前日期: {current_date}")
            self.logger.info(f"完整当前时间: {current_datetime}")
            
            # 查询需要获取结果的比赛
            try:
                # 获取所有状态为进行中或未开始的比赛
                all_matches = localdb.query(TcbkMatch).filter_by(sell_status=1).all()
                
                # 筛选出已经结束的比赛（比赛时间 < 当前时间）
                matches_to_check = []
                for match in all_matches:
                    try:
                        # 解析比赛时间
                        match_time_str = match.match_time
                        if not match_time_str:
                            continue
                            
                        # 转换为datetime对象
                        if len(match_time_str) > 19:
                            match_time_str = match_time_str[:19]  # 截断过长的时间字符串
                            
                        match_datetime = datetime.strptime(match_time_str, '%Y-%m-%d %H:%M:%S')
                        
                        # 判断比赛是否已经结束
                        if match_datetime < current_datetime:
                            matches_to_check.append(match)
                            self.logger.info(f"比赛 {match.match_week} {match.match_num_str} {match.home_team_abb_name} vs {match.away_team_abb_name} 已结束，需要获取结果")
                        else:
                            self.logger.info(f"比赛 {match.match_week} {match.match_num_str} {match.home_team_abb_name} vs {match.away_team_abb_name} 尚未开始，跳过")
                    except Exception as e:
                        self.logger.error(f"解析比赛时间失败: {str(e)}")
                        continue
                
                if not matches_to_check:
                    self.logger.info("没有需要获取结果的比赛")
                    return
                    
                self.logger.info(f"\n总计查询到 {len(matches_to_check)} 场需要获取结果的比赛")
                
                # 获取这些比赛所在的日期
                match_dates = list(set([match.match_date for match in matches_to_check]))
                
                # 按日期获取比赛结果
                for match_date in match_dates:
                    try:
                        result_data = self.api.get_basketball_match_result(match_date)
                        
                        if 'matchResultList' in result_data:
                            self.logger.info(f'获取到 {match_date} 的 {len(result_data["matchResultList"])} 场比赛结果')
                            self._process_result_data(result_data['matchResultList'])
                        else:
                            self.logger.warning(f'未获取到 {match_date} 的篮球比赛赛果数据')
                            
                    except Exception as e:
                        self.logger.error(f'获取 {match_date} 比赛结果API调用失败: {str(e)}')
                        import traceback
                        traceback.print_exc()
                        
            except Exception as e:
                self.logger.error(f"查询比赛失败: {str(e)}")
                import traceback
                traceback.print_exc()
                return
                
        except Exception as e:
            self.logger.error(f"获取比赛结果失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _process_result_data(self, result_list):
        '''
        处理篮球比赛赛果数据
        :param result_list: 赛果数据列表
        :return: None
        '''
        try:
            for result in result_list:
                match_id = result.get('matchId')
                
                # 获取对应的比赛记录
                match_record = localdb.query(TcbkMatch).filter_by(match_id=match_id).first()
                if not match_record:
                    self.logger.warning(f'未找到比赛ID为{match_id}的记录，跳过赛果更新')
                    continue
                
                # 获取或创建赛果记录
                result_record = localdb.query(TcbkResult).filter_by(match_id=match_id).first()
                if not result_record:
                    result_record = TcbkResult(match_id=match_id)
                
                # 更新赛果基本信息
                result_record.match_result_status = result.get('matchResultStatus')
                result_record.pool_status = result.get('poolStatus')
                result_record.result_status = result.get('resultStatus')
                
                # 处理比分信息
                full_score = result.get('fullScore')
                result_record.full_score = full_score
                
                if full_score and '-' in full_score:
                    home_score, away_score = map(int, full_score.split('-'))
                    result_record.home_score = home_score
                    result_record.away_score = away_score
                    result_record.score_diff = abs(home_score - away_score)
                    
                    # 确定获胜方
                    if home_score > away_score:
                        result_record.win_flag = 'H'
                    elif away_score > home_score:
                        result_record.win_flag = 'A'
                
                # 处理玩法结果
                result_record.spf_result = result.get('spfResult')
                result_record.rfsf_result = result.get('rfsfResult')
                result_record.dxf_result = result.get('dxfResult')
                result_record.sfc_result = result.get('sfcResult')
                
                localdb.add(result_record, close=False)
                
            localdb.commit()
            self.logger.info(f'更新了{len(result_list)}条篮球比赛赛果记录')
            
        except Exception as e:
            localdb.rollback()
            self.logger.error(f'Error in _process_result_data:{traceback.format_exc()}, e:{e}')


if __name__ == '__main__':
    '''
    测试篮球数据爬取功能
    '''
    print('=== 篮球数据爬取测试 ===')
    
    # 创建实例
    jcbk_spider = get_jcbk_data()
    
    # 测试获取比赛数据
    print('获取篮球比赛数据...')
    jcbk_spider.get_gamedata()
    
    # 测试获取赛果数据（使用当前日期）
    print('获取篮球比赛赛果...')
    today = datetime.now().strftime('%Y-%m-%d')
    jcbk_spider.get_match_result(today)
    
    # 测试根据时间判断获取比赛结果
    print('\n根据时间判断获取篮球比赛结果...')
    jcbk_spider.get_match_results()
    
    print('测试完成！')