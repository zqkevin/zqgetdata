import json
import re
import traceback
from datetime import datetime, timedelta
from app.common._utils import req_info
from app.common.logger import log
from app.database import *
from app.database.db_core import mydb





def try_parse_float(s):
    try:
        return float(s)
    except:
        return None


def value_re(value):
    try:
        dict = {}
        time = re.search(r"endTime:'(.*?)'", value).group(1)
        dict['matchtime'] = datetime.strptime(time, '%Y-%m-%d %H:%M')
        dict['leaguename'] = re.search(r"leagueName:'(.*?)'", value).group(1)
        dict['homename'] = re.search(r"homeTeam:'(.*?)'", value).group(1)
        dict['awayname'] = re.search(r"guestTeam:'(.*?)'", value).group(1)
        dict['id'] = re.search(r"index:'(.*?)'", value).group(1)
        return dict
    except Exception as e:
        return None


class get_bjdc_data():
    def __init__(self):
        self.nowtime = datetime.now()

    def get_gamedata(self):
        '''
        根据当前期数获取比赛数据，更新到数据库
        包括：
        1. 足球比赛数据
        2. 足球进球赔率
        3. 足球比分赔率
        并且记录变化的时间和变化的赔率到数据库
        :return: None
        '''
        url_list = {
            'spf': 'https://trade.500.com/bjdc/',
            'zjq': 'https://trade.500.com/bjdc/project_fq_jq.php',
            'bifen': 'https://trade.500.com/bjdc/project_fq_bf.php'
        }
        try:
            # 获取当前期数
            soup = req_info("https://trade.500.com/bjdc/")
            if soup:
                qishu = soup.find('select', id='expect_select').find('option', selected=True).get('value')
            else:
                log.info('更新当前比赛数据失败！联网爬取失败')
                return
            for key, value in url_list.items():
                if key == 'spf':
                    self._get_spf(soup, qishu)
                elif key == 'zjq':
                    soup = req_info(value, qishu)
                    if soup:
                        self._get_zjq(soup, qishu)
                    else:
                        log.info(f'更新{qishu}期的总进球赔率数据失败')
                elif key == 'bifen':
                    soup = req_info(value, qishu)
                    if soup:
                        self._get_bifen(soup, qishu)
                    else:
                        log.info(f'更新{qishu}期的比分赔率数据失败')
        except Exception as e:
            log.error(f'Error in get_gamedata:{traceback.format_exc()},e:{e}')

    def _get_bifen(self, soup, qishu):
        '''
        获取足球比分赔率
        :param soup: 足球比分赔率页面的BeautifulSoup对象
        :param qishu: 足球比分赔率对应的期数
        :return: None
        '''
        from app.database.bjdc_models import FootballPLOddsHistory
        upcount = 0

        # 设置一个matchtime的前置时间为最后24小时，判定某场比赛是否在26小时内开始才需更新
        matchtime_pre_time = self.nowtime + timedelta(hours=26)
        # 获取需要更新的比赛
        need_update_matchs = localdb.query(Football).filter(Football.result_statu == 0, Football.dcqs == qishu,
                                                          Football.matchtime <= matchtime_pre_time, 
                                                          Football.matchtime >= self.nowtime).all()
        if len(need_update_matchs) == 0:
            log.info(f'{qishu}期没有需要更新的比分赔率')
            return 
        for match in need_update_matchs:
            fid = match.fid
            tr = soup.find('tr', fid=fid, class_='vs_lines')
            if tr:
                try:
                    err_done = []
                    bifen_tr = tr.find_next_sibling('tr')
                    bifen_tbody = bifen_tr.find('tbody')
                    zhu_goal_list = [0, 1, 2, 3, 4]
                    ke_goal_list = [0, 1, 2, 3, 4, 5]
                    for zhu in zhu_goal_list:
                        conflag = False
                        for ke in ke_goal_list:
                            if zhu > ke > 2 and zhu > 3:
                                bifen = "胜其他"
                                keyname = f'score_win_about'
                                conflag = True
                            elif ke > zhu > 2 and ke > 3:
                                bifen = "负其他"
                                keyname = f'score_lose_about'
                                conflag = True
                            elif zhu == 0 and ke == 5:
                                bifen = "平其他"
                                keyname = f'score_draw_about'
                                ke_goal_list.remove(5)
                                conflag = True
                            else:
                                bifen = f"{zhu}:{ke}"
                                keyname = f'score_{zhu}_{ke}'
                            bifen_span = bifen_tbody.find('span', text=bifen)
                            if bifen_span:
                                bifen_pl = bifen_span.find_next_sibling('span')
                                if bifen_pl:
                                    bifen_pl = bifen_pl.text.strip()
                                    bifen_pl = try_parse_float(bifen_pl)
                                    if bifen_pl is None:
                                        err_done.append(bifen)
                                    else:
                                        # 获取当前赔率值
                                        current_odds = getattr(match.pl, keyname)
                                        # 检查赔率是否有变化或首次设置
                                        if current_odds is None or abs(current_odds - bifen_pl) > 0.03:
                                            # 创建赔率历史记录
                                            odds_history = FootballPLOddsHistory(
                                                football_id=match.id,
                                                odds_type='score',
                                                odds_field=keyname,
                                                odds_value=bifen_pl,
                                                record_time=self.nowtime
                                            )
                                            localdb.add(odds_history, close=False)
                                        # 更新当前赔率值
                                        setattr(match.pl, keyname, bifen_pl)
                                else:
                                    err_done.append(bifen)
                            else:
                                err_done.append(bifen)
                            if conflag:
                                break
                    if len(err_done) > 0:
                        log.error(f'{match.homename}vs{match.awayname}的比分赔率{err_done}未获取完整')
                    else:
                        upcount += 1
                        localdb.update(match, close=False)
                except Exception as e:
                    log.error(f'Error in get_bifen:{traceback.format_exc()}')
                    return None
            else:
                log.info(f'未找到{match.homename}vs{match.awayname}比分赔率')
        log.info(f'{qishu}期未开赛{len(need_update_matchs)}场,本次更新了{upcount}场比分赔率')

    def _get_zjq(self, soup, qishu):
        '''
        获取足球总进球赔率
        :param soup: 足球进球赔率页面的BeautifulSoup对象
        :param qishu: 足球进球赔率对应的期数
        :return: None
        '''
        upcount = 0
        endtime = self.nowtime + timedelta(days=2)
        # 动态创建数据库连接
        db = mydb()
        try:
            need_update_matchs = db.query(Football).filter(Football.result_statu == 0, Football.dcqs == qishu,
                                                            Football.matchtime > self.nowtime, Football.matchtime < endtime).all()
            if len(need_update_matchs) == 0:
                log.info(f'{qishu}期没有需要更新的进球赔率')
                return
            for match in need_update_matchs:
                try:
                    err_done = []
                    fid = match.fid
                    tr = soup.find('tr', fid=fid, class_='vs_lines')
                    td_list = tr.select('td')
                    goal_0 = td_list[6].text.strip()
                    goal_1 = td_list[7].text.strip()
                    goal_2 = td_list[8].text.strip()
                    goal_3 = td_list[9].text.strip()
                    goal_4 = td_list[10].text.strip()
                    goal_5 = td_list[11].text.strip()
                    goal_6 = td_list[12].text.strip()
                    goal_about = td_list[13].text.strip()
                    goal_0 = try_parse_float(goal_0)
                    from app.database.bjdc_models import FootballPLOddsHistory
                    
                    for i in range(7):
                        goal = try_parse_float(locals()[f'goal_{i}'])
                        if goal is None or goal == 0:
                            err_done.append(f'goal_{i}')
                        else:
                            keyname = f'goal_{i}'
                            setattr(match.pl, keyname, goal)
                            
                            # 处理赔率历史数据
                            ploffset = json.loads(getattr(match.pl_offset, keyname))
                            if len(ploffset) < 1:
                                ploffset[self.nowtime.strftime('%d:%H:%M:%S')] = goal
                                
                                # 创建赔率历史记录
                                odds_history = FootballPLOddsHistory()
                                odds_history.football_id = match.id
                                odds_history.odds_type = '总进球'
                                odds_history.odds_field = keyname
                                odds_history.odds_value = goal
                                odds_history.record_time = self.nowtime
                                db.add(odds_history, close=False)
                            else:
                                latest_key = max(ploffset.keys(), key=lambda k: datetime.strptime(k, '%d:%H:%M:%S'))
                                lastvalue = ploffset[latest_key]
                                lastvalue = try_parse_float(lastvalue)
                                if abs(lastvalue - goal) > 0.03:
                                    ploffset[self.nowtime.strftime('%d:%H:%M:%S')] = goal
                                    
                                    # 创建赔率历史记录
                                    odds_history = FootballPLOddsHistory()
                                    odds_history.football_id = match.id
                                    odds_history.odds_type = '总进球'
                                    odds_history.odds_field = keyname
                                    odds_history.odds_value = goal
                                    odds_history.record_time = self.nowtime
                                    db.add(odds_history, close=False)
                            
                            ploffset = json.dumps(ploffset)
                            setattr(match.pl_offset, keyname, ploffset)
                
                    # 处理goal_about赔率
                    goal_about = try_parse_float(goal_about)
                    if goal_about is None:
                        err_done.append('goal_about')
                    else:
                        match.pl.goal_about = goal_about
                        
                        # 处理赔率历史数据
                        ploffset = json.loads(match.pl_offset.goal_about)
                        if len(ploffset) < 1:
                            ploffset[self.nowtime.strftime('%d:%H:%M:%S')] = goal_about
                            
                            # 创建赔率历史记录
                            odds_history = FootballPLOddsHistory()
                            odds_history.football_id = match.id
                            odds_history.odds_type = '总进球'
                            odds_history.odds_field = 'goal_about'
                            odds_history.odds_value = goal_about
                            odds_history.record_time = self.nowtime
                            db.add(odds_history, close=False)
                        else:
                            latest_key = max(ploffset.keys(), key=lambda k: datetime.strptime(k, '%d:%H:%M:%S'))
                            lastvalue = ploffset[latest_key]
                            
                            if lastvalue != goal_about:
                                ploffset[self.nowtime.strftime('%d:%H:%M:%S')] = goal_about
                                
                                # 创建赔率历史记录
                                odds_history = FootballPLOddsHistory()
                                odds_history.football_id = match.id
                                odds_history.odds_type = '总进球'
                                odds_history.odds_field = 'goal_about'
                                odds_history.odds_value = goal_about
                                odds_history.record_time = self.nowtime
                                db.add(odds_history, close=False)
                        
                        ploffset = json.dumps(ploffset)
                        match.pl_offset.goal_about = ploffset
                    
                    if len(err_done) > 0:
                        log.error(f'{match.homename}vs{match.awayname}的进球赔率{err_done}未获取完整')
                    else:
                        upcount += 1
                        db.add(match, close=False)
                except Exception as e:
                    log.error(f'Error in get_zjq:{traceback.format_exc()}')
        except Exception as e:
            log.error(f'Error in get_zjq:{traceback.format_exc()}')
        finally:
            db.close()
        log.info(f'{qishu}期未开赛{len(need_update_matchs)}场,本次更新了{upcount}场总进球赔率')

    def _get_spf(self, soup, qishu):
        '''
        获取足球胜平负赔率
        :param soup: 足球比分赔率页面的BeautifulSoup对象
        :param qishu: 足球比分赔率对应的期数
        :return: None
        '''
        db = mydb()
        try:
            upcount = 0
            addmatch = 0
            all_football = 0
            tbodys_list = soup.find_all('tbody', id=lambda x: x is not None and x != '')
            nowtime = self.nowtime - timedelta(hours=1)
            for tbody in tbodys_list:
                game_date = tbody.get('id').split('_')[0]

                for tr in tbody.find_all('tr'):
                    all_football += 1
                    try:
                        all_done = True
                        td_list = tr.select('td')
                        fid = tr.get('fid')
                        valuestr = tr.get('value')
                        value_dict = value_re(valuestr)
                        if value_dict:
                            matchtime = value_dict['matchtime']
                            homename = value_dict['homename']
                            awayname = value_dict['awayname']
                            leaguename = value_dict['leaguename']
                            qsid = value_dict['id']
                        else:
                            matchtime = game_date + ' ' + td_list[2].text.strip()
                            matchtime = datetime.strptime(matchtime, '%Y-%m-%d %H:%M')
                            homename = tr.find('td', class_='tr').find('a').get('title')
                            awayname = tr.find('td', class_='tl').find('a').get('title')
                            leaguename = tr.find('td', class_='league').text.strip()
                            qsid = tr.find('span', class_="chnum").text.strip()
                        football = db.query(Football).filter_by(index=qsid, dcqs=qishu).first()
                        isaddmatch = 0
                        if not football:
                            isaddmatch = 1
                            football = Football()
                            football.fid = int(fid)
                            football.matchtype = '北单'
                            football.dcqs = qishu
                            football.index = int(qsid)
                            football.leaguename = leaguename
                            football.matchtime = matchtime
                            football.homename = homename
                            football.awayname = awayname
                            football.result_statu = 0
                        else:
                            if matchtime < nowtime or matchtime > self.nowtime + timedelta(days=2):
                                continue
                            elif football.result_statu != 0:
                                continue
                            elif football.result_statu == 6 and self.nowtime - football.matchtime > timedelta(days=2):
                                football.result_statu = 9
                                continue
                            elif football.matchtime < self.nowtime:
                                continue
                            rangqiu_str = td_list[4].text.strip()
                            spf_span_list = td_list[6].select('span')
                            if not spf_span_list or len(spf_span_list) < 3:
                                continue
                            spf_s_pl = td_list[8].text.strip()
                            spf_p_pl = td_list[9].text.strip()
                            spf_f_pl = td_list[10].text.strip()
                            # 欧洲平均赔率
                            spen_list = td_list[6].select('span')
                            s_pl_eu = spen_list[0].text.strip()
                            p_pl_eu = spen_list[1].text.strip()
                            f_pl_eu = spen_list[2].text.strip()
                            winpl = try_parse_float(spf_s_pl)
                            drawpl = try_parse_float(spf_p_pl)
                            losepl = try_parse_float(spf_f_pl)
                            winpl_eu = try_parse_float(s_pl_eu)
                            drawpl_eu = try_parse_float(p_pl_eu)
                            losepl_eu = try_parse_float(f_pl_eu)
                            rangqiu = try_parse_float(rangqiu_str)
                            odds_fields = [
                                {'input_value': winpl, 'pl_attr': 'win_pl', 'pl_offset_attr': 'win_pl',
                                 'error_check': lambda x: x == 0 or x is None},
                                {'input_value': drawpl, 'pl_attr': 'draw_pl', 'pl_offset_attr': 'draw_pl',
                                 'error_check': lambda x: x == 0 or x is None},
                                {'input_value': losepl, 'pl_attr': 'lose_pl', 'pl_offset_attr': 'lose_pl',
                                 'error_check': lambda x: x == 0 or x is None},
                                {'input_value': rangqiu, 'pl_attr': 'rangqiu', 'pl_offset_attr': 'rangqiu',
                                 'error_check': lambda x: x is None},
                                {'input_value': winpl_eu, 'pl_attr': 'winpl_eu', 'pl_offset_attr': 'winpl_eu',
                                 'error_check': lambda x: x == 0 or x is None},
                                {'input_value': drawpl_eu, 'pl_attr': 'drawpl_eu', 'pl_offset_attr': 'drawpl_eu',
                                 'error_check': lambda x: x == 0 or x is None},
                                {'input_value': losepl_eu, 'pl_attr': 'losepl_eu', 'pl_offset_attr': 'losepl_eu',
                                 'error_check': lambda x: x == 0 or x is None},
                            ]

                            # 检查并创建FootballPL实例
                            if football.pl is None:
                                from app.database.bjdc_models import FootballPL
                                football.pl = FootballPL()
                            
                            # 检查并创建FootballPLOffset实例
                            if football.pl_offset is None:
                                from app.database.bjdc_models import FootballPLOffset
                                football.pl_offset = FootballPLOffset()
                            
                            # 遍历处理所有字段
                            for field in odds_fields:
                                value = field['input_value']
                                if field['error_check'](value):
                                    all_done = False
                                else:
                                    # 设置pl属性值
                                    setattr(football.pl, field['pl_attr'], value)
                                    value = try_parse_float(value)
                                    
                                    # 处理赔率历史数据
                                    from app.database.bjdc_models import FootballPLOddsHistory
                                    
                                    # 检查赔率是否有变化
                                    ploffset = getattr(football.pl_offset, field['pl_offset_attr'])
                                    if ploffset is None:
                                        ploffset = {self.nowtime.strftime('%d:%H:%M:%S'): value}
                                        # 创建赔率历史记录
                                        odds_history = FootballPLOddsHistory()
                                        odds_history.football_id = football.id
                                        odds_history.odds_type = '胜平负'
                                        odds_history.odds_field = field['pl_attr']
                                        odds_history.odds_value = value
                                        odds_history.record_time = self.nowtime
                                        db.add(odds_history, close=False)
                                    else:
                                        ploffset = json.loads(ploffset)
                                        if len(ploffset) > 0:
                                            latest_key = max(ploffset.keys(), key=lambda k: datetime.strptime(k, '%d:%H:%M:%S'))
                                            lastvalue = ploffset[latest_key]
                                            lastvalue = try_parse_float(lastvalue)
                                            if abs(lastvalue - value) > 0.03:
                                                # 创建赔率历史记录
                                                odds_history = FootballPLOddsHistory()
                                                odds_history.football_id = football.id
                                                odds_history.odds_type = '胜平负'
                                                odds_history.odds_field = field['pl_attr']
                                                odds_history.odds_value = value
                                                odds_history.record_time = self.nowtime
                                                db.add(odds_history, close=False)
                                                
                                                # 更新偏移表
                                                ploffset[self.nowtime.strftime('%d:%H:%M:%S')] = value
                                        else:
                                            ploffset[self.nowtime.strftime('%d:%H:%M:%S')] = value
                                            # 创建赔率历史记录
                                            odds_history = FootballPLOddsHistory()
                                            odds_history.football_id = football.id
                                            odds_history.odds_type = '胜平负'
                                            odds_history.odds_field = field['pl_attr']
                                            odds_history.odds_value = value
                                            odds_history.record_time = self.nowtime
                                            db.add(odds_history, close=False)
                                    
                                    # 保存更新后的赔率历史
                                    ploffset = json.dumps(ploffset)
                                    setattr(football.pl_offset, field['pl_offset_attr'], ploffset)
                            if all_done:
                                if isaddmatch == 1:
                                    addmatch += 1
                                upcount += 1
                                db.add(football, close=False)
                    except Exception as e:
                        log.error(f'Error in get_spf:{traceback.format_exc()}')
        except Exception as e:
            log.error(f'Error in get_spf:{traceback.format_exc()}')
        finally:
            db.close()
        if addmatch > 0:
            log.info(f'{qishu}期共{all_football}场比赛,本次新增{addmatch}场，更新胜平负赔率{upcount}场')
        else:
            log.info(f'{qishu}期共{all_football}场比赛,本次无新增比赛,更新胜平负赔率{upcount}场')

    def result_match(self):
        '''
        获取需要获取结果的比赛
        查询比赛时间开赛时间和当前时间差大于等于4小时的比赛进行赛果获取
        :return:
        '''
        try:
            # 统计需要获取的比赛数据的场次
            nowtime = self.nowtime - timedelta(hours=3)
            need_result_matchs = localdb.query(Football).filter(Football.result_statu == 0,
                                                                Football.matchtime < nowtime).all()
            if len(need_result_matchs) == 0:
                log.info('没有需要获取结果的比赛')
                return
            else:
                dcqs_list = set(n.dcqs for n in need_result_matchs)
                upcount = 0
                for dcqs in dcqs_list:
                    url = f'https://live.500.com/zqdc.php'
                    log.info(f'开始获取{dcqs}的比赛结果')
                    soup = req_info(url, dcqs)
                    dcqs_matchs = [match for match in need_result_matchs if match.dcqs == dcqs]
                    for i in dcqs_matchs:
                        football = localdb.query(Football).filter(Football.fid == i.fid, Football.dcqs == dcqs,
                                                                  Football.result_statu == 0).first()
                        if football:
                            if nowtime - football.matchtime > timedelta(days=7):
                                football.result_statu = 9
                                localdb.add(football)
                                continue
                        fid = football.fid
                        fid_tr = soup.find('tr', fid=fid)
                        if not fid_tr:
                            home_away = f'{football.homename},{football.awayname}'
                            fid_tr = soup.find('tr', attrs={'gy': lambda x: x and home_away in x})
                        if fid_tr:
                            status = fid_tr.get('status')
                            if football.fid == -1:
                                football.fid = int(fid_tr.get('fid'))
                            if status == '4':
                                fid_td = fid_tr.select('td')
                                homegoal = try_parse_float(fid_tr.find('a', class_='clt1').text.strip())
                                awaygoal = try_parse_float(fid_tr.find('a', class_='clt3').text.strip())
                                half_goal = fid_td[8].text.strip().split('-')
                                half_homegoal = try_parse_float(half_goal[0])
                                half_awaygoal = try_parse_float(half_goal[1])
                                spf, zjq, bifen = check_zq_win_pl(football, homegoal, awaygoal)
                                football.result.homegoal = try_parse_float(homegoal)
                                football.result.awaygoal = try_parse_float(awaygoal)
                                football.result.half_homegoal = try_parse_float(half_homegoal)
                                football.result.half_awaygoal = try_parse_float(half_awaygoal)
                                football.result.spf = spf
                                football.result.zjq = zjq
                                football.result.bifen = bifen
                                football.result.rqspf = 0
                                football.result_statu = 1
                                localdb.add(football, close=False)
                                upcount += 1
                            elif status == '6':
                                football.result_statu = 6
                                localdb.add(football, close=False)
                                log.info(f'{football.homename}vs{football.awayname}的比赛已取消')
                                continue
                            elif status == '8':
                                football.result_statu = 8
                                localdb.add(football, close=False)
                                log.info(f'{football.homename}vs{football.awayname}的比赛中断')
                                continue
                            elif status == '7':
                                football.result_statu = 7
                                localdb.add(football, close=False)
                                log.info(f'{football.homename}vs{football.awayname}的比赛腰斩')
                                continue
                            else:
                                continue
                        else:
                            log.info('未找到比赛结果')
                            continue
                if upcount == len(need_result_matchs):
                    log.info(f'需要更新{upcount}场比赛全部更新')
                else:
                    log.info(f'需要更新{len(need_result_matchs)}场的比赛结果更新了{upcount}场')
        except Exception as e:
            print(f'Error in result_match:{traceback.format_exc()}')
            return None