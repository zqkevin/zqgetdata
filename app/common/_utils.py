# -*- coding: utf-8 -*-
import random
import string
import time
import traceback
from .logger import log
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry


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
    homegoal = int(homegoal)
    awaygoal = int(awaygoal)
    if homegoal > awaygoal:
        spf = match.pl.winpl
    elif homegoal == awaygoal:
        spf = match.pl.drawpl
    else:
        spf = match.pl.losepl
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
    return spf, zjq, bifen

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