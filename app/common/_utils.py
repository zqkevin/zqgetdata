# -*- coding: utf-8 -*-
import random
import string
import time
import traceback
from app.log.logger import log, get_logger
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# 通用数据库操作日志（用于 _utils 中的公共函数）
db_log = get_logger('common', 'db_utils')


def generate_random_cookies(key):
    """
    根据key生成相应的cookies
    key: 'okooo' 或 '500' 等标识符
    返回处理后的cookies字典
    """

    # 生成随机参数的函数
    def generate_random_param(length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    # 生成随机数字参数
    def generate_random_numeric_param(length=10):
        return ''.join(random.choices(string.digits, k=length))

    # 生成随机时间戳
    def generate_timestamp():
        return str(int(time.time()))

    # 根据不同的key生成不同的cookies
    if key == 'okooo':
        cookies = {
            "_ga": "GA1.1." + generate_random_numeric_param(10) + "." + generate_timestamp(),
            "_ga_B3LCXP8H9E": "GS2.1.s" + generate_timestamp() + "$o" + generate_random_numeric_param(1) +
                              "$g0$t" + generate_timestamp() + "$j" + generate_random_numeric_param(2) +
                              "$l0$h" + generate_random_numeric_param(9),
            "acw_tc": "0" + generate_random_param(2) + generate_random_numeric_param(3) + generate_timestamp() +
                      generate_random_param(20),
            "First_Source": "www.okooo.com",
            "FirstOKURL": "https%3A//www.okooo.com/jingcai/",
            "Hm_lpvt_213d524a1d07274f17dfa17b79db318f": generate_timestamp(),
            "Hm_lvt_213d524a1d07274f17dfa17b79db318f": generate_timestamp() + "," + generate_timestamp() + "," + generate_timestamp(),
            "HMACCOUNT": generate_random_param(16),
            "LastUrl": "",
            "LoginStr": "%7B%22welcome%22%3A%22%u60A8%u597D%uFF0C%u6B22%u8FCE%u60A8%22%2C%22login%22%3A%22%u767B%u5F55%22%2C%22register%22%3A%22%u6CE8%u518C%22%2C%22TrustLoginArr%22%3A%7B%22alipay%22%3A%7B%22LoginCn%22%3A%22%22%7D%2C%22tenpay%22%3A%7B%22LoginCn%22%3A%22%u8D22%u4ED8%u901A%22%7D%2C%22weibo%22%3A%7B%22LoginCn%22%3A%22%u65B0%u6D6A%u5FAE%u535A%22%7D%2C%22renren%22%3A%7B%22LoginCn%22%3A%22%22%7D%2C%22baidu%22%3A%7B%22LoginCn%22%3A%22%22%7D%2C%22snda%22%3A%7B%22LoginCn%22%3A%22%22%7D%7D%2C%22userlevel%22%3A%22%22%2C%22flog%22%3A%22hidden%22%2C%22UserInfo%22%3A%22%22%2C%22loginSession%22%3A%22___GlobalSession%22%7D",
            "LStatus": "N",
            "PHPSESSID": generate_random_param(32),
            "pm": ""
        }
    elif key == '500':
        # 这里是基于之前getdata.py中的cookies结构
        cookies = {
            "H_PS_PSSID": "39996_40010_40204_40080_40207_40222_40059",
            "HMACCOUNT_BFESS": generate_random_param(16),
            "ZFY": generate_random_param(20) + ":C",
            "BAIDUID_BFESS": generate_random_param(32) + ":FG=1",
            "PSTM": generate_timestamp(),
            "BIDUPSID": generate_random_param(32),
            "repeata5c50a810b2fec49998325869b586615": generate_random_param(32),
            "motion_id": generate_timestamp() + "_" + str(random.random()),
            "_jzqa": "1." + generate_random_numeric_param(
                19) + "." + generate_timestamp() + "." + generate_timestamp() + "." + generate_timestamp() + ".1",
            "_qzjc": "1",
            "BAIDUID": generate_random_param(32) + ":FG=1",
            "_qzjto": "1.1.0",
            "WT_FPC": "id=undefined:lv=" + generate_timestamp() + ":ss=" + generate_timestamp(),
            "__utmz": generate_random_numeric_param(
                8) + "." + generate_timestamp() + ".1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
            "_qzja": "1." + generate_random_numeric_param(
                10) + "." + generate_timestamp() + "." + generate_timestamp() + "." + generate_timestamp() + "." + generate_timestamp() + "." + generate_timestamp() + ".0.0.0.1.1",
            "_jzqc": "1",
            "__utmb": generate_random_numeric_param(8) + ".17.10." + generate_timestamp(),
            "__utma": generate_random_numeric_param(8) + "." + generate_random_numeric_param(
                9) + "." + generate_timestamp() + "." + generate_timestamp() + "." + generate_timestamp() + ".6",
            "_jzqckmp": "1",
            "ck_RegFromUrl": "https%3A%2F%2Fwww.500.com%2F",
            "ck_RegUrl": "trade.500.com",
            "sdc_userflag": generate_timestamp() + "::" + generate_timestamp() + "::" + str(random.randint(1, 99)),
            "repeat69989f90223482523261fb81b7d63f18": generate_random_param(32),
            "_qzjb": "1." + generate_timestamp() + ".1.0.0.0",
            "repeate4f24e4dc1b07flocaldb133ba9b8bd68b115": generate_random_param(32),
            "amrkts": generate_timestamp()[:-3],  # 使用较短的时间戳
            "Hm_lpvt_4f816d475bb0b9ed640ae412d6b42cab": generate_timestamp(),
            "CLICKSTRN_ID": "223.74.121.7-" + generate_timestamp() + "." + str(
                random.randint(100000, 999999)) + "::" + generate_random_param(16) + "localdb" + generate_random_param(
                16),
            "sdc_session": generate_timestamp()[:-3],
            "liansaihidetag": "true",
            "Hm_lvt_4f816d475bb0b9ed640ae412d6b42cab": generate_timestamp() + "," + generate_timestamp()
        }
    else:
        # 默认返回空cookies或基本cookies
        cookies = {}

    return cookies

def check_zq_win_pl(match, homegoal, awaygoal):
    '''
    检查足球比赛胜平负、总进球、比分赔率
    :param match: 比赛对象 (可以是 FootballMatch 或带 pl 属性的对象)
    :param homegoal: 主队进球数
    :param awaygoal: 客队进球数
    :return: (spf, zjq, bifen) 赔率元组
    '''
    homegoal = int(homegoal)
    awaygoal = int(awaygoal)
    
    # 尝试获取赔率信息
    if hasattr(match, 'pl') and match.pl is not None:
        # 有赔率信息，使用原有逻辑
        if homegoal > awaygoal:
            spf = match.pl.win_pl
        elif homegoal == awaygoal:
            spf = match.pl.draw_pl
        else:
            spf = match.pl.lose_pl
        
        allgoal = homegoal + awaygoal
        if allgoal > 6:
            zjq = match.pl.goal_about
        else:
            zjq = getattr(match.pl, f'goal_{allgoal}')
        
        if homegoal > awaygoal and (homegoal > 4 or awaygoal > 2):
            bifen = match.pl.score_win_about
        elif awaygoal > homegoal and (awaygoal > 4 or homegoal > 2):
            bifen = match.pl.score_lose_about
        elif homegoal == awaygoal and homegoal > 3:
            bifen = match.pl.score_draw_about
        else:
            bifen = getattr(match.pl, f'score_{homegoal}_{awaygoal}')
    else:
        # 没有赔率信息，返回默认值
        home_name = match.home_team.team_short_name if match.home_team else 'Unknown'
        away_name = match.away_team.team_short_name if match.away_team else 'Unknown'
        log.debug(f'比赛 {home_name} vs {away_name} 无赔率信息，使用默认值')
        if homegoal > awaygoal:
            spf = 1.0  # 主胜默认赔率
        elif homegoal == awaygoal:
            spf = 2.0  # 平局默认赔率
        else:
            spf = 3.0  # 客胜默认赔率
        
        # 总进球默认赔率
        zjq = 1.5
        # 比分默认赔率
        bifen = 5.0
    
    return spf, zjq, bifen

def handle_league_name(league_name, source_type=None):
    """
    根据联赛名称检索联赛信息，如果不存在则新增
    :param league_name: 联赛名称 (全称或简称)
    :param source_type: 数据来源类型 ('bjdc', 'tczq'等)，用于判断如何处理名称
    :return: 联赛信息对象
    """
    from app.database import localdb, League
    import traceback
    
    try:
        # 0. 关键修复：确保事务有效（防止 PendingRollbackError）
        try:
            if localdb.session and not localdb.session.is_active:
                log.warning("检测到无效事务，执行回滚")
                localdb.rollback()
        except Exception:
            pass
        
        # 1. 先尝试通过联赛全称精确查找
        league = localdb.query(League).filter_by(league_name=league_name).first()
        
        if not league:
            # 2. 尝试通过联赛简称精确查找
            league = localdb.query(League).filter_by(league_name_abbr=league_name).first()
            
        if not league:
            # 3. 关键优化：双向模糊匹配 + 检查会话中的新对象
            # 先检查当前会话中是否已添加但未提交的对象
            for obj in localdb.session.new:
                if isinstance(obj, League):
                    # 检查是否与待添加的联赛同名
                    if (obj.league_name == league_name or 
                        obj.league_name_abbr == league_name or
                        (obj.league_name and league_name in obj.league_name) or
                        (obj.league_name_abbr and league_name in obj.league_name_abbr)):
                        league = obj
                        log.debug(f"会话中找到匹配联赛：{league_name} -> {obj.league_name}/{obj.league_name_abbr}")
                        break
            
            # 如果会话中没有，再查询数据库进行模糊匹配
            if not league:
                all_leagues = localdb.query(League).all()
                for lg in all_leagues:
                    # 跳过空名称
                    if not lg.league_name and not lg.league_name_abbr:
                        continue
                        
                    is_match = False
                    
                    # 只有当传入名称长度>2时才进行模糊匹配，避免误匹配
                    if len(league_name) > 2:
                        # 情况1：传入的是全称，匹配已有记录的简称
                        # 例如：传入"澳大利亚超级联赛"，匹配简称"澳超"
                        if lg.league_name_abbr and lg.league_name_abbr in league_name:
                            is_match = True
                        # 情况2：传入的是简称，匹配已有记录的全称或简称
                        # 例如：传入"澳超"，匹配全称"澳大利亚超级联赛"或简称"澳超"
                        elif lg.league_name and league_name in lg.league_name:
                            is_match = True
                        elif lg.league_name_abbr and league_name in lg.league_name_abbr:
                            is_match = True
                        # 情况3：传入名称包含已有记录的全称
                        elif lg.league_name and lg.league_name in league_name:
                            is_match = True
                    else:
                        # 短名称精确匹配
                        if lg.league_name_abbr == league_name or lg.league_name == league_name:
                            is_match = True
                    
                    if is_match:
                        league = lg
                        log.debug(f"模糊匹配成功：{league_name} -> {lg.league_name}/{lg.league_name_abbr} (ID: {lg.id})")
                        break
        
        if not league:
            # 4. 如果都不存在，则新增联赛
            import random
            # 生成随机的 league_id
            league_id = random.randint(1000, 9999)
            # 确保 league_id 唯一
            while localdb.query(League).filter_by(league_id=league_id).first():
                league_id = random.randint(1000, 9999)
                    
            league = League()
            league.league_id = league_id
            
            # 关键修改：根据来源类型决定如何存储名称
            if source_type == 'bjdc':
                # BJDC提供的是简称，存到 league_name_abbr，league_name 留空等待 TCZQ 补充
                league.league_name = ''  # 全称留空
                league.league_name_abbr = league_name  # 简称
                db_log.debug(f"✅ 新增联赛（BJDC简称）：{league_name} (ID: {league_id}, 全称待补充)")
            else:
                # 其他来源（如TCZQ），同时存储全称和简称
                league.league_name = league_name
                league.league_name_abbr = league_name  # 默认简称与全称相同
                db_log.debug(f"✅ 新增联赛：{league_name} (ID: {league_id})")
            
            league.region = ""  # 默认空字符串
            league.country = ""  # 默认空字符串
            league.href = f"/league/{league_id}/"  # 生成默认链接地址
            localdb.add(league, close=False)  # 不关闭会话，避免对象分离
        else:
            # 5. 如果找到已有记录，更新缺失的信息
            # 关键逻辑：只有TCZQ才需要补充全称（BJDC只提供简称）
            if source_type == 'tczq' and not league.league_name and league_name:
                # 检查全称是否与简称不同
                existing_abbr = league.league_name_abbr or ''
                
                # 只有当全称与简称不同时，才补充全称
                if league_name != existing_abbr:
                    old_abbr = existing_abbr or '(空)'
                    league.league_name = league_name
                    # 如果简称也为空，则用全称填充
                    if not league.league_name_abbr:
                        league.league_name_abbr = league_name
                    localdb.update(league, close=False)
                    db_log.debug(f"📝 补充联赛全称：{old_abbr} -> {league_name} (ID: {league.id})")
                else:
                    # 全称与简称相同，说明API本身就没有提供真正的全称，不更新
                    db_log.debug(f"联赛全称与简称相同，跳过更新：{league_name} (ID: {league.id})")
            # 如果当前记录有全称但无简称，补充简称
            elif league.league_name and not league.league_name_abbr:
                league.league_name_abbr = league.league_name
                localdb.update(league, close=False)
                log.debug(f"补充联赛简称：{league.league_name}")
        
        # 确保对象数据已加载到内存
        if league:
            # 访问所有属性以确保它们被加载
            _ = league.id
            _ = league.league_id
            _ = league.league_name
            _ = league.league_name_abbr
        
        return league
    except Exception as e:
        log.error(f"处理联赛名称时出错：{traceback.format_exc()}")
        # 关键修复：异常时回滚事务
        try:
            localdb.rollback()
            log.debug("已回滚事务（handle_league_name 异常）")
        except Exception as rollback_error:
            log.error(f"回滚事务失败：{str(rollback_error)}")
        return None


def get_or_create_league(league_name, league_name_abbr=None):
    """
    通用联赛处理函数：根据名称查询或创建联赛，返回数据库主键 ID
    
    Args:
        league_name: 联赛名称（必填，通常是全称）
        league_name_abbr: 联赛简称（可选）
    
    Returns:
        int: 联赛的数据库主键 ID，失败返回 None
    
    Example:
        league_id = get_or_create_league("英格兰冠军联赛", "英冠")
        if league_id:
            match.league_id = league_id
    """
    if not league_name:
        log.warning("联赛名称为空")
        return None
    
    try:
        # 关键修改：传递 source_type=None，让 handle_league_name 自动处理
        # handle_league_name 会先查全称，再查简称，最后才创建
        league = handle_league_name(league_name, source_type=None)
        
        if league:
            # 如果提供了简称，确保简称也被设置
            if league_name_abbr:
                # 如果当前记录的简称为空或与传入的不同，更新简称
                if not league.league_name_abbr or league.league_name_abbr != league_name_abbr:
                    from app.database import localdb
                    old_abbr = league.league_name_abbr
                    league.league_name_abbr = league_name_abbr
                    localdb.update(league, close=False)
                    log.debug(f"更新/补充联赛简称：{old_abbr or '(空)'} -> {league_name_abbr}")
            
            log.debug(f"联赛处理成功：{league_name} -> DB ID: {league.id}")
            return league.id
        else:
            log.error(f"处理联赛失败：{league_name}")
            # 关键修复：handle_league_name 返回 None 时可能已有错误，回滚事务
            try:
                from app.database import localdb
                localdb.rollback()
                log.debug(f"已回滚事务（联赛处理失败：{league_name}）")
            except Exception as rollback_error:
                log.error(f"回滚事务失败：{str(rollback_error)}")
            return None
    except Exception as e:
        log.error(f"获取或创建联赛失败 (league_name={league_name}): {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        # 关键修复：异常时回滚事务
        try:
            from app.database import localdb
            localdb.rollback()
            log.debug(f"已回滚事务（异常：{league_name}）")
        except Exception as rollback_error:
            log.error(f"回滚事务失败：{str(rollback_error)}")
        return None


def handle_team_name(team_full_name, team_short_name=None, team_code=None, source_type=None):
    """
    根据球队名称检索球队信息，如果不存在则新增
    支持通过别名查询，解决不同数据源球队名称不一致问题
    
    :param team_full_name: 球队全称
    :param team_short_name: 球队简称
    :param team_code: 球队代码
    :param source_type: 数据来源类型 ('tczq', 'bjdc', 'okooo'等)
    :return: 球队信息对象
    """
    from app.database import localdb, Team, TeamAlias
    from datetime import datetime
    import traceback
    import random
    
    try:
        # 0. 关键修复：确保事务有效（防止 PendingRollbackError）
        try:
            if localdb.session and not localdb.session.is_active:
                log.warning("检测到无效事务，执行回滚")
                localdb.rollback()
        except Exception:
            pass
        
        # 1. 先尝试通过球队全称查找
        team = localdb.query(Team).filter_by(team_full_name=team_full_name).first()
        
        # 关键修复：如果数据库中找不到，检查当前会话中是否已添加（防止重复创建）
        if not team:
            for obj in localdb.session.new:
                if isinstance(obj, Team) and obj.team_full_name == team_full_name:
                    team = obj
                    log.debug(f"会话中已存在球队：{team_full_name}")
                    break
        
        if not team and source_type:
            # 2. 如果找不到，尝试通过别名查找
            alias = localdb.query(TeamAlias).filter_by(
                alias_name=team_full_name,
                source_type=source_type
            ).first()
            
            if alias:
                team = localdb.query(Team).filter_by(id=alias.team_id).first()
                if team:
                    log.debug(f"通过别名找到球队：{team_full_name} -> {team.team_full_name} (来源:{source_type})")
                else:
                    log.warning(f"通过别名找到 TeamAlias 但未找到对应球队：{team_full_name}, alias.team_id={alias.team_id}")
        
        if not team and team_short_name:
            # 3. 尝试通过球队简称查找
            team = localdb.query(Team).filter_by(team_short_name=team_short_name).first()
        
        if not team:
            # 4. 如果都不存在，则新增球队
            try:
                # 生成随机的 team_id
                team_id = random.randint(1000, 99999)
                # 确保 team_id 唯一
                while localdb.query(Team).filter_by(team_id=team_id).first():
                    team_id = random.randint(1000, 99999)
                
                team = Team(
                    team_id=team_id,
                    team_code=team_code or str(team_id),
                    team_full_name=team_full_name,
                    team_short_name=team_short_name or team_full_name,
                    team_short_en_name="",  # 默认空字符串
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                localdb.add(team, close=False)  # 不关闭会话，避免对象分离
                log.debug(f"新增球队：{team_full_name} (ID: {team_id})")
                
                # 5. 如果是新球队且有来源类型，添加别名记录
                if source_type:
                    alias = TeamAlias(
                        team_id=team.id,
                        alias_name=team_full_name,
                        source_type=source_type,
                        is_primary=1,  # 第一个名称作为主别名
                        remark=f"自动创建 - {source_type} 数据源"
                    )
                    localdb.add(alias, close=False)
                    log.debug(f"添加球队别名：{team_full_name} (来源:{source_type})")
            except Exception as create_error:
                # 如果是唯一键冲突，重新查询
                if 'Duplicate entry' in str(create_error):
                    log.warning(f"检测到球队重复创建，重新查询：{team_full_name}")
                    localdb.rollback()  # 回滚失败的事务
                    team = localdb.query(Team).filter_by(team_full_name=team_full_name).first()
                    if team:
                        log.info(f"✓ 找到已存在的球队：{team_full_name} (ID: {team.id})")
                    else:
                        log.error(f"回滚后仍未找到球队：{team_full_name}")
                        return None
                else:
                    raise
        else:
            # 6. 如果找到球队且有来源类型，检查是否需要添加别名
            if source_type:
                existing_alias = localdb.query(TeamAlias).filter_by(
                    team_id=team.id,
                    source_type=source_type,
                    alias_name=team_full_name
                ).first()
                
                if not existing_alias:
                    # 添加新的别名记录
                    alias = TeamAlias(
                        team_id=team.id,
                        alias_name=team_full_name,
                        source_type=source_type,
                        is_primary=0,
                        remark=f"自动添加 - {source_type} 数据源"
                    )
                    localdb.add(alias, close=False)
                    log.debug(f"为已有球队添加别名：{team.team_full_name} <- {team_full_name} (来源:{source_type})")
        
        # 确保对象数据已加载到内存
        if team:
            # 访问所有属性以确保它们被加载
            _ = team.id
            _ = team.team_id
            _ = team.team_full_name
            _ = team.team_short_name
        
        return team
    except Exception as e:
        log.error(f"处理球队名称时出错：{traceback.format_exc()}")
        # 关键修复：异常时回滚事务
        try:
            localdb.rollback()
            log.debug("已回滚事务（handle_team_name 异常）")
        except Exception as rollback_error:
            log.error(f"回滚事务失败：{str(rollback_error)}")
        return None


def get_or_create_team(team_full_name, team_short_name=None, team_code=None, source_type=None):
    """
    通用球队处理函数：根据名称查询或创建球队，返回数据库主键 ID
    
    Args:
        team_full_name: 球队全称（必填）
        team_short_name: 球队简称（可选）
        team_code: 球队代码（可选）
        source_type: 数据来源类型 ('tczq', 'bjdc', 'okooo'等)（可选）
    
    Returns:
        int: 球队的数据库主键 ID，失败返回 None
    
    Example:
        home_team_id = get_or_create_team("曼联", "曼彻斯特联", source_type='tczq')
        away_team_id = get_or_create_team("利物浦", source_type='tczq')
        if home_team_id and away_team_id:
            match.home_team_id = home_team_id
            match.away_team_id = away_team_id
    """
    if not team_full_name:
        log.warning("球队全称为空")
        return None
    
    try:
        team = handle_team_name(team_full_name, team_short_name, team_code, source_type)
        if team:
            log.debug(f"球队处理成功：{team_full_name} -> DB ID: {team.id}")
            return team.id
        else:
            log.error(f"处理球队失败：{team_full_name}")
            # 关键修复：handle_team_name 返回 None 时可能已有错误，回滚事务
            try:
                from app.database import localdb
                localdb.rollback()
                log.debug(f"已回滚事务（球队处理失败：{team_full_name}）")
            except Exception as rollback_error:
                log.error(f"回滚事务失败：{str(rollback_error)}")
            return None
    except Exception as e:
        log.error(f"获取或创建球队失败 (team_full_name={team_full_name}): {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        # 关键修复：异常时回滚事务
        try:
            from app.database import localdb
            localdb.rollback()
            log.debug(f"已回滚事务（异常：{team_full_name}）")
        except Exception as rollback_error:
            log.error(f"回滚事务失败：{str(rollback_error)}")
        return None


def get_or_create_tcbk_league(league_id: int, league_name: str, league_name_abbr: str = ''):
    """
    竞彩篮球专用联赛处理函数：根据联赛ID查询或创建联赛，返回数据库主键 ID
    
    Args:
        league_id: 联赛 ID（API 提供）
        league_name: 联赛名称
        league_name_abbr: 联赛简称
    
    Returns:
        int: 联赛的数据库主键 ID，失败返回 None
    
    Example:
        league_db_id = get_or_create_tcbk_league(100, "NBA", "美职篮")
        if league_db_id:
            match.league_id = league_id  # 注意：这里存的是 API 的 league_id
    """
    if not league_id or not league_name:
        log.warning(f"联赛信息不完整 (league_id={league_id}, league_name={league_name})")
        return None
    
    try:
        from app.database import localdb, TcbkLeague
        
        # 0. 关键修复：确保事务有效（防止 PendingRollbackError）
        try:
            if localdb.session and not localdb.session.is_active:
                log.warning("检测到无效事务，执行回滚")
                localdb.rollback()
        except Exception:
            pass
        
        # 1. 先尝试通过 league_id 查找
        league = localdb.query(TcbkLeague).filter_by(league_id=league_id).first()
        
        if not league:
            # 2. 不存在则创建
            league = TcbkLeague(
                league_id=league_id,
                league_name=league_name,
                league_name_abbr=league_name_abbr or ''
            )
            localdb.add(league, close=False)
            log.info(f"新增篮球联赛：{league_name} (API ID: {league_id})")
        else:
            # 3. 存在则更新简称（如果有变化）
            if league_name_abbr and league.league_name_abbr != league_name_abbr:
                league.league_name_abbr = league_name_abbr
                localdb.update(league, close=False)
                log.debug(f"更新篮球联赛简称：{league_name} -> {league_name_abbr}")
        
        log.debug(f"篮球联赛处理成功：{league_name} -> DB ID: {league.id}")
        return league.id
        
    except Exception as e:
        log.error(f"获取或创建篮球联赛失败 (league_id={league_id}, league_name={league_name}): {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        # 关键修复：异常时回滚事务
        try:
            from app.database import localdb
            localdb.rollback()
            log.debug(f"已回滚事务（篮球联赛处理失败：{league_name}）")
        except Exception as rollback_error:
            log.error(f"回滚事务失败：{str(rollback_error)}")
        return None


def req_info(url, qishu=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.149 Safari/537.36'
        }
        if '500' in url:
            cookies = generate_random_cookies('500')
        elif 'okooo' in url:
            cookies = generate_random_cookies('okooo')
        else:
            cookies = None
        url = url if qishu is None else f'{url}?e={qishu}'
        soup = None
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        for i in range(3):
            response = session.get(url=url, headers=headers, cookies=cookies, timeout=10)
            if response.status_code == 200:
                response.encoding = 'gbk'
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup
            else:
                time.sleep(5)
        if soup:
            return soup
        else:
            return None
    except Exception as e:
        log.error(f"Error in get_bdgame_info: {traceback.format_exc()}")
        return None


def calculate_current_odds(odds_record_id: int, field_name: str, odds_table: str = None, 
                          sport_type: str = 'tczq') -> float:
    """
    根据赔率记录ID和字段名，计算考虑所有波动后的当前赔率
    
    业务逻辑：
    1. 从数据库中获取该赔率记录的原始值（初始值）
    2. 查询该记录的所有历史波动日志
    3. 累加所有波动值：当前赔率 = 初始值 + 所有波动的diff之和
    
    Args:
        odds_record_id: 赔率记录的主键ID
        field_name: 需要计算的赔率字段名 (如 'win_pl', 'draw_pl', 'handicap' 等)
        odds_table: 赔率表名 (可选，用于确定使用哪个变化日志表)
                   - 'tczq_spf_odds' -> zq_odds_change_log
                   - 'tcbk_dxf' -> bk_odds_change_log
                   - 'bjdc_spf' -> bjdc_odds_change_log
                   如果为None，会自动根据ID推断
        sport_type: 赛事类型 ('tczq'=足球, 'tcbk'=篮球, 'bjdc'=北京单场)
                   用于确定从哪个日志表查询数据
    
    Returns:
        float: 计算后的当前赔率值，如果出错返回0.0
    
    Examples:
        # 计算体彩足球胜平负赔率记录ID=5的当前主胜赔率
        current_win_pl = calculate_current_odds(5, 'win_pl', 'tczq_spf_odds', 'tczq')
        
        # 计算竞彩篮球大小分赔率记录ID=10的当前大分赔率
        current_over = calculate_current_odds(10, 'over', 'tcbk_dxf', 'tcbk')
    """
    from app.database import localdb
    
    try:
        # 1. 直接使用传入的 sport_type 参数
        change_log_class = _get_change_log_class(sport_type)
        
        if change_log_class is None:
            log.error(f"无法获取变化日志类 (sport_type={sport_type})")
            return 0.0
        
        # 2. 从原始赔率表中获取初始值（基准值）
        base_value = _get_original_odds_value(odds_record_id, field_name, odds_table)
        
        if base_value == 0.0:
            log.debug(f"[{sport_type}] 赔率记录 {odds_record_id}.{field_name} 的当前值为 0.0 (可能未初始化)")
            return 0.0
        
        # 3. 查询该记录的所有历史波动日志，累加波动值
        logs = localdb.query(change_log_class).filter_by(
            odds_record_id=odds_record_id,
            odds_field=field_name
        ).order_by(change_log_class.change_time.asc()).all()
        
        # 4. 计算累计波动：当前值 = 初始值 + 所有波动的(new_value - old_value)之和
        total_diff = 0.0
        for log_entry in logs:
            diff = log_entry.new_value - log_entry.old_value
            total_diff += diff
        
        current_value = base_value + total_diff
        
        if logs:
            log.debug(f"[{sport_type}] 赔率记录 {odds_record_id}.{field_name}: "
                     f"初始值={base_value:.3f}, 累计波动={total_diff:.3f} ({len(logs)}次), "
                     f"当前值={current_value:.3f}")
        else:
            log.debug(f"[{sport_type}] 赔率记录 {odds_record_id}.{field_name}: "
                     f"当前值={current_value:.3f} (无波动记录)")
        
        return float(current_value)
        
    except Exception as e:
        log.error(f"计算赔率失败 (record_id={odds_record_id}, field={field_name}): {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return 0.0


def _get_change_log_class(sport_type: str):
    """
    根据赛事类型获取对应的赔率变化日志类
    
    Args:
        sport_type: 赛事类型 ('tczq', 'tcbk', 'bjdc')
    
    Returns:
        对应的OddsChangeLog类，如果不存在返回None
    """
    try:
        if sport_type == 'tczq':
            from app.database import TczqOddsChangeLog
            return TczqOddsChangeLog
        elif sport_type == 'tcbk':
            from app.database import TcbkOddsChangeLog
            return TcbkOddsChangeLog
        elif sport_type == 'bjdc':
            from app.database import BjdcOddsChangeLog
            return BjdcOddsChangeLog
        else:
            log.error(f"不支持的赛事类型: {sport_type}")
            return None
    except ImportError as e:
        log.error(f"导入变化日志类失败 ({sport_type}): {str(e)}")
        return None


def _get_original_odds_value(odds_record_id: int, field_name: str, odds_table: str) -> float:
    """
    从原始赔率表中获取指定字段的当前值
    
    Args:
        odds_record_id: 赔率记录ID
        field_name: 字段名
        odds_table: 赔率表名
    
    Returns:
        float: 字段值，如果不存在返回0.0
    """
    from app.database import localdb
    
    try:
        # 根据表名动态获取模型类
        model_class = _get_odds_model_class(odds_table)
        if model_class is None:
            return 0.0
        
        # 查询记录
        record = localdb.query(model_class).filter_by(id=odds_record_id).first()
        if record is None:
            log.warning(f"未找到赔率记录: {odds_table}.id={odds_record_id}")
            return 0.0
        
        # 获取字段值
        value = getattr(record, field_name, None)
        if value is None:
            log.warning(f"字段不存在: {odds_table}.{field_name}")
            return 0.0
        
        return float(value)
        
    except Exception as e:
        log.error(f"获取原始赔率值失败: {str(e)}")
        return 0.0


def _get_odds_model_class(odds_table: str):
    """
    根据表名获取对应的ORM模型类
    
    Args:
        odds_table: 表名 (如 'tczq_spf_odds', 'tcbk_dxf')
    
    Returns:
        对应的模型类，如果不存在返回None
    """
    try:
        # 体彩足球
        if odds_table == 'tczq_spf_odds':
            from app.database import TczqSpfOdds
            return TczqSpfOdds
        elif odds_table == 'tczq_handicap_spf_odds':
            from app.database import TczqHandicapSpfOdds
            return TczqHandicapSpfOdds
        elif odds_table == 'tczq_total_goal_odds':
            from app.database import TczqTotalGoalOdds
            return TczqTotalGoalOdds
        elif odds_table == 'tczq_ht_ft_odds':
            from app.database import TczqHalfTimeFullTimeOdds
            return TczqHalfTimeFullTimeOdds
        elif odds_table == 'tczq_score_odds':
            from app.database import TczqScoreOdds
            return TczqScoreOdds
        
        # 竞彩篮球
        elif odds_table == 'tcbk_dxf':
            from app.database import TcbkDxf
            return TcbkDxf
        elif odds_table == 'tcbk_rfsf':
            from app.database import TcbkRfsf
            return TcbkRfsf
        elif odds_table == 'tcbk_spf':
            from app.database import TcbkSpf
            return TcbkSpf
        elif odds_table == 'tcbk_sfc':
            from app.database import TcbkSfc
            return TcbkSfc
        
        # 北京单场
        elif odds_table.startswith('bjdc_'):
            from app.database import (
                BjdcSpfOdds, 
                BjdcHandicapSpfOdds, 
                BjdcTotalGoalOdds, 
                BjdcScoreOdds, 
                BjdcHalfTimeFullTimeOdds
            )
            table_map = {
                'bjdc_spf_odds': BjdcSpfOdds,
                'bjdc_handicap_spf_odds': BjdcHandicapSpfOdds,
                'bjdc_total_goal_odds': BjdcTotalGoalOdds,
                'bjdc_score_odds': BjdcScoreOdds,
                'bjdc_ht_ft_odds': BjdcHalfTimeFullTimeOdds
            }
            return table_map.get(odds_table)
        
        else:
            log.warning(f"未知的赔率表: {odds_table}")
            return None
            
    except ImportError as e:
        log.error(f"导入模型类失败 ({odds_table}): {str(e)}")
        return None


def should_log_odds_change(odds_record_id: int, field_name: str, new_value: float, 
                           odds_table: str = None, sport_type: str = 'tczq', 
                           threshold: float = 0.05) -> tuple:
    """
    判断是否应该记录赔率变化
    
    业务逻辑：
    1. 计算当前赔率（考虑所有历史波动）
    2. 与新赔率比较
    3. 只有当差值超过阈值时才记录
    
    Args:
        odds_record_id: 赔率记录ID
        field_name: 赔率字段名
        new_value: 新获取的赔率值
        odds_table: 赔率表名
        sport_type: 赛事类型 ('tczq'=足球, 'tcbk'=篮球, 'bjdc'=北京单场)
        threshold: 变化阈值，默认0.05
    
    Returns:
        tuple: (should_log: bool, current_value: float, diff: float)
            - should_log: 是否应该记录
            - current_value: 当前赔率值
            - diff: 差值 (new_value - current_value)
    
    Examples:
        # 体彩足球
        should_log, current, diff = should_log_odds_change(
            odds_record_id=5,
            field_name='win_pl',
            new_value=3.05,
            odds_table='tczq_spf_odds',
            sport_type='tczq',
            threshold=0.05
        )
        
        # 竞彩篮球
        should_log, current, diff = should_log_odds_change(
            odds_record_id=10,
            field_name='over',
            new_value=1.95,
            odds_table='tcbk_dxf',
            sport_type='tcbk',
            threshold=0.05
        )
        
        if should_log:
            # 记录变化
            pass
    """
    try:
        # 计算当前赔率
        current_value = calculate_current_odds(odds_record_id, field_name, odds_table, sport_type)
        
        if current_value == 0.0:
            # 无法获取当前值，建议记录（可能是首次）
            log.debug(f"[{sport_type}] 无法获取当前赔率，建议记录: record_id={odds_record_id}, field={field_name}")
            return True, current_value, new_value
                # 计算差值（带符号，用于日志显示）
        diff = new_value - current_value
        
        # 判断是否超过阈值（使用绝对值）
        should_log = abs(diff) > threshold
        
        if should_log:
            log.debug(f"[{sport_type}] 赔率变化超过阈值: {odds_table}.{field_name} "
                     f"{current_value:.3f} -> {new_value:.3f} (diff={diff:.3f} > {threshold})")
        else:
            log.debug(f"[{sport_type}] 赔率变化未超阈值: {odds_table}.{field_name} "
                     f"{current_value:.3f} -> {new_value:.3f} (diff={diff:.3f} <= {threshold})")
        
        return should_log, current_value, diff
        
    except Exception as e:
        log.error(f"判断赔率变化失败: {str(e)}")
        # 出错时建议记录，避免遗漏重要变化
        return True, 0.0, new_value