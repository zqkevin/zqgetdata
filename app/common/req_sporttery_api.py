# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.log.logger import log


class SportteryAPI:
    """
    中国体育彩票竞彩API调用类
    提供各种接口的调用和数据清洗整理功能
    """
    
    Football_BASE_URL = "https://webapi.sporttery.cn/gateway/uniform/football/"
    Basketball_BASE_URL = "https://webapi.sporttery.cn/gateway/uniform/basketball/"
    Digital_BASE_URL = "https://webapi.sporttery.cn/gateway/lottery/"
    
    def __init__(self):
        """
        初始化API客户端
        
        Args:
            headers: 自定义请求头，如不提供则使用默认请求头
        """
        self.session = requests.Session()
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate',  # 移除 br，避免Brotli压缩问题
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.sporttery.cn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.sporttery.cn/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        self.session.headers.update(self.headers)
    
    def _request(self, retype: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送请求的通用方法
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            清洗整理后的JSON响应数据
            
        Raises:
            Exception: 当请求失败时抛出异常
        """
        if retype == 'football':
            if endpoint == 'result':
                url = f"{self.Football_BASE_URL}getUniformMatchResultV1.qry"
            elif endpoint == 'info':
                url = f"{self.Football_BASE_URL}getMatchCalculatorV1.qry"
            elif endpoint == 'oddshistory':
                url = f"{self.Football_BASE_URL}getOddsHistoryV1.qry"
            elif endpoint == 'searchodds':
                url = f"{self.Football_BASE_URL}searchOddsV1.qry"
            else:
                raise ValueError(f"未知的足球接口: {endpoint}")
        elif retype == 'basketball':
            if endpoint == 'result':
                url = f"{self.Basketball_BASE_URL}getMatchResultV1.qry"
            elif endpoint == 'resultV2':
                url = f"{self.Basketball_BASE_URL}getUniformMatchResultV2.qry"
            elif endpoint == 'info':
                url = f"{self.Basketball_BASE_URL}getMatchCalculatorV1.qry"
            elif endpoint == 'list':
                url = f"{self.Basketball_BASE_URL}getMatchListV2.qry"
            else:
                raise ValueError(f"未知的篮球接口: {endpoint}")
        elif retype == 'digital':
            if endpoint == 'draw':
                url = f"{self.Digital_BASE_URL}getDigitalDrawInfoV1.qry"
            elif endpoint == 'history':
                url = f"{self.Digital_BASE_URL}getHistoryPageListV1.qry"
            else:
                raise ValueError(f"未知的数字彩接口: {endpoint}")
        else:
            raise ValueError(f"未知的API类型: {retype}")
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 检查响应是否成功
            if data.get('errorCode') != '0' or not data.get('success'):
                raise Exception(f"API请求失败: {data.get('errorMessage', '未知错误')}")
            
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求错误: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析错误: {str(e)}")
    
    def get_football_match_list(self, pool_codes: List[str] = None, channel: str = "c") -> Dict[str, Any]:
        """
        获取足球比赛列表
        
        Args:
            pool_codes: 投注玩法代码列表，如['hhad', 'had']
            channel: 渠道标识，默认为'c'

        Returns:
            包含比赛列表、日期列表和联赛列表的字典
        """
        if pool_codes is None:
            pool_codes = ['hhad', 'had', 'hafu', 'crs', 'ttg']
            
        params = {
            'poolCode': ','.join(pool_codes),
            'channel': channel
        }
        
        data = self._request(retype='football', endpoint='info', params=params)
        
        # 处理返回的数据
        match_info_list = data.get('value', {}).get('matchInfoList', [])
        match_date_list = data.get('value', {}).get('matchDateList', [])
        league_list = data.get('value', {}).get('leagueList', [])
        
        return {
            'match_info_list': match_info_list,
            'match_date_list': match_date_list,
            'league_list': league_list
        }
        
    def _format_date(self, date_str: str) -> Optional[str]:
        """
        将输入日期字符串格式化为标准的YYYY-MM-DD格式
        
        Args:
            date_str: 输入的日期字符串
            
        Returns:
            格式化后的日期字符串或None
        """
        if not date_str:
            return None
        
        # 尝试不同的日期格式
        formats_to_try = [
            '%Y-%m-%d',  # 2024-01-01
            '%Y/%m/%d',  # 2024/01/01
            '%Y.%m.%d',  # 2024.01.01
            '%d-%m-%Y',  # 01-01-2024
            '%d/%m/%Y',  # 01/01/2024
            '%d.%m.%Y',  # 01.01.2024
            '%Y%m%d'     # 20240101
        ]
        
        for fmt in formats_to_try:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # 如果所有格式都失败，返回None
        log.error(f"无法解析日期格式: {date_str}")
        return None
    
    def get_football_match_result(self, match_begin_date: str = None, match_end_date: str = None) -> list:
        """
        获取足球比赛赛果信息
        
        Args:
            match_begin_date: 比赛开始日期，格式为YYYY-MM-DD
            match_end_date: 比赛结束日期，格式为YYYY-MM-DD
            channel: 渠道标识，默认为'c'
            page_size: 每页条数
            page_no: 页码
            is_fix: 是否固定
            match_page: 比赛页码
            pc_or_wap: PC或WAP标识
            
        Returns:
            足球比赛赛果信息
        """
        params = {
            'pageSize': 30,
            'pageNo': 1,
            'isFix': 0,
            'matchPage': 1,
            'pcOrWap': 1
        }
        
        # 添加比赛日期参数（如果提供）
        if match_begin_date is not None:
            formatted_begin = self._format_date(match_begin_date)
            if formatted_begin:
                params['matchBeginDate'] = formatted_begin
        if match_end_date is not None:
            formatted_end = self._format_date(match_end_date)
            if formatted_end:
                params['matchEndDate'] = formatted_end
            
        data = self._request(retype='football', endpoint='result', params=params)
        value = data.get('value', {})
        total = value.get('total', 0)
        pages = value.get('pages', 0)
        log.info(f"获取足球比赛赛果信息，共{total}条，{pages}页")
        pageNo = params.get('pageNo', 1)
        results = value.get('matchResult', [])
        while pageNo < pages:
            pageNo += 1
            params['pageNo'] = pageNo
            data = self._request(retype='football', endpoint='result', params=params)
            value = data.get('value', {})
            match_results = value.get('matchResult', [])
            results.extend(match_results)


        # 从返回数据中提取比赛结果列表并标准化
        standardized_results = []
        for result in results:
            # 解析比分信息
            match_result_status = result.get('matchResultStatus')
            pool_status = result.get('poolStatus')
            win_flag = result.get('winFlag')
            
            # 判断比赛是否已结束（多种条件确保覆盖所有情况）
            is_match_finished = (match_result_status == '2' or 
                               pool_status == 'Payout' or 
                               (win_flag and win_flag not in ['N', '']))
            
            if is_match_finished:
                # 解析最终比分
                final_score = result.get('sectionsNo999', '')
                if final_score and ':' in final_score:
                    try:
                        home_score, away_score = final_score.split(':')
                    except ValueError:
                        # 处理比分格式异常
                        home_score, away_score = 'N/A', 'N/A'
                elif final_score == '取消':
                    home_score, away_score = '取消', '取消'
                else:
                    home_score, away_score = 'N/A', 'N/A'
                
                # 解析半场比分
                half_score = result.get('sectionsNo1', '')
                if half_score and ':' in half_score:
                    try:
                        half_home_score, half_away_score = half_score.split(':')
                    except ValueError:
                        # 处理比分格式异常
                        half_home_score, half_away_score = 'N/A', 'N/A'
                else:
                    half_home_score, half_away_score = 'N/A', 'N/A'
            else:
                # 比赛未结束或取消
                match_status = result.get('resultStatus', '')
                final_score = result.get('sectionsNo999', '')
                if match_status == '取消' or final_score == '取消':
                    home_score, away_score = '取消', '取消'
                    half_home_score, half_away_score = '取消', '取消'
                else:
                    home_score, away_score = 'N/A', 'N/A'
                    half_home_score, half_away_score = 'N/A', 'N/A'
                
            standardized = {
                'matchId': result.get('matchId'),
                'matchNum': result.get('matchNum'),
                'matchDate': result.get('matchDate'),
                'homeTeam': result.get('homeTeam'),
                'allHomeTeam': result.get('allHomeTeam'),
                'awayTeam': result.get('awayTeam'),
                'allAwayTeam': result.get('allAwayTeam'),
                'homeScore': home_score,
                'awayScore': away_score,
                'halfHomeScore': half_home_score,
                'halfAwayScore': half_away_score,
                'matchResultStatus': result.get('matchResultStatus'),
                'leagueName': result.get('leagueName'),
                'leagueNameAbbr': result.get('leagueNameAbbr')
            }
            standardized_results.append(standardized)
            
        return standardized_results
    
    def get_basketball_match_list(self, client_code: str = "3001") -> pd.DataFrame:
        """
        获取篮球比赛列表
        
        Args:
            client_code: 客户端代码，默认为3001
            
        Returns:
            比赛列表的DataFrame
        """
        params = {'clientCode': client_code}
        
        data = self._request(retype='basketball', endpoint='list', params=params)
        
        # 处理返回的数据
        match_list = data.get('value', {}).get('matchInfoList', [])
        if match_list:
            # 转换为DataFrame并进行基本清洗
            df = pd.DataFrame(match_list)
            
            # 处理日期时间字段
            if 'matchTime' in df.columns:
                df['matchTime'] = pd.to_datetime(df['matchTime'], errors='coerce')
            
            # 处理数字字段
            numeric_columns = ['homeScore', 'awayScore', 'letNum']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        
        # 如果比赛列表接口返回空，尝试从比赛计算器接口获取比赛信息
        calculator_data = self.get_basketball_match_calculator(['hilo'])
        match_info_list = calculator_data.get('matchInfoList', [])
        
        if match_info_list:
            # 从比赛计算器数据中提取比赛列表
            match_list = []
            for match_info in match_info_list:
                # 检查是否有subMatchList字段（这是实际包含比赛记录的地方）
                sub_match_list = match_info.get('subMatchList', [])
                
                if sub_match_list:
                    # 处理subMatchList中的每个比赛记录
                    for sub_match in sub_match_list:
                        match_data = {
                            'matchId': sub_match.get('matchId'),
                            'matchNum': sub_match.get('matchNum'),
                            'matchNumStr': sub_match.get('matchNumStr'),
                            'matchNumDate': sub_match.get('matchNumDate'),
                            'matchWeek': sub_match.get('matchWeek'),
                            'matchDate': sub_match.get('matchDate'),
                            'matchTime': sub_match.get('matchTime'),
                            'leagueId': sub_match.get('leagueId'),
                            'leagueName': sub_match.get('leagueName'),
                            'homeTeamName': sub_match.get('homeTeamName', sub_match.get('homeTeamAbbName', '')),
                            'awayTeamName': sub_match.get('awayTeamName', sub_match.get('awayTeamAbbName', '')),
                            'matchStatus': sub_match.get('matchStatus'),
                            'sellStatus': 1 if sub_match.get('poolStatus') == 'Selling' else 0
                        }
                        match_list.append(match_data)
                else:
                    # 兼容原来的格式
                    match_data = {
                        'matchId': match_info.get('matchId'),
                        'matchNum': match_info.get('matchNum'),
                        'matchNumStr': match_info.get('matchNumStr'),
                        'matchNumDate': match_info.get('matchNumDate'),
                        'matchWeek': match_info.get('matchWeek'),
                        'matchDate': match_info.get('matchDate'),
                        'matchTime': match_info.get('matchTime'),
                        'leagueId': match_info.get('leagueId'),
                        'leagueName': match_info.get('leagueName'),
                        'homeTeamName': match_info.get('homeTeamName'),
                        'awayTeamName': match_info.get('awayTeamName'),
                        'matchStatus': match_info.get('matchStatus'),
                        'sellStatus': 1 if match_info.get('poolStatus') == 'Selling' else 0
                    }
                    match_list.append(match_data)
            
            if match_list:
                df = pd.DataFrame(match_list)
                # 过滤掉matchId为None的记录
                df = df.dropna(subset=['matchId'])
                
                # 处理日期时间字段
                if 'matchTime' in df.columns:
                    df['matchTime'] = pd.to_datetime(df['matchTime'], errors='coerce')
                
                # 处理数字字段
                numeric_columns = ['homeScore', 'awayScore', 'letNum']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                return df
        
        return pd.DataFrame()
    
    def get_football_match_odds_history(self, pool_codes=None, matchId: str = None) -> Dict[str, Any]:
        """
        获取足球比赛赔率历史记录
        
        Args:
            pool_codes: 投注玩法代码列表，如['hhad', 'had']
            matchId: 比赛ID
            
        Returns:
            清洗整理后的赔率历史记录
        """
        if matchId is None:
            log.error("获取足球比赛赔率历史记录失败: matchId不能为空")
            return {}
        if pool_codes is None:
            pool_codes = ['hhad', 'had']

        params = {
            'poolCode': ','.join(pool_codes),
            'matchId': matchId
        }
        
        data = self._request(retype='football', endpoint='oddshistory', params=params)
        if data.get('errorCode') != "0":
            log.error(f"获取足球比赛投注计算信息失败: {data.get('msg', '未知错误')}")
            return {}

        histroy_data = data.get('value', {})
        

        
        return histroy_data
    

    def get_basketball_match_calculator(self, pool_codes: List[str], channel: str = "c") -> Dict[str, Any]:
        """
        获取篮球比赛投注计算信息
        
        Args:
            pool_codes: 投注玩法代码列表，如['hilo', 'spf']
            channel: 渠道标识，默认为'c'（客户端）
            
        Returns:
            清洗整理后的投注计算信息
        """
        params = {
            'poolCode': ','.join(pool_codes),
            'channel': channel
        }
        
        data = self._request(retype='basketball', endpoint='info', params=params)
        return data.get('value', {})
    
    def get_basketball_match_result(self, match_date: str, channel: str = "c") -> Dict[str, Any]:
        """
        获取篮球比赛赛果信息（单日期查询，已废弃）
        
        Args:
            match_date: 比赛日期，格式为YYYY-MM-DD
            channel: 渠道标识，默认为'c'（客户端）
            
        Returns:
            清洗整理后的赛果信息
        """
        # 格式化比赛日期
        formatted_date = self._format_date(match_date)
        if not formatted_date:
            log.error(f"无效的比赛日期: {match_date}")
            return {}
            
        params = {
            'matchDate': formatted_date,
            'channel': channel
        }
        
        data = self._request(retype='basketball', endpoint='result', params=params)
        return data.get('value', {})
    
    def get_basketball_match_results(self, match_begin_date: str = None, match_end_date: str = None) -> list:
        """
        获取篮球比赛赛果信息（支持日期范围查询）
        
        Args:
            match_begin_date: 比赛开始日期，格式为YYYY-MM-DD
            match_end_date: 比赛结束日期，格式为YYYY-MM-DD
            
        Returns:
            篮球比赛赛果列表
        """
        params = {
            'pageSize': 30,
            'pageNo': 1,
            'isFix': 0,
            'leagueId': ''
        }
        
        # 添加比赛日期参数（如果提供）
        if match_begin_date is not None:
            formatted_begin = self._format_date(match_begin_date)
            if formatted_begin:
                params['matchBeginDate'] = formatted_begin
        if match_end_date is not None:
            formatted_end = self._format_date(match_end_date)
            if formatted_end:
                params['matchEndDate'] = formatted_end
        
        # 使用 _request 方法获取第一页数据
        data = self._request(retype='basketball', endpoint='resultV2', params=params)
        value = data.get('value', {})
        total = value.get('total', 0)
        pages = value.get('pages', 0)
        log.info(f"获取篮球比赛赛果信息，共{total}条，{pages}页")
        
        # 获取第一页数据
        pageNo = params.get('pageNo', 1)
        results = value.get('matchResult', [])
        
        # 如果有多个页面，继续获取
        while pageNo < pages:
            pageNo += 1
            params['pageNo'] = pageNo
            data = self._request(retype='basketball', endpoint='resultV2', params=params)
            value = data.get('value', {})
            match_results = value.get('matchResult', [])
            results.extend(match_results)
        
        # 标准化返回数据
        standardized_results = []
        for result in results:
            # 解析比分
            final_score = result.get('finalScore', '')
            if final_score and '-' in final_score:
                try:
                    home_score, away_score = final_score.split('-')
                    home_score = int(home_score.strip())
                    away_score = int(away_score.strip())
                except (ValueError, AttributeError):
                    home_score, away_score = 0, 0
            else:
                home_score, away_score = 0, 0
            
            standardized = {
                'matchId': result.get('matchId'),
                'matchNum': result.get('matchNum'),
                'matchNumStr': result.get('matchNumStr'),
                'matchDate': result.get('matchDate'),
                'matchTime': result.get('matchTime'),
                'homeTeam': result.get('homeTeam'),
                'allHomeTeam': result.get('allHomeTeam'),
                'awayTeam': result.get('awayTeam'),
                'allAwayTeam': result.get('allAwayTeam'),
                'homeTeamId': result.get('homeTeamId'),
                'awayTeamId': result.get('awayTeamId'),
                'homeScore': home_score,
                'awayScore': away_score,
                'leagueName': result.get('leagueName'),
                'leagueNameAbbr': result.get('leagueNameAbbr'),
                'leagueId': result.get('leagueId'),
                'status': result.get('status'),
                'poolStatus': result.get('poolStatus')
            }
            standardized_results.append(standardized)
        
        return standardized_results
    
    def search_football_some_odds(self, match_id: str = None, h: str = None, a: str = None, d: str = None, league_id: str = None, homeTeamId: str = None, awayTeamId: str = None) -> Dict[str, Any]:
        """
        获取指定比赛的赔率信息
        
        Args:
            match_id: 比赛ID
            h: 参数h
            a: 参数a
            d: 参数d
            league_id: 联赛ID
            homeTeamId: 主队ID
            awayTeamId: 客队ID
            channel: 渠道标识，默认为'c'
            type_: 玩法类型，默认为空
            single: 是否单关，0为否，1为是
            
        Returns:
            清洗整理后的赔率信息
        """
        # 固定包含的参数
        params = {
            'channel': "c",
            'type': "",
            'single': 0
        }
        
        # 动态添加非None参数
        if match_id is not None:
            params['matchId'] = match_id
        if h is not None:
            params['h'] = h
        if a is not None:
            params['a'] = a
        if d is not None:
            params['d'] = d
        if league_id is not None:
            params['league_id'] = league_id
        if homeTeamId is not None:
            params['homeTeamId'] = homeTeamId
        if awayTeamId is not None:
            params['awayTeamId'] = awayTeamId
        data = self._request(retype='football', endpoint='searchodds', params=params)
        same_data = data.get('value', {})
        return same_data
    
    def get_support_rate(self, match_id: str = None) -> Dict[str, Any]:
        """
        获取比赛投注支持率信息
        
        Args:
            match_id: 比赛ID（可选）
            
        Returns:
            清洗整理后的支持率信息
        """
        # 注意：此接口的实际URL需要确认，暂时使用通用请求方式
        # 如果这个接口不存在或URL不正确，可能需要从网页抓取支持率数据
        log.warning("get_support_rate 接口可能不可用，建议从网页抓取支持率数据")
        return {}
    
    def get_digital_lottery_info(self, lottery_type: str, term_flag: int = 0) -> Dict[str, Any]:
        """
        获取数字彩票的开奖信息
        
        Args:
            lottery_type: 彩票类型
            term_flag: 期号标识，0表示最近一期
            
        Returns:
            数字彩票开奖信息
        """
        # 彩票类型与代码的映射
        lottery_code_map = {
            'pl3': '35',
            'pl5': '350133',
            'dlt': '85',
            'qxc': '04'
        }
        
        # 获取彩票类型代码
        lottery_code = lottery_code_map.get(lottery_type)
        if not lottery_code:
            raise ValueError(f"未知的彩票类型: {lottery_type}")
        
        params = {
            'param': f"{lottery_code},{term_flag}",
            'isVerify': 0
        }
        
        data = self._request(retype='digital', endpoint='draw', params=params)
        return data.get('value', {})
    
    def get_digital_lottery_history(self, lottery_type: str, page_no: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """
        获取数字彩票历史开奖数据
        
        Args:
            lottery_type: 彩票类型 (pl3, pl5, dlt, qxc)
            page_no: 页码，默认第 1 页
            page_size: 每页条数，默认 30 条
            
        Returns:
            历史开奖数据
        """
        # 彩票类型与代码的映射
        lottery_code_map = {
            'pl3': '35',
            'pl5': '350133',
            'dlt': '85',
            'qxc': '04'
        }
        
        lottery_code = lottery_code_map.get(lottery_type)
        if not lottery_code:
            raise ValueError(f"未知的彩票类型：{lottery_type}")
        
        params = {
            'gameNo': lottery_code,
            'provinceId': 0,
            'pageSize': page_size,
            'isVerify': 1,
            'pageNo': page_no
        }
        
        try:
            data = self._request(retype='digital', endpoint='history', params=params)
            value_data = data.get('value', {})
            return {
                'total': value_data.get('total', 0),
                'pageNo': value_data.get('pageNo', 0),
                'pageSize': value_data.get('pageSize', 0),
                'pages': value_data.get('pages', 0),
                'result': value_data.get('result', [])  # 开奖结果列表
            }
        except Exception as e:
            log.error(f"获取{lottery_type}历史数据失败：{str(e)}")
            return {'error': str(e), 'result': []}
    
    def get_multi_lottery_data(self, lottery_types: List[str]) -> Dict[str, Any]:
        """
        批量获取多种彩票的开奖信息
            
        Args:
            lottery_types: 彩票类型列表
                
        Returns:
            多种彩票开奖信息的字典
        """
        # 彩票类型与代码的映射
        lottery_code_map = {
            'pl3': '35',
            'pl5': '350133',
            'dlt': '85',
            'qxc': '04'
        }
        
        # API 返回的键名与彩票类型的映射 (API 返回的是 pls 而不是 pl3)
        api_response_key_map = {
            'pl3': 'pls',
            'pl5': 'plw',  # 排列 5 使用 plw 键
            'dlt': 'dlt',
            'qxc': 'qxc'
        }
            
        result = {}
        valid_lottery_codes = []
        valid_lottery_types = []
            
        # 验证彩票类型并转换为代码
        for lottery_type in lottery_types:
            lottery_code = lottery_code_map.get(lottery_type)
            if lottery_code:
                valid_lottery_codes.append(f"{lottery_code},0")
                valid_lottery_types.append(lottery_type)
            else:
                result[lottery_type] = {'error': f"未知的彩票类型：{lottery_type}"}
            
        if not valid_lottery_codes:
            return result
            
        # 构造一次请求的参数字符串，使用分号分隔
        param_str = ";".join(valid_lottery_codes)
            
        params = {
            'param': param_str,
            'isVerify': 1  # 改为 1，启用验证
        }
            
        try:
            # 一次请求获取所有彩种的数据
            data = self._request(retype='digital', endpoint='draw', params=params)
            response_data = data.get('value', {})
                
            # 处理返回的数据
            # API 返回的数据键可能是缩写 (如'pls'代表排列 3/5)
            for lottery_type in valid_lottery_types:
                # 获取 API 返回数据中对应的键名
                api_key = api_response_key_map.get(lottery_type, lottery_type)
                
                # 尝试两种可能的键名
                lottery_data = None
                if api_key in response_data:
                    lottery_data = response_data[api_key]
                elif lottery_type in response_data:
                    lottery_data = response_data[lottery_type]
                
                # 检查是否是空数据 (某些彩种可能当天没有开奖)
                if lottery_data and isinstance(lottery_data, dict) and lottery_data.get('lotteryDrawNum'):
                    result[lottery_type] = lottery_data
                else:
                    result[lottery_type] = {'error': '未找到对应彩种的数据 (可能当天未开奖)'}
        except Exception as e:
            # 如果整体请求失败，为所有有效彩种设置错误信息
            for lottery_type in valid_lottery_types:
                result[lottery_type] = {'error': str(e)}
            
        return result
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()


# 使用示例
if __name__ == "__main__":
    try:
        # 初始化API客户端
        api = SportteryAPI()
        
        a = api.get_football_match_result(match_begin_date='2026-01-14', match_end_date='2026-01-16')
        print(a)
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        if 'api' in locals():
            api.close()