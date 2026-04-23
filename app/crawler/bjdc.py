# -*- coding: utf-8 -*-
"""
北京单场数据采集器
从 500 彩票网爬取北京单场比赛数据和赔率信息
"""
import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List
from bs4 import BeautifulSoup

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.common._utils import req_info
from app.log import bjdc_log as logger
from app.common._utils import handle_league_name, handle_team_name
from app.database import (
    localdb,
    League, Team,
    BjdcMatch,
    BjdcSpfOdds,
    BjdcTotalGoalOdds,
    BjdcScoreOdds,
    BjdcHalfTimeFullTimeOdds,
    BjdcUpDownOdds
)


class BjdcDataCollector:
    """北京单场数据采集器"""
    
    def __init__(self):
        """初始化数据采集器实例"""
        self.nowtime = datetime.now()
    
    def _get_weekday(self, date_str):
        """
        根据日期字符串计算星期
        :param date_str: 日期字符串，格式 'YYYY-MM-DD'
        :return: 星期字符串，如'周一'、'周二'
        """
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            # Python 的 weekday() 返回 0-6（周一到周日）
            return weekdays[date_obj.weekday()]
        except Exception as e:
            logger.error(f"计算星期失败：{e}")
            return ''
    
    def _try_parse_float(self, s):
        """尝试转换为浮点数"""
        try:
            return float(s)
        except:
            return None
    
    def _parse_value_str(self, value_str):
        """解析 tr 标签的 value 属性字符串"""
        try:
            dict_data = {}
            time_match = re.search(r"endTime:'(.*?)'", value_str)
            if time_match:
                # endTime 格式：'2026-04-03 16:25'
                dict_data['matchtime'] = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M')
            
            league_match = re.search(r"leagueName:'(.*?)'", value_str)
            if league_match:
                dict_data['leaguename'] = league_match.group(1)
            
            home_match = re.search(r"homeTeam:'(.*?)'", value_str)
            if home_match:
                dict_data['homename'] = home_match.group(1)
            
            away_match = re.search(r"guestTeam:'(.*?)'", value_str)
            if away_match:
                dict_data['awayname'] = away_match.group(1)
            
            index_match = re.search(r"index:'(.*?)'", value_str)
            if index_match:
                dict_data['id'] = index_match.group(1)
            
            # 获取日期（用于计算星期）
            schedule_date_match = re.search(r"scheduleDate:'(.*?)'", value_str)
            if schedule_date_match:
                dict_data['schedule_date'] = schedule_date_match.group(1)
            
            return dict_data
        except Exception as e:
            logger.error(f"解析 value 字符串失败：{e}")
            return None
    
    def _get_current_qishu(self, soup):
        """获取当前期数"""
        try:
            expect_select = soup.find('select', id='expect_select')
            if expect_select:
                selected_option = expect_select.find('option', selected=True)
                if selected_option:
                    qishu = selected_option.get('value')
                    logger.info(f'当前期数：{qishu}')
                    return qishu
        except Exception as e:
            logger.error(f"获取期数失败：{e}")
        return None
    
    def get_gamedata(self):
        """
        根据当前期数获取比赛数据，更新到数据库
        包括：1. 足球比赛数据 2. 足球进球赔率 3. 足球比分赔率
        """
        try:
            # 获取当前期数
            logger.info('开始获取北京单场数据...')
            soup = req_info("https://trade.500.com/bjdc/")
            if not soup:
                logger.error('联网爬取失败！')
                return False
            
            qishu = self._get_current_qishu(soup)
            if not qishu:
                logger.error('获取期数失败')
                return False
            
            # 1. 处理联赛和比赛数据
            logger.info(f'处理 {qishu} 期联赛和比赛数据...')
            tbodys_list = soup.find_all('tbody', id=lambda x: x is not None and x != '')
            for tbody in tbodys_list:
                self._process_league_and_match(tbody, qishu)
            
            # 2. 获取总进球数据
            logger.info(f'获取 {qishu} 期总进球数据...')
            zjq_soup = req_info('https://trade.500.com/bjdc/project_fq_jq.php', qishu)
            if zjq_soup:
                self._get_zjq(zjq_soup, qishu)
            else:
                logger.warning(f'获取 {qishu} 期总进球数据失败')
            
            # 3. 获取比分数据
            logger.info(f'获取 {qishu} 期比分数据...')
            bifen_soup = req_info('https://trade.500.com/bjdc/project_fq_bf.php', qishu)
            if bifen_soup:
                self._get_bifen(bifen_soup, qishu)
            else:
                logger.warning(f'获取 {qishu} 期比分数据失败')
            
            # 4. 获取半全场数据
            logger.info(f'获取 {qishu} 期半全场数据...')
            bq_soup = req_info('https://trade.500.com/bjdc/project_fq_bq.php', qishu)
            if bq_soup:
                self._get_bqc(bq_soup, qishu)
            else:
                logger.warning(f'获取 {qishu} 期半全场数据失败')
            
            # 5. 获取上下单双数据
            logger.info(f'获取 {qishu} 期上下单双数据...')
            ds_soup = req_info('https://trade.500.com/bjdc/project_fq_ds.php', qishu)
            if ds_soup:
                self._get_dxs(ds_soup, qishu)
            else:
                logger.warning(f'获取 {qishu} 期上下单双数据失败')
            
            logger.info('北京单场数据采集完成')
            return True
            
        except Exception as e:
            logger.error(f'采集异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _process_league_and_match(self, tbody, qishu):
        """
        处理联赛和比赛信息
        :param tbody: HTML 中的 tbody 元素
        :param qishu: 期数
        """
        try:
            new_match_count = 0  # 统计新增比赛数
            game_date = tbody.get('id').split('_')[0] if '_' in tbody.get('id', '') else ''
            
            for tr in tbody.find_all('tr', class_='vs_lines'):
                try:
                    fid = tr.get('fid')
                    valuestr = tr.get('value')
                    
                    # ========== 从 DOM 结构中提取队名和联赛名 ==========
                    td_list = tr.find_all('td')
                    if len(td_list) < 8:
                        logger.debug(f"表格列数不足，跳过：fid={fid}, cols={len(td_list)}")
                        continue
                    
                    # 1. 提取联赛名称（td[1]的<a>标签）
                    league_td = td_list[1]
                    league_link = league_td.find('a')
                    leaguename = league_link.text.strip() if league_link else None
                    
                    # 2. 提取主队名称（td[3]的<a>标签）
                    home_td = td_list[3]
                    home_link = home_td.find('a')
                    homename = home_link.text.strip() if home_link else None
                    
                    # 3. 提取客队名称（td[5]的<a>标签）
                    away_td = td_list[5]
                    away_link = away_td.find('a')
                    awayname = away_link.text.strip() if away_link else None
                    
                    # 4. 从 value 属性中提取其他信息（时间、场次等）
                    value_dict = self._parse_value_str(valuestr)
                    if not value_dict:
                        logger.debug(f"解析 value 失败，跳过：fid={fid}")
                        continue
                    
                    matchtime = value_dict.get('matchtime')
                    qsid = value_dict.get('id')
                    schedule_date = value_dict.get('schedule_date')
                                        
                    if not all([matchtime, homename, awayname, leaguename, qsid]):
                        logger.debug(f"比赛信息不完整，跳过：fid={fid}, home={homename}, away={awayname}, league={leaguename}")
                        continue
                                        
                    # 过滤时间（赛前 26 小时内）
                    if matchtime > self.nowtime + timedelta(hours=26):
                        logger.debug(f"比赛时间超过 26 小时，跳过：{matchtime}")
                        continue
                                        
                    # 计算星期
                    match_week = ''
                    if schedule_date:
                        match_week = self._get_weekday(schedule_date)
                    elif matchtime:
                        match_week = self._get_weekday(matchtime.strftime('%Y-%m-%d'))
                                        
                    # 1. 处理联赛 - 使用与 tczq 相同的策略
                    league = handle_league_name(leaguename, source_type='bjdc')
                    if not league:
                        logger.warning(f"联赛处理失败：{leaguename}")
                        continue
                                        
                    # 2. 处理球队
                    home_team = handle_team_name(homename, '', '', source_type='bjdc')
                    away_team = handle_team_name(awayname, '', '', source_type='bjdc')
                                        
                    if not home_team or not away_team:
                        logger.warning(f"球队处理失败：{homename} vs {awayname}")
                        continue
                                        
                    # 3. 查询是否已存在
                    existing_match = localdb.query(BjdcMatch).filter_by(match_id=int(fid)).first()
                                        
                    if not existing_match:
                        # 新增比赛（match_time 保存完整的日期时间）
                        new_match = BjdcMatch(
                            match_id=int(fid),
                            issue=qishu,
                            match_num=int(qsid),
                            match_num_str=f'{qishu}期{qsid}场',
                            match_week=match_week,
                            match_time=matchtime.replace(second=0, microsecond=0),  # 完整日期时间，秒数设为 0
                            league_id=league.id,
                            home_team_id=home_team.id,
                            away_team_id=away_team.id,
                            status=0
                        )
                        localdb.add(new_match, close=False)
                        new_match_count += 1
                        # logger.info(f'新增比赛：{homename} vs {awayname} (联赛:{leaguename})')  # 减少日志输出
                    else:
                        # 更新现有比赛的星期和时间
                        if match_week and not existing_match.match_week:
                            existing_match.match_week = match_week
                        # 更新时间（完整日期时间）
                        if matchtime and not existing_match.match_time:
                            existing_match.match_time = matchtime.replace(second=0, microsecond=0)
                        localdb.update(existing_match, close=False)
                        logger.debug(f'更新比赛：{homename} vs {awayname}')
                    
                    # 4. 提取并保存胜负平赔率
                    self._save_spf_odds(tr, int(fid))
                    
                except Exception as e:
                    logger.error(f'处理比赛失败：{e}')
                    import traceback
                    traceback.print_exc()
                    continue
                    
        except Exception as e:
            logger.error(f'处理联赛和比赛失败：{e}')
            import traceback
            traceback.print_exc()
        
        # 输出统计信息
        if new_match_count > 0:
            logger.info(f'本期共新增 {new_match_count} 场比赛')
    
    def _get_zjq(self, soup, qishu):
        """
        获取足球总进球赔率
        :param soup: 足球进球赔率页面的 BeautifulSoup 对象
        :param qishu: 足球进球赔率对应的期数
        """
        upcount = 0
        
        for tr in soup.find_all('tr', fid=lambda x: x is not None, class_='vs_lines'):
            try:
                fid = tr.get('fid')
                td_list = tr.select('td')
                
                if len(td_list) < 14:
                    logger.debug(f"总进球数据列数不足，跳过：fid={fid}, cols={len(td_list)}")
                    continue
                
                # 提取进球数赔率（索引 6-12 对应 0-6 球）
                goal_odds = []
                for i in range(6, 13):
                    goal_val = self._try_parse_float(td_list[i].text.strip())
                    goal_odds.append(goal_val)
                
                # 其他赔率
                goal_about = self._try_parse_float(td_list[13].text.strip())
                
                # 查询比赛并更新赔率
                match = localdb.query(BjdcMatch).filter_by(match_id=int(fid)).first()
                if match:
                    # 检查是否已有赔率记录
                    existing_odds = localdb.query(BjdcTotalGoalOdds).filter_by(match_id=int(fid)).first()
                    
                    if not existing_odds:
                        # 新增赔率记录
                        new_odds = BjdcTotalGoalOdds(
                            match_id=int(fid),
                            goal_0=goal_odds[0] or 0,
                            goal_1=goal_odds[1] or 0,
                            goal_2=goal_odds[2] or 0,
                            goal_3=goal_odds[3] or 0,
                            goal_4=goal_odds[4] or 0,
                            goal_5=goal_odds[5] or 0,
                            goal_6=goal_odds[6] or 0,
                            goal_about=goal_about or 0
                        )
                        localdb.add(new_odds, close=False)
                        logger.debug(f'新增总进球赔率：fid={fid}')
                    else:
                        # 更新现有赔率记录
                        for i, goal_val in enumerate(goal_odds):
                            if goal_val:
                                setattr(existing_odds, f'goal_{i}', goal_val)
                        if goal_about:
                            existing_odds.goal_about = goal_about
                        localdb.update(existing_odds, close=False)
                        logger.debug(f'更新总进球赔率：fid={fid}')
                    
                    upcount += 1
                else:
                    logger.debug(f"未找到比赛，跳过总进球赔率更新：fid={fid}")
                
            except Exception as e:
                logger.error(f'处理总进球赔率失败：{e}')
                import traceback
                traceback.print_exc()
                continue
        
        logger.info(f'总进球数据处理完成，更新{upcount}场')
    
    def _get_bifen(self, soup, qishu):
        """
        获取足球比分赔率
        :param soup: 足球比分赔率页面的 BeautifulSoup 对象
        :param qishu: 足球比分赔率对应的期数
        """
        upcount = 0
        
        for tr in soup.find_all('tr', fid=lambda x: x is not None, class_='vs_lines'):
            try:
                fid = tr.get('fid')
                
                # 查找下一个 tr（包含比分表）
                bifen_tr = tr.find_next_sibling('tr')
                if not bifen_tr:
                    logger.debug(f"未找到比分表行，跳过：fid={fid}")
                    continue
                
                bifen_tbody = bifen_tr.find('tbody')
                if not bifen_tbody:
                    logger.debug(f"未找到比分表 tbody，跳过：fid={fid}")
                    continue
                
                # 提取比分赔率
                spans = bifen_tbody.find_all('span')
                score_odds = {}
                
                for i in range(0, len(spans), 2):
                    if i + 1 < len(spans):
                        score_name = spans[i].text.strip()
                        odd_val = self._try_parse_float(spans[i+1].text.strip())
                        if score_name and odd_val:
                            score_odds[score_name] = odd_val
                
                # 查询比赛并更新赔率
                match = localdb.query(BjdcMatch).filter_by(match_id=int(fid)).first()
                if match:
                    # 检查是否已有赔率记录
                    existing_odds = localdb.query(BjdcScoreOdds).filter_by(match_id=int(fid)).first()
                    
                    if not existing_odds:
                        # 新增比分赔率记录
                        new_odds = BjdcScoreOdds(match_id=int(fid))
                        
                        # 解析比分赔率并设置到对象
                        for score_name, odd_val in score_odds.items():
                            if score_name == '胜其他':
                                new_odds.score_win_about = odd_val
                            elif score_name == '负其他':
                                new_odds.score_lose_about = odd_val
                            elif score_name == '平其他':
                                new_odds.score_draw_about = odd_val
                            else:
                                # 解析 "x:y" 格式的比分
                                parts = score_name.split(':')
                                if len(parts) == 2:
                                    home_goals = int(parts[0])
                                    away_goals = int(parts[1])
                                    field_name = f'score_{home_goals}_{away_goals}'
                                    if hasattr(new_odds, field_name):
                                        setattr(new_odds, field_name, odd_val)
                        
                        localdb.add(new_odds, close=False)
                        logger.debug(f'新增比分赔率：fid={fid}')
                    else:
                        # 更新现有赔率记录
                        for score_name, odd_val in score_odds.items():
                            if score_name == '胜其他':
                                existing_odds.score_win_about = odd_val
                            elif score_name == '负其他':
                                existing_odds.score_lose_about = odd_val
                            elif score_name == '平其他':
                                existing_odds.score_draw_about = odd_val
                            else:
                                # 解析 "x:y" 格式的比分
                                parts = score_name.split(':')
                                if len(parts) == 2:
                                    home_goals = int(parts[0])
                                    away_goals = int(parts[1])
                                    field_name = f'score_{home_goals}_{away_goals}'
                                    if hasattr(existing_odds, field_name):
                                        setattr(existing_odds, field_name, odd_val)
                        
                        localdb.update(existing_odds, close=False)
                        logger.debug(f'更新比分赔率：fid={fid}')
                    
                    upcount += 1
                else:
                    logger.debug(f"未找到比赛，跳过比分赔率更新：fid={fid}")
                
            except Exception as e:
                logger.error(f'处理比分赔率失败：{e}')
                import traceback
                traceback.print_exc()
                continue
        
        logger.info(f'比分数据处理完成，更新{upcount}场')
    
    def _get_bqc(self, soup, qishu):
        """
        获取足球半全场赔率
        :param soup: 足球半全场赔率页面的 BeautifulSoup 对象
        :param qishu: 足球半全场赔率对应的期数
        """
        upcount = 0
        
        for tr in soup.find_all('tr', fid=lambda x: x is not None, class_='vs_lines'):
            try:
                fid = tr.get('fid')
                td_list = tr.select('td')
                
                if len(td_list) < 15:
                    logger.debug(f"半全场数据列数不足，跳过：fid={fid}, cols={len(td_list)}")
                    continue
                
                # 提取半全场赔率（从合适的 td 开始）
                # 根据网页结构，半全场有 9 种赔率：胜胜、胜平、胜负、平胜、平平、平负、负胜、负平、负负
                bq_odds = []
                for i in range(6, 15):  # 索引 6-14 对应 9 种赔率
                    if i < len(td_list):
                        bq_val = self._try_parse_float(td_list[i].text.strip())
                        bq_odds.append(bq_val)
                
                # 查询比赛并更新赔率
                match = localdb.query(BjdcMatch).filter_by(match_id=int(fid)).first()
                if match and len(bq_odds) >= 9:
                    # 检查是否已有赔率记录
                    existing_odds = localdb.query(BjdcHalfTimeFullTimeOdds).filter_by(match_id=int(fid)).first()
                    
                    if not existing_odds:
                        # 新增半全场赔率记录
                        new_odds = BjdcHalfTimeFullTimeOdds(
                            match_id=int(fid),
                            half_win_full_win=bq_odds[0] or 0,      # 胜胜
                            half_win_full_draw=bq_odds[1] or 0,     # 胜平
                            half_win_full_lose=bq_odds[2] or 0,     # 胜负
                            half_draw_full_win=bq_odds[3] or 0,     # 平胜
                            half_draw_full_draw=bq_odds[4] or 0,    # 平平
                            half_draw_full_lose=bq_odds[5] or 0,    # 平负
                            half_lose_full_win=bq_odds[6] or 0,     # 负胜
                            half_lose_full_draw=bq_odds[7] or 0,    # 负平
                            half_lose_full_lose=bq_odds[8] or 0     # 负负
                        )
                        localdb.add(new_odds, close=False)
                        logger.debug(f'新增半全场赔率：fid={fid}')
                    else:
                        # 更新现有赔率记录
                        field_map = [
                            ('half_win_full_win', bq_odds[0]),
                            ('half_win_full_draw', bq_odds[1]),
                            ('half_win_full_lose', bq_odds[2]),
                            ('half_draw_full_win', bq_odds[3]),
                            ('half_draw_full_draw', bq_odds[4]),
                            ('half_draw_full_lose', bq_odds[5]),
                            ('half_lose_full_win', bq_odds[6]),
                            ('half_lose_full_draw', bq_odds[7]),
                            ('half_lose_full_lose', bq_odds[8])
                        ]
                        for field_name, value in field_map:
                            if value:
                                setattr(existing_odds, field_name, value)
                        localdb.update(existing_odds, close=False)
                        logger.debug(f'更新半全场赔率：fid={fid}')
                    
                    upcount += 1
                else:
                    logger.debug(f"未找到比赛或赔率数据不足，跳过半全场赔率更新：fid={fid}, odds_count={len(bq_odds)}")
                
            except Exception as e:
                logger.error(f'处理半全场赔率失败：{e}')
                import traceback
                traceback.print_exc()
                continue
        
        logger.info(f'半全场数据处理完成，更新{upcount}场')
    
    def _get_dxs(self, soup, qishu):
        """
        获取足球上下单双赔率
        :param soup: 足球上下单双赔率页面的 BeautifulSoup 对象
        :param qishu: 足球上下单双赔率对应的期数
        """
        upcount = 0
        
        for tr in soup.find_all('tr', fid=lambda x: x is not None, class_='vs_lines'):
            try:
                fid = tr.get('fid')
                td_list = tr.select('td')
                
                if len(td_list) < 10:
                    logger.debug(f"上下单双数据列数不足，跳过：fid={fid}, cols={len(td_list)}")
                    continue
                
                # 提取上下单双赔率（4 种：上 + 单、上 + 双、下 + 单、下 + 双）
                dxs_odds = []
                for i in range(6, 10):  # 索引 6-9 对应 4 种赔率
                    if i < len(td_list):
                        dxs_val = self._try_parse_float(td_list[i].text.strip())
                        dxs_odds.append(dxs_val)
                
                # 查询比赛并更新赔率
                match = localdb.query(BjdcMatch).filter_by(match_id=int(fid)).first()
                if match and len(dxs_odds) >= 4:
                    # 检查是否已有赔率记录
                    existing_odds = localdb.query(BjdcUpDownOdds).filter_by(match_id=int(fid)).first()
                    
                    if not existing_odds:
                        # 新增上下单双赔率记录
                        new_odds = BjdcUpDownOdds(
                            match_id=int(fid),
                            up_single=dxs_odds[0] or 0,     # 上 + 单
                            up_double=dxs_odds[1] or 0,     # 上 + 双
                            down_single=dxs_odds[2] or 0,   # 下 + 单
                            down_double=dxs_odds[3] or 0    # 下 + 双
                        )
                        localdb.add(new_odds, close=False)
                        logger.debug(f'新增上下单双赔率：fid={fid}')
                    else:
                        # 更新现有赔率记录
                        field_map = [
                            ('up_single', dxs_odds[0]),
                            ('up_double', dxs_odds[1]),
                            ('down_single', dxs_odds[2]),
                            ('down_double', dxs_odds[3])
                        ]
                        for field_name, value in field_map:
                            if value:
                                setattr(existing_odds, field_name, value)
                        localdb.update(existing_odds, close=False)
                        logger.debug(f'更新上下单双赔率：fid={fid}')
                    
                    upcount += 1
                else:
                    logger.debug(f"未找到比赛或赔率数据不足，跳过上下单双赔率更新：fid={fid}, odds_count={len(dxs_odds)}")
                
            except Exception as e:
                logger.error(f'处理上下单双赔率失败：{e}')
                import traceback
                traceback.print_exc()
                continue
        
        logger.info(f'上下单双数据处理完成，更新{upcount}场')
    
    def _save_spf_odds(self, tr, match_id):
        """
        保存胜负平赔率
        :param tr: HTML tr 元素
        :param match_id: 比赛 ID
        """
        try:
            td_list = tr.find_all('td')
            
            # 检查是否有足够的 td 元素
            if len(td_list) < 11:
                logger.debug(f"胜负平数据列数不足，跳过：match_id={match_id}, cols={len(td_list)}")
                return
            
            # 提取胜负平赔率（td[8], td[9], td[10]）
            win_odd = self._try_parse_float(td_list[8].text.strip())
            draw_odd = self._try_parse_float(td_list[9].text.strip())
            lose_odd = self._try_parse_float(td_list[10].text.strip())
            
            # 如果赔率为空，跳过
            if not all([win_odd, draw_odd, lose_odd]):
                logger.debug(f"胜负平赔率不完整，跳过：match_id={match_id}")
                return
            
            # 查询比赛是否存在
            match = localdb.query(BjdcMatch).filter_by(match_id=match_id).first()
            if not match:
                logger.debug(f"未找到比赛，跳过胜负平赔率更新：match_id={match_id}")
                return
            
            # 检查是否已有赔率记录
            existing_odds = localdb.query(BjdcSpfOdds).filter_by(match_id=match_id).first()
            
            if not existing_odds:
                # 新增赔率记录
                new_odds = BjdcSpfOdds(
                    match_id=match_id,
                    win_pl=win_odd,
                    draw_pl=draw_odd,
                    lose_pl=lose_odd
                )
                localdb.add(new_odds, close=False)
                # logger.info(f'新增胜负平赔率：match_id={match_id}, 主胜={win_odd}, 平={draw_odd}, 客胜={lose_odd}')  # 减少日志输出
            else:
                # 记录赔率变化（如果需要）
                self._log_odds_change(
                    match_id=match_id,
                    odds_table='bjdc_spf_odds',
                    odds_record_id=existing_odds.id,
                    new_data={
                        'win_pl': win_odd,
                        'draw_pl': draw_odd,
                        'lose_pl': lose_odd
                    },
                    fields=['win_pl', 'draw_pl', 'lose_pl']
                )
                
                # 更新现有赔率记录
                existing_odds.win_pl = win_odd
                existing_odds.draw_pl = draw_odd
                existing_odds.lose_pl = lose_odd
                localdb.update(existing_odds, close=False)
                logger.debug(f'更新胜负平赔率：match_id={match_id}')
                
        except Exception as e:
            logger.error(f'处理胜负平赔率失败：{e}')
            import traceback
            logger.error(traceback.format_exc())
    
    def _log_odds_change(self, match_id, odds_table, odds_record_id, new_data, fields):
        """
        记录赔率变化日志（带阈值判断）
        
        Args:
            match_id: 比赛ID
            odds_table: 赔率表名 (如 bjdc_spf_odds)
            odds_record_id: 赔率记录ID
            new_data: 新数据字典
            fields: 需要检查变化的字段列表
        """
        from app.database import BjdcOddsChangeLog
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
                    sport_type='bjdc',  # 北京单场
                    threshold=0.1  # 波动阈值 ±0.1
                )
                
                if should_log:
                    # 获取比赛信息用于日志输出
                    match_info = ""
                    try:
                        from app.database import BjdcMatch
                        match = localdb.query(BjdcMatch).filter_by(match_id=match_id).first()
                        if match:
                            home_name = match.home_team.team_full_name if match.home_team else '未知'
                            away_name = match.away_team.team_full_name if match.away_team else '未知'
                            match_num = match.match_num or ''
                            match_info = f"[{match_num} {home_name} vs {away_name}] "
                    except Exception:
                        pass
                    
                    change_log = BjdcOddsChangeLog(
                        match_id=match_id,
                        odds_table=odds_table,
                        odds_record_id=odds_record_id,
                        odds_field=field,
                        old_value=float(current_value) if current_value != 0.0 else 0.0,
                        new_value=float(new_value),
                        change_time=datetime.now()
                    )
                    localdb.add(change_log, close=False)
                    # logger.info(f"✓ {match_info}北单{field}赔率变化: {current_value:.3f} -> {new_value:.3f} (波动{diff:+.3f})")  # 减少日志输出，只记录统计
                else:
                    logger.debug(f"⊘ 忽略小幅波动: {odds_table}.{field} "
                               f"{current_value:.3f} -> {new_value:.3f} (波动{diff:+.3f})")
        except Exception as e:
            logger.error(f"记录北单赔率变化失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def collect_matches(self) -> bool:
        """采集北京单场比赛数据"""
        return self.get_gamedata()
    
    def get_matches_with_odds(self) -> list:
        """获取比赛数据（带赔率）"""
        try:
            self.get_gamedata()
            
            # 返回数据库中的比赛
            matches = localdb.query(BjdcMatch).limit(100).all()
            result = []
            for m in matches:
                match_dict = {
                    'id': m.id,
                    'match_id': m.match_id,
                    'issue': m.issue,
                    'match_num': m.match_num,
                    'match_date': m.match_date,
                    'match_time': m.match_time.strftime('%Y-%m-%d %H:%M:%S') if m.match_time else None,
                    'home_team_id': m.home_team_id,
                    'away_team_id': m.away_team_id
                }
                result.append(match_dict)
            
            return result
            
        except Exception as e:
            logger.error(f'获取比赛数据异常：{e}')
            import traceback
            logger.error(traceback.format_exc())
            return []
