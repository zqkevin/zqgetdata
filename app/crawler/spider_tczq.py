# -*- coding: utf-8 -*-
"""
体彩足球爬虫模块
实现获取当前赛事信息、处理联赛信息和获取比赛结果的功能
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
from app.common.logger import log as logger
from app.database import localdb
from app.database.tczq_models import (
    TczqLeague,
    TczqMatch,
    TczqResult,
    TczqCrs,
    TczqHad,
    TczqHhad,
    TczqHafu,
    TczqTtg,
    TczqOddsHistory,
    TczqOddsHistoryHad,
    TczqOddsHistoryHhad,
    TczqOddsHistoryHafu,
    TczqOddsHistoryTtg,
    TczqOddsHistoryCrs
)


class TczqSpider:
    """
    体彩足球爬虫类
    """
    
    def __init__(self):
        """
        初始化爬虫实例
        """
        self.api = SportteryAPI()
    
    def _process_league_info(self, league_list: List[Dict[str, str]]) -> None:
        """
        处理联赛信息，若不存在则新增到数据库
        
        Args:
            league_list: 联赛信息列表
        """
        print(f"处理联赛信息，共 {len(league_list)} 个联赛")
        for league_info in league_list:
            print(f"联赛信息: {json.dumps(league_info, ensure_ascii=False)}")
            league_id = int(league_info.get('leagueId', 0))
            league_name = league_info.get('leagueName', '')
            league_name_abbr = league_info.get('leagueNameAbbr', '')
            
            if not all([league_id, league_name, league_name_abbr]):
                print(f"联赛信息不完整，跳过: league_id={league_id}, league_name={league_name}, league_name_abbr={league_name_abbr}")
                continue
            
            # 查询数据库中是否已存在该联赛
            try:
                existing_league = localdb.query(TczqLeague).filter_by(league_id=league_id).first()
                
                if not existing_league:
                    # 新增联赛信息
                    new_league = TczqLeague(
                        league_id=league_id,
                        league_name=league_name,
                        league_name_abbr=league_name_abbr
                    )
                    localdb.add(new_league, close=False)
                    print(f"新增联赛: {league_name} ({league_name_abbr})")
            except Exception as e:
                print(f"处理联赛失败 (league_id={league_id}): {str(e)}")
                import traceback
                traceback.print_exc()
    
    def get_current_matches(self) -> None:
        """
        获取当前赛事信息并记录到数据库
        """
        matches = []  # 初始化比赛列表
        try:
            # 获取当前可投注的足球比赛列表
            logger.info("正在获取当前赛事信息...")
            match_data = self.api.get_football_match_list(pool_codes=["had", "hhad", "ttg", "hafu", "crs"])
            
            if not match_data:
                logger.warning("未获取到赛事数据")
                return matches
            
            # 处理联赛信息
            self._process_league_info(match_data.get("league_list", []))
            
            # 处理比赛信息
            match_info_list = match_data.get("match_info_list", [])
            logger.info(f"共处理 {len(match_info_list)} 个日期/时间段的比赛集合")
            
            total_matches = 0
            processed_matches = 0
            
            for idx, date_match_set in enumerate(match_info_list):
                logger.info(f"处理第 {idx+1} 个日期/时间段的比赛集合")
                
                # 获取真正的比赛列表
                sub_match_list = date_match_set.get('subMatchList', [])
                total_matches += len(sub_match_list)
                logger.info(f"该集合包含 {len(sub_match_list)} 场比赛")
                
                for sub_idx, match in enumerate(sub_match_list):
                    logger.info(f"处理第 {processed_matches+1} 场比赛")
                    processed_matches += 1
                    
                    # 解析比赛基本信息
                    match_id = match.get('matchId', '')
                    logger.info(f"解析到的match_id: {match_id}")
                    
                    try:
                        match_id = int(match_id) if match_id else 0
                    except ValueError:
                        logger.warning(f"match_id格式错误: {match_id}")
                        continue
                        
                    match_num_str = match.get('matchNum', '')
                    match_num_date = match.get('matchNumDate', '')
                    match_week = match.get('matchWeek', '')
                    match_date = match.get('matchDate', '')
                    match_time = match.get('matchTime', '')
                    business_date = match.get('businessDate', '')
                    tax_date_no = match.get('taxDateNo', '')
                    
                    league_id = int(match.get('leagueId', '0'))
                    
                    # 解析球队信息
                    home_team_id = int(match.get('homeTeamId', '0'))
                    home_team_code = match.get('homeTeamCode', '')
                    home_team_all_name = match.get('homeTeamAllName', '')
                    home_team_abb_name = match.get('homeTeamAbbName', '')
                    home_team_abb_en_name = match.get('homeTeamAbbEnName', '')
                    home_rank = match.get('homeRank', '')
                    
                    away_team_id = int(match.get('awayTeamId', '0'))
                    away_team_code = match.get('awayTeamCode', '')
                    away_team_all_name = match.get('awayTeamAllName', '')
                    away_team_abb_name = match.get('awayTeamAbbName', '')
                    away_team_abb_en_name = match.get('awayTeamAbbEnName', '')
                    away_rank = match.get('awayRank', '')
                    
                    # 解析比赛其他信息
                    base_home_team_id = int(match.get('baseHomeTeamId', '0'))
                    base_away_team_id = int(match.get('baseAwayTeamId', '0'))
                    match_name = match.get('matchName', '')
                    group_name = match.get('groupName', '')
                    line_num = match.get('lineNum', '')
                    
                    # 解析投注信息
                    betting_single = int(match.get('bettingSingle', '0'))
                    betting_all_up = int(match.get('bettingAllUp', '0'))
                    
                    if not match_id:
                        logger.warning("match_id为空，跳过该比赛")
                        continue
                    
                    # 将比赛信息添加到返回列表中
                    match_info = {
                        'match_id': match_id,
                        'match_num_str': match_num_str,
                        'match_num_date': match_num_date,
                        'match_week': match_week,
                        'match_date': match_date,
                        'match_time': match_time,
                        'business_date': business_date,
                        'tax_date_no': tax_date_no,
                        'league_id': league_id,
                        'home_team_id': home_team_id,
                        'home_team_code': home_team_code,
                        'home_team_all_name': home_team_all_name,
                        'home_team_abb_name': home_team_abb_name,
                        'home_team_abb_en_name': home_team_abb_en_name,
                        'home_rank': home_rank,
                        'away_team_id': away_team_id,
                        'away_team_code': away_team_code,
                        'away_team_all_name': away_team_all_name,
                        'away_team_abb_name': away_team_abb_name,
                        'away_team_abb_en_name': away_team_abb_en_name,
                        'away_rank': away_rank,
                        'base_home_team_id': base_home_team_id,
                        'base_away_team_id': base_away_team_id,
                        'match_name': match_name,
                        'group_name': group_name,
                        'line_num': line_num,
                        'betting_single': betting_single,
                        'betting_all_up': betting_all_up
                    }
                    matches.append(match_info)
                    
                    # 查询数据库中是否已存在该比赛
                    existing_match = localdb.query(TczqMatch).filter_by(match_id=match_id).first()
                    
                    if not existing_match:
                        # 新增比赛信息
                        new_match = TczqMatch(
                            match_id=match_id,
                            match_num_str=match_num_str,
                            match_num_date=match_num_date,
                            match_week=match_week,
                            match_date=match_date,
                            match_time=match_time,
                            business_date=business_date,
                            tax_date_no=tax_date_no,
                            league_id=league_id,
                            home_team_id=home_team_id,
                            home_team_code=home_team_code,
                            home_team_all_name=home_team_all_name,
                            home_team_abb_name=home_team_abb_name,
                            home_team_abb_en_name=home_team_abb_en_name,
                            home_rank=home_rank,
                            away_team_id=away_team_id,
                            away_team_code=away_team_code,
                            away_team_all_name=away_team_all_name,
                            away_team_abb_name=away_team_abb_name,
                            away_team_abb_en_name=away_team_abb_en_name,
                            away_rank=away_rank,
                            base_home_team_id=base_home_team_id,
                            base_away_team_id=base_away_team_id,
                            match_name=match_name,
                            group_name=group_name,
                            line_num=line_num,
                            betting_single=betting_single,
                            betting_all_up=betting_all_up,
                            status=0  # 0-未开始
                        )
                        localdb.add(new_match, close=False)
                        logger.info(f"新增比赛: {match_week} {match_num_str} {home_team_abb_name} vs {away_team_abb_name}")
                    
                    # 处理赔率信息
                    self._process_match_odds(match_id, match)
                
        except Exception as e:
            logger.error(f"获取当前赛事信息失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return matches  # 返回比赛列表
    
    def _process_match_odds(self, match_id: int, match_data: Dict[str, str]) -> None:
        """
        处理比赛赔率信息
        
        Args:
            match_id: 比赛ID
            match_data: 完整的比赛数据（包含赔率信息）
        """
        # 获取各玩法赔率
        hhad_odds = match_data.get('hhad', {})
        had_odds = match_data.get('had', {})
        hafu_odds = match_data.get('hafu', {})
        crs_odds = match_data.get('crs', {})
        ttg_odds = match_data.get('ttg', {})
        
        # 获取当前时间
        from datetime import datetime
        now = datetime.now()
        
        # 获取比赛信息
        match = localdb.query(TczqMatch).filter_by(match_id=match_id).first()
        if not match:
            logger.error(f"未找到比赛ID为{match_id}的记录，跳过赔率历史记录")
            return
        
        logger.info(f"处理比赛 {match_id} 的赔率信息，match对象已获取")
        
        # 处理胜平负赔率
        if isinstance(had_odds, dict):
            h_odds = float(had_odds.get('h', 0))
            d_odds = float(had_odds.get('d', 0))
            a_odds = float(had_odds.get('a', 0))
            hf_odds = float(had_odds.get('hf', 0))
            af_odds = float(had_odds.get('af', 0))
            df_odds = float(had_odds.get('df', 0))
            
            # 解析更新时间
            update_date_str = had_odds.get('updateDate')
            update_time_str = had_odds.get('updateTime')
            if update_date_str and update_time_str:
                update_time_str = f"{update_date_str} {update_time_str}"
                update_time = datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                update_time = now

            # 查询最新的赔率记录
            latest_had = localdb.query(TczqHad).filter_by(match_id=match_id).order_by(TczqHad.update_time.desc()).first()

            # 检查赔率是否有变化
            odds_changed = False
            if latest_had:
                if (latest_had.h != h_odds or latest_had.d != d_odds or latest_had.a != a_odds or
                    latest_had.hf != hf_odds or latest_had.af != af_odds or latest_had.df != df_odds):
                    odds_changed = True
            else:
                # 没有记录，需要新增
                odds_changed = True

            if odds_changed:
                # 创建新的赔率记录
                new_had = TczqHad(
                    match_id=match_id,
                    h=h_odds,
                    d=d_odds,
                    a=a_odds,
                    hf=hf_odds,
                    af=af_odds,
                    df=df_odds,
                    update_time=update_time
                )
                localdb.add(new_had, close=False)
                logger.info(f"比赛 {match_id} 的胜平负赔率有变化，已新增记录")
        
        # 处理让球胜平负赔率
        if isinstance(hhad_odds, dict):
            goal_line_value = float(hhad_odds.get('goalLineValue', 0))
            h_odds = float(hhad_odds.get('h', 0))
            d_odds = float(hhad_odds.get('d', 0))
            a_odds = float(hhad_odds.get('a', 0))
            hf_odds = float(hhad_odds.get('hf', 0))
            af_odds = float(hhad_odds.get('af', 0))
            df_odds = float(hhad_odds.get('df', 0))
            
            # 解析更新时间
            update_date_str = hhad_odds.get('updateDate')
            update_time_str = hhad_odds.get('updateTime')
            if update_date_str and update_time_str:
                update_time_str = f"{update_date_str} {update_time_str}"
                update_time = datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                update_time = now
            
            # 查询最新的赔率记录
            latest_hhad = localdb.query(TczqHhad).filter_by(match_id=match_id).order_by(TczqHhad.update_time.desc()).first()

            # 检查赔率是否有变化
            odds_changed = False
            if latest_hhad:
                if (latest_hhad.goal_line_value != goal_line_value or latest_hhad.h != h_odds or 
                    latest_hhad.d != d_odds or latest_hhad.a != a_odds or latest_hhad.hf != hf_odds or 
                    latest_hhad.af != af_odds or latest_hhad.df != df_odds):
                    odds_changed = True
            else:
                # 没有记录，需要新增
                odds_changed = True

            if odds_changed:
                # 创建新的赔率记录
                new_hhad = TczqHhad(
                    match_id=match_id,
                    goal_line=str(goal_line_value),
                    goal_line_value=goal_line_value,
                    h=h_odds,
                    d=d_odds,
                    a=a_odds,
                    hf=hf_odds,
                    af=af_odds,
                    df=df_odds,
                    update_time=update_time
                )
                localdb.add(new_hhad, close=False)
                logger.info(f"比赛 {match_id} 的让球胜平负赔率有变化，已新增记录")
        
        # 处理半全场赔率
        if isinstance(hafu_odds, dict):
            hh_odds = float(hafu_odds.get('hh', 0))
            hd_odds = float(hafu_odds.get('hd', 0))
            ha_odds = float(hafu_odds.get('ha', 0))
            dh_odds = float(hafu_odds.get('dh', 0))
            dd_odds = float(hafu_odds.get('dd', 0))
            da_odds = float(hafu_odds.get('da', 0))
            ah_odds = float(hafu_odds.get('ah', 0))
            ad_odds = float(hafu_odds.get('ad', 0))
            aa_odds = float(hafu_odds.get('aa', 0))
            hhf_odds = float(hafu_odds.get('hhf', 0))
            hdf_odds = float(hafu_odds.get('ahd', 0))
            haf_odds = float(hafu_odds.get('haf', 0))
            dhf_odds = float(hafu_odds.get('dhf', 0))
            daf_odds = float(hafu_odds.get('daf', 0))
            ddf_odds = float(hafu_odds.get('ddf', 0))
            ahf_odds = float(hafu_odds.get('ahf', 0))
            adf_odds = float(hafu_odds.get('adf', 0))
            aaf_odds = float(hafu_odds.get('aaf', 0))
            
            # 解析更新时间
            update_date_str = hafu_odds.get('updateDate')
            update_time_str = hafu_odds.get('updateTime')
            if update_date_str and update_time_str:
                update_time_str = f"{update_date_str} {update_time_str}"
                update_time = datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                update_time = now
            
            # 查询最新的赔率记录
            latest_hafu = localdb.query(TczqHafu).filter_by(match_id=match_id).order_by(TczqHafu.update_time.desc()).first()

            # 检查赔率是否有变化
            odds_changed = False
            if latest_hafu:
                if (latest_hafu.hh != hh_odds or latest_hafu.hd != hd_odds or latest_hafu.ha != ha_odds or
                    latest_hafu.dh != dh_odds or latest_hafu.dd != dd_odds or latest_hafu.da != da_odds or
                    latest_hafu.ah != ah_odds or latest_hafu.ad != ad_odds or latest_hafu.aa != aa_odds or
                    latest_hafu.hhf != hhf_odds or latest_hafu.hdf != hdf_odds or latest_hafu.haf != haf_odds or
                    latest_hafu.dhf != dhf_odds or latest_hafu.daf != daf_odds or latest_hafu.ddf != ddf_odds or
                    latest_hafu.ahf != ahf_odds or latest_hafu.adf != adf_odds or latest_hafu.aaf != aaf_odds):
                    odds_changed = True
            else:
                # 没有记录，需要新增
                odds_changed = True

            if odds_changed:
                # 创建新的赔率记录
                new_hafu = TczqHafu(
                    match_id=match_id,
                    hh=hh_odds,
                    hd=hd_odds,
                    ha=ha_odds,
                    dh=dh_odds,
                    dd=dd_odds,
                    da=da_odds,
                    ah=ah_odds,
                    ad=ad_odds,
                    aa=aa_odds,
                    hhf=hhf_odds,
                    hdf=hdf_odds,
                    haf=haf_odds,
                    dhf=dhf_odds,
                    daf=daf_odds,
                    ddf=ddf_odds,
                    ahf=ahf_odds,
                    adf=adf_odds,
                    aaf=aaf_odds,
                    update_time=update_time
                )
                localdb.add(new_hafu, close=False)
                logger.info(f"比赛 {match_id} 的半全场赔率有变化，已新增记录")
        
        # 处理总进球数赔率
        if isinstance(ttg_odds, dict):
            s0_odds = float(ttg_odds.get('s0', 0))
            s1_odds = float(ttg_odds.get('s1', 0))
            s2_odds = float(ttg_odds.get('s2', 0))
            s3_odds = float(ttg_odds.get('s3', 0))
            s4_odds = float(ttg_odds.get('s4', 0))
            s5_odds = float(ttg_odds.get('s5', 0))
            s6_odds = float(ttg_odds.get('s6', 0))
            s7_odds = float(ttg_odds.get('s7', 0))
            s0f_odds = float(ttg_odds.get('s0f', 0))
            s1f_odds = float(ttg_odds.get('s1f', 0))
            s2f_odds = float(ttg_odds.get('s2f', 0))
            s3f_odds = float(ttg_odds.get('s3f', 0))
            s4f_odds = float(ttg_odds.get('s4f', 0))
            s5f_odds = float(ttg_odds.get('s5f', 0))
            s6f_odds = float(ttg_odds.get('s6f', 0))
            s7f_odds = float(ttg_odds.get('s7f', 0))
            
            # 解析更新时间
            update_date_str = ttg_odds.get('updateDate')
            update_time_str = ttg_odds.get('updateTime')
            if update_date_str and update_time_str:
                update_time_str = f"{update_date_str} {update_time_str}"
                update_time = datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                update_time = now

            # 查询最新的赔率记录
            latest_ttg = localdb.query(TczqTtg).filter_by(match_id=match_id).order_by(TczqTtg.update_time.desc()).first()

            # 检查赔率是否有变化
            odds_changed = False
            if latest_ttg:
                if (latest_ttg.s0 != s0_odds or latest_ttg.s1 != s1_odds or latest_ttg.s2 != s2_odds or
                    latest_ttg.s3 != s3_odds or latest_ttg.s4 != s4_odds or latest_ttg.s5 != s5_odds or
                    latest_ttg.s6 != s6_odds or latest_ttg.s7 != s7_odds or latest_ttg.s0f != s0f_odds or
                    latest_ttg.s1f != s1f_odds or latest_ttg.s2f != s2f_odds or latest_ttg.s3f != s3f_odds or
                    latest_ttg.s4f != s4f_odds or latest_ttg.s5f != s5f_odds or latest_ttg.s6f != s6f_odds or
                    latest_ttg.s7f != s7f_odds):
                    odds_changed = True
            else:
                # 没有记录，需要新增
                odds_changed = True

            if odds_changed:
                # 创建新的赔率记录
                new_ttg = TczqTtg(
                    match_id=match_id,
                    s0=s0_odds,
                    s1=s1_odds,
                    s2=s2_odds,
                    s3=s3_odds,
                    s4=s4_odds,
                    s5=s5_odds,
                    s6=s6_odds,
                    s7=s7_odds,
                    s0f=s0f_odds,
                    s1f=s1f_odds,
                    s2f=s2f_odds,
                    s3f=s3f_odds,
                    s4f=s4f_odds,
                    s5f=s5f_odds,
                    s6f=s6f_odds,
                    s7f=s7f_odds,
                    update_time=update_time
                )
                localdb.add(new_ttg, close=False)
                logger.info(f"比赛 {match_id} 的总进球数赔率有变化，已新增记录")
        
        # 处理比分赔率
        if isinstance(crs_odds, dict):
            # 解析更新时间
            update_date_str = crs_odds.get('updateDate')
            update_time_str = crs_odds.get('updateTime')
            if update_date_str and update_time_str:
                update_time_str = f"{update_date_str} {update_time_str}"
                update_time = datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                update_time = now
            
            # 构建TczqCrs对象的数据
            crs_data = {
                'match_id': match_id,
                's00s00': float(crs_odds.get('s0000', 0)),
                's00s01': float(crs_odds.get('s0001', 0)),
                's00s02': float(crs_odds.get('s0002', 0)),
                's00s03': float(crs_odds.get('s0003', 0)),
                's00s04': float(crs_odds.get('s0004', 0)),
                's00s05': float(crs_odds.get('s0005', 0)),
                's01s00': float(crs_odds.get('s0100', 0)),
                's01s01': float(crs_odds.get('s0101', 0)),
                's01s02': float(crs_odds.get('s0102', 0)),
                's01s03': float(crs_odds.get('s0103', 0)),
                's01s04': float(crs_odds.get('s0104', 0)),
                's01s05': float(crs_odds.get('s0105', 0)),
                's02s00': float(crs_odds.get('s0200', 0)),
                's02s01': float(crs_odds.get('s0201', 0)),
                's02s02': float(crs_odds.get('s0202', 0)),
                's02s03': float(crs_odds.get('s0203', 0)),
                's02s04': float(crs_odds.get('s0204', 0)),
                's02s05': float(crs_odds.get('s0205', 0)),
                's03s00': float(crs_odds.get('s0300', 0)),
                's03s01': float(crs_odds.get('s0301', 0)),
                's03s02': float(crs_odds.get('s0302', 0)),
                's03s03': float(crs_odds.get('s0303', 0)),
                's04s00': float(crs_odds.get('s0400', 0)),
                's04s01': float(crs_odds.get('s0401', 0)),
                's04s02': float(crs_odds.get('s0402', 0)),
                's05s00': float(crs_odds.get('s0500', 0)),
                's05s01': float(crs_odds.get('s0501', 0)),
                's05s02': float(crs_odds.get('s0502', 0)),
                's1sh': float(crs_odds.get('s1sh', 0)),
                's1sd': float(crs_odds.get('s1sd', 0)),
                's1sa': float(crs_odds.get('s1sa', 0)),
                'update_time': update_time
            }
            
            # 查询最新的赔率记录
            latest_crs = localdb.query(TczqCrs).filter_by(match_id=match_id).order_by(TczqCrs.update_time.desc()).first()

            # 检查赔率是否有变化
            odds_changed = False
            if latest_crs:
                # 比较所有赔率字段
                for key, value in crs_data.items():
                    if key != 'update_time' and hasattr(latest_crs, key) and getattr(latest_crs, key) != value:
                        odds_changed = True
                        break
            else:
                # 没有记录，需要新增
                odds_changed = True

            if odds_changed:
                # 创建新的赔率记录
                new_crs = TczqCrs(**crs_data)
                localdb.add(new_crs, close=False)
                logger.info(f"比赛 {match_id} 的比分赔率有变化，已新增记录")
        


    def get_match_results(self) -> None:
        """
        查询数据库，根据 status 以及开赛时间进行结果获取，并根据返回的数据记录到数据库中，同时更新状态
        """
        try:
            # 获取需要查询结果的比赛（status=0 且开赛时间小于当前时间）
            from datetime import datetime
            current_datetime = datetime.now()
            current_time = current_datetime.strftime('%H:%M:%S')
            current_date = current_datetime.strftime('%Y-%m-%d')
            
            print(f"当前时间: {current_time}")
            print(f"当前日期: {current_date}")
            print(f"完整当前时间: {current_datetime}")
            
            # 查询需要获取结果的比赛
            try:
                # 获取所有status=0的比赛
                all_matches = localdb.query(TczqMatch).filter_by(status=0).all()
                
                # 筛选出已经结束的比赛（比赛时间 < 当前时间）
                matches_to_check = []
                for match in all_matches:
                    try:
                        # 组合比赛日期和时间
                        match_datetime_str = f"{match.match_date} {match.match_time}"
                        match_datetime = datetime.strptime(match_datetime_str, '%Y-%m-%d %H:%M:%S')
                        
                        # 判断比赛是否已经结束
                        if match_datetime < current_datetime:
                            matches_to_check.append(match)
                            print(f"比赛 {match.match_week} {match.match_num_str} {match.home_team_abb_name} vs {match.away_team_abb_name} 已结束，需要获取结果")
                        else:
                            print(f"比赛 {match.match_week} {match.match_num_str} {match.home_team_abb_name} vs {match.away_team_abb_name} 尚未开始，跳过")
                    except Exception as e:
                        print(f"解析比赛时间失败: {str(e)}")
                        continue
                
                matches = matches_to_check
                print(f"\n总计查询到 {len(matches)} 场需要获取结果的比赛")
            except Exception as e:
                print(f"查询比赛失败: {str(e)}")
                import traceback
                traceback.print_exc()
                return
            
            if not matches:
                print("没有需要获取结果的比赛")
                return
            
            # 获取比赛结果
            match_ids = [str(match.match_id) for match in matches]
            if match_ids:
                print(f"需要获取结果的比赛ID: {match_ids}")
                # 由于API不支持批量获取，我们按日期范围获取
                try:
                    # 使用当前日期获取比赛结果
                    result_data = self.api.get_football_match_result(
                        match_date=current_date
                    )
                    # API直接返回比赛结果列表
                    match_result_list = result_data
                    print(f"获取到 {len(match_result_list)} 场比赛结果")
                    
                    # 处理比赛结果
                    for result in match_result_list:
                        print(f"比赛结果: {json.dumps(result, ensure_ascii=False)}")
                        match_id = int(result.get('matchId', 0))
                        if match_id:
                            # 更新比赛结果
                            self._update_match_result(match_id, result)
                except Exception as e:
                    print(f"获取比赛结果API调用失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                        
        except Exception as e:
            print(f"获取比赛结果失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _update_match_result(self, match_id: int, result_data: Dict[str, str]) -> None:
        """
        更新比赛结果到数据库
        
        Args:
            match_id: 比赛ID
            result_data: 比赛结果数据
        """
        try:
            # 获取比赛基本信息
            home_team = result_data.get('homeTeamName', '')
            away_team = result_data.get('awayTeamName', '')
            match_status = result_data.get('matchStatus', '')
            
            # 获取比分信息
            full_score = result_data.get('fullScore', '')
            half_score = result_data.get('halfScore', '')
            home_score = int(full_score.split(':')[0]) if ':' in full_score else 0
            away_score = int(full_score.split(':')[1]) if ':' in full_score else 0
            half_home_score = int(half_score.split(':')[0]) if ':' in half_score else 0
            half_away_score = int(half_score.split(':')[1]) if ':' in half_score else 0
            
            # 获取结果信息
            had_result = result_data.get('hadResult', '')
            hhad_result = result_data.get('hhadResult', '')
            hafu_result = result_data.get('hafuResult', '')
            ttg_result = result_data.get('ttgResult', '')
            crs_result = result_data.get('crsResult', '')
            
            # 更新比赛结果表
            existing_result = localdb.query(TczqResult).filter_by(match_id=match_id).first()
            if not existing_result:
                new_result = TczqResult(
                    match_id=match_id,
                    match_result_status=match_status,
                    pool_status='End' if match_status == 'End' else '',
                    result_status='End' if match_status == 'End' else '',
                    win_flag='H' if home_score > away_score else 'A' if home_score < away_score else 'D',
                    half_score=half_score,
                    full_score=full_score,
                    home_score=home_score,
                    away_score=away_score,
                    home_team=home_team,
                    away_team=away_team,
                    all_home_team=home_team,
                    all_away_team=away_team,
                    had_result=had_result,
                    hhad_result=hhad_result,
                    hafu_result=hafu_result,
                    ttg_result=ttg_result,
                    crs_result=crs_result
                )
                localdb.add(new_result, close=False)
            else:
                existing_result.match_result_status = match_status
                existing_result.pool_status = 'End' if match_status == 'End' else ''
                existing_result.result_status = 'End' if match_status == 'End' else ''
                existing_result.win_flag = 'H' if home_score > away_score else 'A' if home_score < away_score else 'D'
                existing_result.half_score = half_score
                existing_result.full_score = full_score
                existing_result.home_score = home_score
                existing_result.away_score = away_score
                existing_result.home_team = home_team
                existing_result.away_team = away_team
                existing_result.all_home_team = home_team
                existing_result.all_away_team = away_team
                existing_result.had_result = had_result
                existing_result.hhad_result = hhad_result
                existing_result.hafu_result = hafu_result
                existing_result.ttg_result = ttg_result
                existing_result.crs_result = crs_result
                localdb.update(existing_result)
            
            # 更新比赛主表状态
            match = localdb.query(TczqMatch).filter_by(match_id=match_id).first()
            if match:
                match.status = 1 if match_status == 'End' else 2  # 1-赛果已经记录，2-赛果获取失败
                localdb.update(match)
                
        except Exception as e:
            print(f"更新比赛结果失败 (match_id={match_id}): {str(e)}")


if __name__ == "__main__":
    spider = TczqSpider()
    
    # 获取当前赛事信息
    print("获取当前赛事信息...")
    spider.get_current_matches()
    
    # 获取比赛结果
    print("获取比赛结果...")
    spider.get_match_results()
    
    print("爬虫任务完成")