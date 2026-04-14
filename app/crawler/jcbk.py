# -*- coding: utf-8 -*-
"""
竞彩篮球数据采集器
实现获取篮球比赛数据和赔率信息的功能
"""
import sys
import os
import json
import traceback
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.common.req_sporttery_api import SportteryAPI
from app.log import jcbk_log as logger
from app.database import localdb, TcbkLeague, TcbkMatch


class JcbkDataCollector:
    """
    竞彩篮球数据采集器
    """
    
    def __init__(self):
        self.api = SportteryAPI()
    
    def _process_league_info(self, league_id: int, league_name: str, league_name_abbr: str = '') -> int:
        """
        处理联赛信息，若不存在则新增
        
        Args:
            league_id: 联赛 ID
            league_name: 联赛名称
            league_name_abbr: 联赛简称
            
        Returns:
            int: 联赛在数据库中的 ID
        """
        try:
            league = localdb.query(TcbkLeague).filter_by(league_id=league_id).first()
            
            if not league:
                # 确保联赛名称不为 None
                if league_name is None:
                    league_name = f'未知联赛_{league_id}'
                    logger.debug(f'联赛 ID {league_id} 无名称，使用默认名：{league_name}')
                
                league = TcbkLeague(
                    league_id=league_id,
                    league_name=league_name,
                    league_name_abbr=league_name_abbr or ''
                )
                localdb.add(league, close=False)
                logger.info(f'新增联赛：{league_name}')
            else:
                # 更新联赛简称
                if league_name_abbr and league.league_name_abbr != league_name_abbr:
                    league.league_name_abbr = league_name_abbr
                    localdb.update(league, close=False)
            
            return league.id
            
        except Exception as e:
            logger.error(f'处理联赛失败 (league_id={league_id}): {str(e)}')
            return None
    
    def _process_match_data(self, match_list) -> int:
        """
        处理比赛列表数据
        
        Args:
            match_list: 比赛列表 DataFrame
            
        Returns:
            int: 成功处理的比赛数量
        """
        try:
            processed_count = 0
            
            for index, match in match_list.iterrows():
                # 获取或创建联赛记录
                league_id = match.get('leagueId')
                if not league_id:
                    continue
                
                # 使用正确的字段名：leagueAllName 和 leagueAbbName
                league_name = match.get('leagueAllName', '')
                league_name_abbr = match.get('leagueAbbName', '')
                
                league_db_id = self._process_league_info(
                    league_id,
                    league_name,
                    league_name_abbr
                )
                
                if not league_db_id:
                    continue
                
                # 获取或创建比赛记录
                match_id = match.get('matchId')
                if not match_id:
                    continue
                
                match_record = localdb.query(TcbkMatch).filter_by(match_id=match_id).first()
                if not match_record:
                    match_record = TcbkMatch()
                    match_record.match_id = match_id
                
                # 更新比赛信息
                match_record.match_num = match.get('matchNum')
                match_record.match_num_str = match.get('matchNumStr')
                match_record.match_num_date = match.get('matchNumDate')
                match_record.match_week = match.get('matchWeek')
                match_record.match_date = match.get('matchDate')
                
                # 处理 match_time 字段
                match_time = match.get('matchTime')
                if match_time is not None:
                    if hasattr(match_time, 'strftime'):
                        match_record.match_time = match_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        match_record.match_time = str(match_time)
                
                match_record.business_date = match.get('businessDate', match.get('matchDate'))
                
                # 转换 league_id 为整数
                try:
                    match_record.league_id = int(league_id)
                except (ValueError, TypeError) as e:
                    logger.error(f'Failed to convert league_id to int: {e}')
                    continue
                
                # 处理主队信息
                home_team_id = match.get('homeTeamId')
                try:
                    match_record.home_team_id = int(home_team_id) if home_team_id else None
                except (ValueError, TypeError) as e:
                    logger.error(f'Failed to convert home_team_id to int: {e}')
                    match_record.home_team_id = None
                
                match_record.home_team_code = match.get('homeTeamCode', '')
                match_record.home_team_all_name = match.get('homeTeamAllName', match.get('homeTeamName', ''))
                match_record.home_team_abb_name = match.get('homeTeamAbbrName', match.get('homeTeamName', ''))
                match_record.home_team_rank = match.get('homeTeamRank', '')
                
                # 处理客队信息
                away_team_id = match.get('awayTeamId')
                try:
                    match_record.away_team_id = int(away_team_id) if away_team_id else None
                except (ValueError, TypeError) as e:
                    logger.error(f'Failed to convert away_team_id to int: {e}')
                    match_record.away_team_id = None
                
                match_record.away_team_code = match.get('awayTeamCode', '')
                match_record.away_team_all_name = match.get('awayTeamAllName', match.get('awayTeamName', ''))
                match_record.away_team_abb_name = match.get('awayTeamAbbrName', match.get('awayTeamName', ''))
                match_record.away_team_rank = match.get('awayTeamRank', '')
                
                # 处理其他字段
                base_home_team_id = match.get('baseHomeTeamId')
                try:
                    match_record.base_home_team_id = int(base_home_team_id) if base_home_team_id else None
                except (ValueError, TypeError) as e:
                    logger.error(f'Failed to convert base_home_team_id to int: {e}')
                    match_record.base_home_team_id = None
                
                base_away_team_id = match.get('baseAwayTeamId')
                try:
                    match_record.base_away_team_id = int(base_away_team_id) if base_away_team_id else None
                except (ValueError, TypeError) as e:
                    logger.error(f'Failed to convert base_away_team_id to int: {e}')
                    match_record.base_away_team_id = None
                
                match_record.match_name = match.get('matchName', f"{match.get('homeTeamName', '')} vs {match.get('awayTeamName', '')}")
                match_record.group_name = match.get('groupName', '')
                match_record.match_status = match.get('matchStatus')
                
                # 处理 sell_status
                sell_status = match.get('sellStatus', 1 if match.get('poolStatus') == 'Selling' else 0)
                try:
                    match_record.sell_status = int(sell_status)
                except (ValueError, TypeError) as e:
                    logger.error(f'Failed to convert sell_status to int: {e}')
                    match_record.sell_status = 0
                
                # 处理布尔字段
                for field in ['isHot', 'isHide', 'bettingSingle', 'bettingAllUp']:
                    value = match.get(field, 0)
                    try:
                        setattr(match_record, field.lower(), int(value))
                    except (ValueError, TypeError) as e:
                        logger.error(f'Failed to convert {field} to int: {e}')
                        setattr(match_record, field.lower(), 0)
                
                match_record.back_color = match.get('backColor', '')
                match_record.remark = match.get('remark', '')
                
                # 保存到数据库
                try:
                    if not hasattr(match_record, 'id') or not match_record.id:
                        localdb.add(match_record, close=False)
                    else:
                        localdb.update(match_record, close=False)
                    processed_count += 1
                except Exception as e:
                    logger.error(f'保存比赛记录失败 (match_id={match_id}): {str(e)}')
                    continue
            
            return processed_count
            
        except Exception as e:
            logger.error(f'处理比赛数据异常：{traceback.format_exc()}')
            return 0
    
    def collect_matches(self) -> bool:
        """
        采集篮球比赛数据
            
        Returns:
            bool: 采集成功返回 True
        """
        try:
            logger.info('开始采集竞彩篮球比赛数据...')
                
            # 获取比赛列表
            try:
                match_list = self.api.get_basketball_match_list()
                logger.info(f'成功获取篮球比赛列表，共 {len(match_list)} 场比赛')
            except Exception as e:
                logger.error(f'获取篮球比赛列表失败：{e}')
                return False
                
            if match_list.empty:
                logger.info('获取到的比赛列表为空')
                return False
                
            # 处理比赛数据
            logger.info(f'开始处理 {len(match_list)} 条比赛数据')
            count = self._process_match_data(match_list)
                
            logger.info(f'成功处理 {count} 条比赛记录')
            return count > 0
                
        except Exception as e:
            logger.error(f'采集篮球比赛数据异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def get_matches_with_odds(self) -> list:
        """
        获取比赛数据（带赔率）
            
        Returns:
            list: 比赛数据列表
        """
        try:
            logger.info('开始获取篮球比赛数据（带赔率）...')
                
            # 获取比赛列表
            match_list = self.api.get_basketball_match_list()
                
            if match_list.empty:
                logger.info('获取到的比赛列表为空')
                return []
                
            logger.info(f'成功获取 {len(match_list)} 场篮球比赛')
            
            # 处理API返回的嵌套结构（类似足球）
            all_matches = []
            for index, row in match_list.iterrows():
                sub_match_list = row.get('subMatchList', [])
                if isinstance(sub_match_list, list):
                    all_matches.extend(sub_match_list)
            
            logger.info(f'共提取 {len(all_matches)} 场实际比赛')
            
            if not all_matches:
                logger.info('没有实际比赛数据')
                return []
            
            # 将列表转换为DataFrame
            import pandas as pd
            matches_df = pd.DataFrame(all_matches)
                
            # 处理比赛数据
            logger.info('开始处理比赛数据...')
            self._process_match_data(matches_df)
            localdb.commit()  # 提交事务
            logger.info('比赛数据处理完成')
                
            # 获取赔率数据
            try:
                logger.info('开始获取篮球赔率数据...')
                # 篮球的poolCode: hilo(大小分), hdc(让分胜负), wnm(胜分差), mnl(胜负)
                calculator_data = self.api.get_basketball_match_calculator(['hilo', 'hdc', 'wnm', 'mnl'])
                logger.info('成功获取篮球赔率数据')
            except Exception as e:
                logger.error(f'获取篮球赔率数据失败：{e}')
                calculator_data = {}
                
            # 处理赔率数据
            if 'matchInfoList' in calculator_data:
                logger.info(f'开始处理 {len(calculator_data["matchInfoList"])} 条赔率数据')
                self._process_odds_data(calculator_data['matchInfoList'])
                logger.info('赔率数据处理完成')
            else:
                logger.debug('计算器数据中没有 matchInfoList 字段')
                
            return match_list.to_dict('records')
                
        except Exception as e:
            logger.error(f'获取篮球比赛数据异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _process_odds_data(self, odds_data):
        """
        处理赔率数据
        
        Args:
            odds_data: matchInfoList 列表，每个元素包含 subMatchList
        """
        try:
            for match_info in odds_data:
                # 从 subMatchList 中获取实际的比赛数据
                sub_match_list = match_info.get('subMatchList', [])
                
                if not sub_match_list:
                    continue
                
                # 处理 subMatchList 中的每场比赛
                for sub_match in sub_match_list:
                    match_id = sub_match.get('matchId')
                    if not match_id:
                        continue
                    
                    # 保存各种赔率数据到数据库
                    self._save_odds_to_db(match_id, sub_match)
                
        except Exception as e:
            logger.error(f'处理赔率数据失败：{str(e)}')
            import traceback
            logger.error(traceback.format_exc())
    
    def _save_odds_to_db(self, match_id: int, odds_data: dict):
        """
        保存赔率数据到数据库，并记录赔率变化
        
        Args:
            match_id: 比赛 ID
            odds_data: 赔率数据（包含 hilo, mnl, wnm, vote, hdc 等）
        """
        from app.database import TcbkSpf, TcbkRfsf, TcbkDxf, TcbkSfc
        
        try:
            # 保存大小分赔率 (hilo -> dxf)
            if 'hilo' in odds_data and odds_data['hilo']:
                api_data = odds_data['hilo']
                db_data = {
                    'goal_line': float(api_data.get('goalLineValue', 0)),
                    'goal_line_str': api_data.get('goalLine', ''),
                    'over': float(api_data.get('h', 0)),
                    'under': float(api_data.get('l', 0))
                }
                
                existing = localdb.query(TcbkDxf).filter_by(match_id=match_id).first()
                if existing:
                    # 记录赔率变化
                    self._log_odds_change(
                        match_id, 'tcbk_dxf', existing.id, db_data,
                        ['over', 'under']
                    )
                    # 更新现有记录
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                    logger.debug(f"更新大小分赔率：match_id={match_id}")
                else:
                    new_odds = TcbkDxf(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
                    logger.debug(f"新增大小分赔率：match_id={match_id}")
            
            # 保存让分胜负赔率 (hdc -> rfsf)
            if 'hdc' in odds_data and odds_data['hdc']:
                api_data = odds_data['hdc']
                db_data = {
                    'goal_line': float(api_data.get('goalLineValue', 0)),
                    'goal_line_str': api_data.get('goalLine', ''),
                    'h': float(api_data.get('h', 0)),
                    'a': float(api_data.get('a', 0))
                }
                
                existing = localdb.query(TcbkRfsf).filter_by(match_id=match_id).first()
                if existing:
                    self._log_odds_change(
                        match_id, 'tcbk_rfsf', existing.id, db_data,
                        ['h', 'a']
                    )
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                    logger.debug(f"更新让分胜负赔率：match_id={match_id}")
                else:
                    new_odds = TcbkRfsf(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
                    logger.debug(f"新增让分胜负赔率：match_id={match_id}")
            
            # 保存胜负赔率 (mnl -> spf)
            if 'mnl' in odds_data and odds_data['mnl']:
                api_data = odds_data['mnl']
                db_data = {
                    'h': float(api_data.get('h', 0)),
                    'a': float(api_data.get('a', 0))
                }
                
                existing = localdb.query(TcbkSpf).filter_by(match_id=match_id).first()
                if existing:
                    self._log_odds_change(
                        match_id, 'tcbk_spf', existing.id, db_data,
                        ['h', 'a']
                    )
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                    logger.debug(f"更新胜负赔率：match_id={match_id}")
                else:
                    new_odds = TcbkSpf(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
                    logger.debug(f"新增胜负赔率：match_id={match_id}")
            
            # 保存胜分差赔率 (wnm -> sfc)
            if 'wnm' in odds_data and odds_data['wnm']:
                api_data = odds_data['wnm']
                db_data = {
                    'h1': float(api_data.get('w1', 0)),  # API使用w1-w6表示主队胜分差
                    'h2': float(api_data.get('w2', 0)),
                    'h3': float(api_data.get('w3', 0)),
                    'h4': float(api_data.get('w4', 0)),
                    'h5': float(api_data.get('w5', 0)),
                    'h6': float(api_data.get('w6', 0)),
                    'a1': float(api_data.get('l1', 0)),  # API使用l1-l6表示客队胜分差
                    'a2': float(api_data.get('l2', 0)),
                    'a3': float(api_data.get('l3', 0)),
                    'a4': float(api_data.get('l4', 0)),
                    'a5': float(api_data.get('l5', 0)),
                    'a6': float(api_data.get('l6', 0))
                }
                
                existing = localdb.query(TcbkSfc).filter_by(match_id=match_id).first()
                if existing:
                    self._log_odds_change(
                        match_id, 'tcbk_sfc', existing.id, db_data,
                        list(db_data.keys())
                    )
                    for k, v in db_data.items():
                        setattr(existing, k, v)
                    localdb.update(existing, close=False)
                    logger.debug(f"更新胜分差赔率：match_id={match_id}")
                else:
                    new_odds = TcbkSfc(match_id=match_id, **db_data)
                    localdb.add(new_odds, close=False)
                    logger.debug(f"新增胜分差赔率：match_id={match_id}")
                    
        except Exception as e:
            logger.error(f"保存赔率数据失败 (match_id={match_id}): {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _log_odds_change(self, match_id: int, odds_table: str, odds_record_id: int,
                         new_data: dict, fields: list):
        """
        记录赔率变化日志（带阈值判断）
        
        Args:
            match_id: 比赛ID
            odds_table: 赔率表名 (如 tcbk_spf, tcbk_dxf)
            odds_record_id: 赔率记录ID
            new_data: 新数据字典
            fields: 需要检查变化的字段列表
        """
        from app.database import TcbkOddsChangeLog
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
                    sport_type='tcbk',  # 竞彩篮球
                    threshold=0.05  # 波动阈值 ±0.05
                )
                
                if should_log:
                    change_log = TcbkOddsChangeLog(
                        match_id=match_id,
                        odds_table=odds_table,
                        odds_record_id=odds_record_id,
                        odds_field=field,
                        old_value=float(current_value) if current_value != 0.0 else 0.0,
                        new_value=float(new_value),
                        change_time=datetime.now()
                    )
                    localdb.add(change_log, close=False)
                    logger.info(f"✓ 记录篮球赔率变化: {odds_table}.{field} "
                              f"{current_value:.3f} -> {new_value:.3f} (diff={diff:.3f})")
                else:
                    logger.debug(f"⊘ 忽略篮球小幅波动: {odds_table}.{field} "
                               f"{current_value:.3f} -> {new_value:.3f} (diff={diff:.3f})")
        except Exception as e:
            logger.error(f"记录篮球赔率变化失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    """
    单独调试测试 JcbkDataCollector 类
    """
    import sys
    import os
    
    # 添加项目根目录到 Python 路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 配置日志输出到控制台
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print(" " * 20 + "开始测试 JcbkDataCollector")
    print("="*70)
    
    try:
        # 创建采集器实例
        collector = JcbkDataCollector()
        
        print("\n【测试 1】获取比赛数据（带赔率）")
        print("-"*70)
        matches = collector.get_matches_with_odds()
        print(f"✓ 成功获取 {len(matches)} 场比赛数据")
        
        if matches:
            print(f"\n第一场比赛信息：")
            first_match = matches[0]
            for key, value in list(first_match.items())[:10]:
                print(f"  {key}: {value}")
        
        print("\n" + "="*70)
        print("测试完成！")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70 + "\n")
