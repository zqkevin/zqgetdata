# -*- coding: utf-8 -*-
"""
扩展关键词映射并重新匹配未匹配的联赛
"""
import sys
import os

# 添加项目根目录到 Python 路径（从 app/common/ 回到项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config import config

from app.database.base_models import League, LeagueRegion, LeagueCountry, LeagueLevel
from app.database import localdb


def build_extended_keyword_mapping():
    """构建扩展的关键词映射（包含新增的关键词）"""
    
    # 国际赛事关键词（优先级最高）
    international_keywords = {
        '洲际杯': {'country_code': 'INTL', 'level_code': 'CUP'},
        '中北美冠': {'country_code': 'INTL', 'level_code': 'CUP'},
        '世欧预': {'country_code': 'INTL', 'level_code': 'CUP'},
        '世亚预': {'country_code': 'INTL', 'level_code': 'CUP'},
        '世预附加': {'country_code': 'INTL', 'level_code': 'CUP'},
        '亚冠二级': {'country_code': 'INTL', 'level_code': 'CUP'},
        'U21欧预赛': {'country_code': 'INTL', 'level_code': 'CUP'},
        '南超杯': {'country_code': 'INTL', 'level_code': 'SUPER_CUP'},
    }
    
    # 国家关键词映射（扩展版）
    country_keywords = {
        # 亚洲
        'CHN': ['中超', '中甲', '足协杯', '中国'],
        'JPN': ['日职', '日乙', '天皇杯', '日联杯', '日本', 'J1联赛', 'J2联赛', 'J1', 'J2'],
        'KOR': ['韩职', '韩K', '韩足总', '韩国', 'K1联赛', 'K2联赛', 'K1', 'K2'],
        'AUS': ['澳超', '澳大利亚'],
        'SAU': ['沙职', '沙特'],
        'IRN': ['伊朗超', '伊朗'],
        'QAT': ['卡塔尔', '卡塔'],
        'UAE': ['阿联', '阿联酋'],
        'IRQ': ['伊拉克'],
        'UZB': ['乌兹别克斯坦'],
        'THA': ['泰超', '泰国'],
        'VIE': ['越南'],
        'IDN': ['印尼', '印度尼西亚'],
        'MYS': ['马来西亚'],
        'SGP': ['新加坡'],
        'IND': ['印度'],
        
        # 欧洲
        'ENG': ['英超', '英冠', '英甲', '英乙', '足总杯', '联赛杯', '英锦赛', '英格兰', '英联杯'],
        'ESP': ['西甲', '西乙', '国王杯', '西班牙', '西超杯'],
        'GER': ['德甲', '德乙', '德国杯', '德国'],
        'ITA': ['意甲', '意乙', '意大利杯', '意大利', '意超杯'],
        'FRA': ['法甲', '法乙', '法国杯', '法国', '法超杯'],
        'POR': ['葡超', '葡甲', '葡萄牙杯', '葡联杯', '葡萄牙'],
        'NED': ['荷甲', '荷乙', '荷兰杯', '荷兰'],
        'BEL': ['比甲', '比乙', '比利时杯', '比利时'],
        'TUR': ['土超', '土耳其'],
        'SCO': ['苏超', '苏冠', '苏格兰'],
        'GRE': ['希腊超', '希腊杯', '希腊'],
        'RUS': ['俄超', '俄罗斯'],
        'UKR': ['乌超', '乌克兰'],
        'POL': ['波兰甲', '波兰杯', '波兰'],
        'CZE': ['捷克甲', '捷克杯', '捷克'],
        'AUT': ['奥甲', '奥乙', '奥地利'],
        'SUI': ['瑞士超', '瑞士甲', '瑞士'],
        'DEN': ['丹超', '丹甲', '丹麦杯', '丹麦'],
        'SWE': ['瑞超', '瑞甲', '瑞典杯', '瑞典'],
        'NOR': ['挪超', '挪甲', '挪威杯', '挪威'],
        'CRO': ['克亚甲', '克罗地亚'],
        'SRB': ['塞超', '塞尔维亚'],
        'ROU': ['罗甲', '罗马尼亚杯', '罗马尼亚'],
        'BUL': ['保加利亚'],
        'HUN': ['匈牙利'],
        'SVK': ['斯洛伐克'],
        'FIN': ['芬超', '芬甲', '芬兰', '芬联杯'],
        'IRL': ['爱超', '爱尔兰'],
        'WAL': ['威尔士'],
        'NIR': ['北爱尔兰'],
        'ISL': ['冰岛超', '冰岛'],
        
        # 南美洲
        'BRA': ['巴甲', '巴西杯', '巴西', '巴超杯'],
        'ARG': ['阿职联', '阿根廷杯', '阿根廷'],
        'URU': ['乌拉圭'],
        'COL': ['哥伦比亚'],
        'CHI': ['智利甲', '智利'],
        'PAR': ['巴拉圭'],
        'ECU': ['厄瓜多尔'],
        'PER': ['秘鲁'],
        'VEN': ['委内瑞拉'],
        'BOL': ['玻利维亚'],
        
        # 北美洲
        'USA': ['美职', '美公杯', '美国'],
        'MEX': ['墨超', '墨西哥'],
        'CAN': ['加拿大'],
        'CRC': ['哥斯达黎加'],
        'PAN': ['巴拿马'],
        
        # 非洲
        'EGY': ['埃及超', '埃及'],
        'NGA': ['尼日利亚'],
        'MAR': ['摩洛哥'],
        'TUN': ['突尼斯'],
        'ALG': ['阿尔及利亚'],
        'SEN': ['塞内加尔'],
        'CMR': ['喀麦隆'],
        'GHA': ['加纳'],
        'CIV': ['科特迪瓦'],
        'RSA': ['南非超', '南非'],
        
        # 大洋洲
        'NZL': ['新西兰'],
    }
    
    # 等级关键词映射（扩展版）
    level_keywords = {
        '超级联赛': 'TIER_1',
        '甲级联赛': 'TIER_1',
        '职业联赛': 'TIER_1',
        '超': 'TIER_1',
        '甲': 'TIER_1',
        '乙级联赛': 'TIER_2',
        '乙': 'TIER_2',
        '丙级联赛': 'TIER_3',
        '丙': 'TIER_3',
        '杯': 'CUP',
        '杯赛': 'CUP',
        '超级杯': 'SUPER_CUP',
        '联赛杯': 'LEAGUE_CUP',
        '青年': 'YOUTH',
        '预备队': 'RESERVE',
        '女子': 'WOMEN',
    }
    
    return international_keywords, country_keywords, level_keywords


def match_league_to_country(league_name, league_abbr, international_kw, country_kw):
    """匹配联赛到国家代码（优先匹配国际赛事）"""
    
    # 先检查是否是国际赛事
    for keyword, mapping in international_kw.items():
        if keyword in league_name or keyword in league_abbr:
            return mapping['country_code'], mapping['level_code']
    
    # 再匹配国家
    best_match = None
    best_score = 0
    
    for country_code, keywords in country_kw.items():
        score = 0
        for keyword in keywords:
            if keyword in league_name:
                score += len(keyword)  # 长关键词权重更高
            elif keyword in league_abbr:
                score += len(keyword) * 0.8
        
        if score > best_score:
            best_score = score
            best_match = country_code
    
    return best_match, None


def match_league_to_level(league_name, league_abbr, level_kw, matched_international_level=None):
    """匹配联赛到等级代码"""
    
    # 如果已经通过国际赛事匹配到了等级，直接返回
    if matched_international_level:
        return matched_international_level
    
    best_match = None
    best_score = 0
    
    for keyword, level_code in level_kw.items():
        score = 0
        if keyword in league_name or keyword in league_abbr:
            score = len(keyword)
        
        if score > best_score:
            best_score = score
            best_match = level_code
    
    # 默认等级
    if not best_match:
        best_match = 'TIER_1'
    
    return best_match


def update_league_classification():
    """更新联赛分类"""
    print("=" * 120)
    print("开始扩展关键词匹配并更新联赛分类")
    print("=" * 120)
    
    # 获取所有未匹配的联赛
    unmatched_leagues = localdb.query(League).filter(League.region_id.is_(None)).all()
    print(f"\n找到 {len(unmatched_leagues)} 个未匹配的联赛\n")
    
    if not unmatched_leagues:
        print("✓ 所有联赛都已匹配，无需更新")
        return 0
    
    # 构建扩展的关键词映射
    international_kw, country_kw, level_kw = build_extended_keyword_mapping()
    
    # 查询分类表数据
    countries = localdb.query(LeagueCountry).all()
    country_map = {c.country_code: c.id for c in countries}
    
    regions = localdb.query(LeagueRegion).all()
    region_map = {r.region_code: r.id for r in regions}
    
    levels = localdb.query(LeagueLevel).all()
    level_map = {l.level_code: l.id for l in levels}
    
    # 执行匹配和更新
    updated_count = 0
    still_unmatched = []
    
    for league in unmatched_leagues:
        league_name = league.league_name or ''
        league_abbr = league.league_name_abbr or ''
        
        # 匹配国家和等级
        country_code, international_level = match_league_to_country(
            league_name, league_abbr, international_kw, country_kw
        )
        
        if country_code and country_code in country_map:
            country_id = country_map[country_code]
            
            # 根据国家获取地区
            country_obj = localdb.query(LeagueCountry).filter_by(country_code=country_code).first()
            region_id = country_obj.region_id if country_obj else None
            
            # 匹配等级
            level_code = match_league_to_level(
                league_name, league_abbr, level_kw, international_level
            )
            level_id = level_map.get(level_code)
            
            # 更新联赛
            league.region_id = region_id
            league.country_id = country_id
            league.level_id = level_id
            
            updated_count += 1
            print(f"✓ {league_name:30s} ({league_abbr:10s}) → {country_obj.country_name}")
        else:
            still_unmatched.append(league)
            print(f"✗ {league_name:30s} ({league_abbr:10s}) - 未匹配")
    
    # 提交事务
    if updated_count > 0:
        localdb.commit()
        print("\n" + "=" * 120)
        print(f"✅ 成功更新 {updated_count} 个联赛的分类")
        
        if still_unmatched:
            print(f"\n⚠️  仍有 {len(still_unmatched)} 个联赛未能匹配：")
            for league in still_unmatched:
                print(f"  - {league.league_name} ({league.league_name_abbr})")
    else:
        print("\n❌ 没有联赛被更新")
    
    print("=" * 120)
    
    return updated_count


if __name__ == '__main__':
    count = update_league_classification()
    print(f"\n{'='*120}")
    print(f"完成！共更新 {count} 个联赛")
    print(f"{'='*120}")
