# -*- coding: utf-8 -*-
"""
联赛分类数据初始化脚本
初始化地区、国家、等级三个分类表的基础数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.database.base_models import LeagueRegion, LeagueCountry, LeagueLevel
from app.database import localdb


def init_league_regions():
    """初始化地区数据"""
    regions = [
        {'region_code': 'ASIA', 'region_name': '亚洲', 'region_name_en': 'Asia', 'description': '亚洲地区联赛'},
        {'region_code': 'EUROPE', 'region_name': '欧洲', 'region_name_en': 'Europe', 'description': '欧洲地区联赛'},
        {'region_code': 'SOUTH_AMERICA', 'region_name': '南美洲', 'region_name_en': 'South America', 'description': '南美洲地区联赛'},
        {'region_code': 'NORTH_AMERICA', 'region_name': '北美洲', 'region_name_en': 'North America', 'description': '北美洲及中美洲地区联赛'},
        {'region_code': 'AFRICA', 'region_name': '非洲', 'region_name_en': 'Africa', 'description': '非洲地区联赛'},
        {'region_code': 'OCEANIA', 'region_name': '大洋洲', 'region_name_en': 'Oceania', 'description': '大洋洲地区联赛'},
        {'region_code': 'INTERNATIONAL', 'region_name': '国际', 'region_name_en': 'International', 'description': '国际性赛事（如世界杯、欧冠等）'},
    ]
    
    count = 0
    for region_data in regions:
        existing = localdb.query(LeagueRegion).filter_by(region_code=region_data['region_code']).first()
        if not existing:
            region = LeagueRegion(**region_data)
            localdb.add(region)
            count += 1
    
    localdb.commit()
    print(f"✓ 地区数据初始化完成，新增 {count} 个地区")
    return count


def init_league_countries():
    """初始化国家数据（完整版，包含75+个国家）"""
    # 先查询地区ID映射
    region_map = {}
    regions = localdb.query(LeagueRegion).all()
    for r in regions:
        region_map[r.region_code] = r.id
    
    countries = [
        # 亚洲 (16个)
        {'country_code': 'CHN', 'country_name': '中国', 'country_name_en': 'China', 'region_id': region_map.get('ASIA'), 'fifa_code': 'CHN', 'iso_code': 'CN'},
        {'country_code': 'JPN', 'country_name': '日本', 'country_name_en': 'Japan', 'region_id': region_map.get('ASIA'), 'fifa_code': 'JPN', 'iso_code': 'JP'},
        {'country_code': 'KOR', 'country_name': '韩国', 'country_name_en': 'South Korea', 'region_id': region_map.get('ASIA'), 'fifa_code': 'KOR', 'iso_code': 'KR'},
        {'country_code': 'AUS', 'country_name': '澳大利亚', 'country_name_en': 'Australia', 'region_id': region_map.get('ASIA'), 'fifa_code': 'AUS', 'iso_code': 'AU'},
        {'country_code': 'SAU', 'country_name': '沙特阿拉伯', 'country_name_en': 'Saudi Arabia', 'region_id': region_map.get('ASIA'), 'fifa_code': 'KSA', 'iso_code': 'SA'},
        {'country_code': 'IRN', 'country_name': '伊朗', 'country_name_en': 'Iran', 'region_id': region_map.get('ASIA'), 'fifa_code': 'IRN', 'iso_code': 'IR'},
        {'country_code': 'QAT', 'country_name': '卡塔尔', 'country_name_en': 'Qatar', 'region_id': region_map.get('ASIA'), 'fifa_code': 'QAT', 'iso_code': 'QA'},
        {'country_code': 'UAE', 'country_name': '阿联酋', 'country_name_en': 'United Arab Emirates', 'region_id': region_map.get('ASIA'), 'fifa_code': 'UAE', 'iso_code': 'AE'},
        {'country_code': 'IRQ', 'country_name': '伊拉克', 'country_name_en': 'Iraq', 'region_id': region_map.get('ASIA'), 'fifa_code': 'IRQ', 'iso_code': 'IQ'},
        {'country_code': 'UZB', 'country_name': '乌兹别克斯坦', 'country_name_en': 'Uzbekistan', 'region_id': region_map.get('ASIA'), 'fifa_code': 'UZB', 'iso_code': 'UZ'},
        {'country_code': 'THA', 'country_name': '泰国', 'country_name_en': 'Thailand', 'region_id': region_map.get('ASIA'), 'fifa_code': 'THA', 'iso_code': 'TH'},
        {'country_code': 'VIE', 'country_name': '越南', 'country_name_en': 'Vietnam', 'region_id': region_map.get('ASIA'), 'fifa_code': 'VIE', 'iso_code': 'VN'},
        {'country_code': 'IDN', 'country_name': '印度尼西亚', 'country_name_en': 'Indonesia', 'region_id': region_map.get('ASIA'), 'fifa_code': 'IDN', 'iso_code': 'ID'},
        {'country_code': 'MYS', 'country_name': '马来西亚', 'country_name_en': 'Malaysia', 'region_id': region_map.get('ASIA'), 'fifa_code': 'MAS', 'iso_code': 'MY'},
        {'country_code': 'SGP', 'country_name': '新加坡', 'country_name_en': 'Singapore', 'region_id': region_map.get('ASIA'), 'fifa_code': 'SIN', 'iso_code': 'SG'},
        {'country_code': 'IND', 'country_name': '印度', 'country_name_en': 'India', 'region_id': region_map.get('ASIA'), 'fifa_code': 'IND', 'iso_code': 'IN'},
        
        # 欧洲 (30个)
        {'country_code': 'ENG', 'country_name': '英格兰', 'country_name_en': 'England', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'ENG', 'iso_code': 'GB-ENG'},
        {'country_code': 'ESP', 'country_name': '西班牙', 'country_name_en': 'Spain', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'ESP', 'iso_code': 'ES'},
        {'country_code': 'GER', 'country_name': '德国', 'country_name_en': 'Germany', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'GER', 'iso_code': 'DE'},
        {'country_code': 'ITA', 'country_name': '意大利', 'country_name_en': 'Italy', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'ITA', 'iso_code': 'IT'},
        {'country_code': 'FRA', 'country_name': '法国', 'country_name_en': 'France', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'FRA', 'iso_code': 'FR'},
        {'country_code': 'POR', 'country_name': '葡萄牙', 'country_name_en': 'Portugal', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'POR', 'iso_code': 'PT'},
        {'country_code': 'NED', 'country_name': '荷兰', 'country_name_en': 'Netherlands', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'NED', 'iso_code': 'NL'},
        {'country_code': 'BEL', 'country_name': '比利时', 'country_name_en': 'Belgium', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'BEL', 'iso_code': 'BE'},
        {'country_code': 'TUR', 'country_name': '土耳其', 'country_name_en': 'Turkey', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'TUR', 'iso_code': 'TR'},
        {'country_code': 'SCO', 'country_name': '苏格兰', 'country_name_en': 'Scotland', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'SCO', 'iso_code': 'GB-SCT'},
        {'country_code': 'GRE', 'country_name': '希腊', 'country_name_en': 'Greece', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'GRE', 'iso_code': 'GR'},
        {'country_code': 'RUS', 'country_name': '俄罗斯', 'country_name_en': 'Russia', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'RUS', 'iso_code': 'RU'},
        {'country_code': 'UKR', 'country_name': '乌克兰', 'country_name_en': 'Ukraine', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'UKR', 'iso_code': 'UA'},
        {'country_code': 'POL', 'country_name': '波兰', 'country_name_en': 'Poland', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'POL', 'iso_code': 'PL'},
        {'country_code': 'CZE', 'country_name': '捷克', 'country_name_en': 'Czech Republic', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'CZE', 'iso_code': 'CZ'},
        {'country_code': 'AUT', 'country_name': '奥地利', 'country_name_en': 'Austria', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'AUT', 'iso_code': 'AT'},
        {'country_code': 'SUI', 'country_name': '瑞士', 'country_name_en': 'Switzerland', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'SUI', 'iso_code': 'CH'},
        {'country_code': 'DEN', 'country_name': '丹麦', 'country_name_en': 'Denmark', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'DEN', 'iso_code': 'DK'},
        {'country_code': 'SWE', 'country_name': '瑞典', 'country_name_en': 'Sweden', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'SWE', 'iso_code': 'SE'},
        {'country_code': 'NOR', 'country_name': '挪威', 'country_name_en': 'Norway', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'NOR', 'iso_code': 'NO'},
        {'country_code': 'CRO', 'country_name': '克罗地亚', 'country_name_en': 'Croatia', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'CRO', 'iso_code': 'HR'},
        {'country_code': 'SRB', 'country_name': '塞尔维亚', 'country_name_en': 'Serbia', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'SRB', 'iso_code': 'RS'},
        {'country_code': 'ROU', 'country_name': '罗马尼亚', 'country_name_en': 'Romania', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'ROU', 'iso_code': 'RO'},
        {'country_code': 'BUL', 'country_name': '保加利亚', 'country_name_en': 'Bulgaria', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'BUL', 'iso_code': 'BG'},
        {'country_code': 'HUN', 'country_name': '匈牙利', 'country_name_en': 'Hungary', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'HUN', 'iso_code': 'HU'},
        {'country_code': 'SVK', 'country_name': '斯洛伐克', 'country_name_en': 'Slovakia', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'SVK', 'iso_code': 'SK'},
        {'country_code': 'FIN', 'country_name': '芬兰', 'country_name_en': 'Finland', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'FIN', 'iso_code': 'FI'},
        {'country_code': 'ISL', 'country_name': '冰岛', 'country_name_en': 'Iceland', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'ISL', 'iso_code': 'IS'},
        {'country_code': 'IRL', 'country_name': '爱尔兰', 'country_name_en': 'Ireland', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'IRL', 'iso_code': 'IE'},
        {'country_code': 'WAL', 'country_name': '威尔士', 'country_name_en': 'Wales', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'WAL', 'iso_code': 'GB-WLS'},
        {'country_code': 'NIR', 'country_name': '北爱尔兰', 'country_name_en': 'Northern Ireland', 'region_id': region_map.get('EUROPE'), 'fifa_code': 'NIR', 'iso_code': 'GB-NIR'},
        
        # 南美洲 (10个)
        {'country_code': 'BRA', 'country_name': '巴西', 'country_name_en': 'Brazil', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'BRA', 'iso_code': 'BR'},
        {'country_code': 'ARG', 'country_name': '阿根廷', 'country_name_en': 'Argentina', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'ARG', 'iso_code': 'AR'},
        {'country_code': 'URU', 'country_name': '乌拉圭', 'country_name_en': 'Uruguay', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'URU', 'iso_code': 'UY'},
        {'country_code': 'COL', 'country_name': '哥伦比亚', 'country_name_en': 'Colombia', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'COL', 'iso_code': 'CO'},
        {'country_code': 'CHI', 'country_name': '智利', 'country_name_en': 'Chile', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'CHI', 'iso_code': 'CL'},
        {'country_code': 'PAR', 'country_name': '巴拉圭', 'country_name_en': 'Paraguay', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'PAR', 'iso_code': 'PY'},
        {'country_code': 'ECU', 'country_name': '厄瓜多尔', 'country_name_en': 'Ecuador', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'ECU', 'iso_code': 'EC'},
        {'country_code': 'PER', 'country_name': '秘鲁', 'country_name_en': 'Peru', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'PER', 'iso_code': 'PE'},
        {'country_code': 'VEN', 'country_name': '委内瑞拉', 'country_name_en': 'Venezuela', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'VEN', 'iso_code': 'VE'},
        {'country_code': 'BOL', 'country_name': '玻利维亚', 'country_name_en': 'Bolivia', 'region_id': region_map.get('SOUTH_AMERICA'), 'fifa_code': 'BOL', 'iso_code': 'BO'},
        
        # 北美洲 (5个)
        {'country_code': 'USA', 'country_name': '美国', 'country_name_en': 'United States', 'region_id': region_map.get('NORTH_AMERICA'), 'fifa_code': 'USA', 'iso_code': 'US'},
        {'country_code': 'MEX', 'country_name': '墨西哥', 'country_name_en': 'Mexico', 'region_id': region_map.get('NORTH_AMERICA'), 'fifa_code': 'MEX', 'iso_code': 'MX'},
        {'country_code': 'CAN', 'country_name': '加拿大', 'country_name_en': 'Canada', 'region_id': region_map.get('NORTH_AMERICA'), 'fifa_code': 'CAN', 'iso_code': 'CA'},
        {'country_code': 'CRC', 'country_name': '哥斯达黎加', 'country_name_en': 'Costa Rica', 'region_id': region_map.get('NORTH_AMERICA'), 'fifa_code': 'CRC', 'iso_code': 'CR'},
        {'country_code': 'PAN', 'country_name': '巴拿马', 'country_name_en': 'Panama', 'region_id': region_map.get('NORTH_AMERICA'), 'fifa_code': 'PAN', 'iso_code': 'PA'},
        
        # 非洲 (10个)
        {'country_code': 'EGY', 'country_name': '埃及', 'country_name_en': 'Egypt', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'EGY', 'iso_code': 'EG'},
        {'country_code': 'NGA', 'country_name': '尼日利亚', 'country_name_en': 'Nigeria', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'NGA', 'iso_code': 'NG'},
        {'country_code': 'MAR', 'country_name': '摩洛哥', 'country_name_en': 'Morocco', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'MAR', 'iso_code': 'MA'},
        {'country_code': 'TUN', 'country_name': '突尼斯', 'country_name_en': 'Tunisia', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'TUN', 'iso_code': 'TN'},
        {'country_code': 'ALG', 'country_name': '阿尔及利亚', 'country_name_en': 'Algeria', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'ALG', 'iso_code': 'DZ'},
        {'country_code': 'SEN', 'country_name': '塞内加尔', 'country_name_en': 'Senegal', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'SEN', 'iso_code': 'SN'},
        {'country_code': 'CMR', 'country_name': '喀麦隆', 'country_name_en': 'Cameroon', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'CMR', 'iso_code': 'CM'},
        {'country_code': 'GHA', 'country_name': '加纳', 'country_name_en': 'Ghana', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'GHA', 'iso_code': 'GH'},
        {'country_code': 'CIV', 'country_name': '科特迪瓦', 'country_name_en': 'Ivory Coast', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'CIV', 'iso_code': 'CI'},
        {'country_code': 'RSA', 'country_name': '南非', 'country_name_en': 'South Africa', 'region_id': region_map.get('AFRICA'), 'fifa_code': 'RSA', 'iso_code': 'ZA'},
        
        # 大洋洲 (1个)
        {'country_code': 'NZL', 'country_name': '新西兰', 'country_name_en': 'New Zealand', 'region_id': region_map.get('OCEANIA'), 'fifa_code': 'NZL', 'iso_code': 'NZ'},
        
        # 国际赛事（无具体国家）
        {'country_code': 'INTL', 'country_name': '国际', 'country_name_en': 'International', 'region_id': region_map.get('INTERNATIONAL'), 'fifa_code': None, 'iso_code': None},
    ]
    
    count = 0
    for country_data in countries:
        existing = localdb.query(LeagueCountry).filter_by(country_code=country_data['country_code']).first()
        if not existing:
            country = LeagueCountry(**country_data)
            localdb.add(country)
            count += 1
    
    localdb.commit()
    print(f"✓ 国家数据初始化完成，新增 {count} 个国家")
    return count


def init_league_levels():
    """初始化等级数据"""
    levels = [
        {'level_code': 'TIER_1', 'level_name': '顶级联赛', 'level_name_en': 'Top Tier', 'sort_order': 1, 'description': '各国最高级别联赛'},
        {'level_code': 'TIER_2', 'level_name': '二级联赛', 'level_name_en': 'Second Tier', 'sort_order': 2, 'description': '各国第二级别联赛'},
        {'level_code': 'TIER_3', 'level_name': '三级联赛', 'level_name_en': 'Third Tier', 'sort_order': 3, 'description': '各国第三级别联赛'},
        {'level_code': 'TIER_4', 'level_name': '四级联赛', 'level_name_en': 'Fourth Tier', 'sort_order': 4, 'description': '各国第四级别联赛'},
        {'level_code': 'CUP', 'level_name': '杯赛', 'level_name_en': 'Cup', 'sort_order': 10, 'description': '各国国内杯赛'},
        {'level_code': 'SUPER_CUP', 'level_name': '超级杯', 'level_name_en': 'Super Cup', 'sort_order': 11, 'description': '超级杯赛事'},
        {'level_code': 'LEAGUE_CUP', 'level_name': '联赛杯', 'level_name_en': 'League Cup', 'sort_order': 12, 'description': '联赛杯赛事'},
        {'level_code': 'YOUTH', 'level_name': '青年联赛', 'level_name_en': 'Youth League', 'sort_order': 20, 'description': '青年队联赛'},
        {'level_code': 'RESERVE', 'level_name': '预备队联赛', 'level_name_en': 'Reserve League', 'sort_order': 21, 'description': '预备队联赛'},
        {'level_code': 'WOMEN', 'level_name': '女子联赛', 'level_name_en': "Women's League", 'sort_order': 30, 'description': '女子足球联赛'},
    ]
    
    count = 0
    for level_data in levels:
        existing = localdb.query(LeagueLevel).filter_by(level_code=level_data['level_code']).first()
        if not existing:
            level = LeagueLevel(**level_data)
            localdb.add(level)
            count += 1
    
    localdb.commit()
    print(f"✓ 等级数据初始化完成，新增 {count} 个等级")
    return count


def init_league_classification():
    """
    初始化联赛分类表
    Returns:
        bool: 初始化是否成功
    """
    print("=" * 80)
    print("开始初始化联赛分类表数据")
    print("=" * 80)
    
    try:
        # 1. 初始化地区
        print("\n【1】初始化地区数据...")
        region_count = init_league_regions()
        
        # 2. 初始化国家
        print("\n【2】初始化国家数据...")
        country_count = init_league_countries()
        
        # 3. 初始化等级
        print("\n【3】初始化等级数据...")
        level_count = init_league_levels()
        
        print("\n" + "=" * 80)
        print("联赛分类表初始化完成！")
        print(f"  - 地区: {region_count} 条")
        print(f"  - 国家: {country_count} 条")
        print(f"  - 等级: {level_count} 条")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 联赛分类表初始化失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = init_league_classification()
    if success:
        print("\n✅ 所有操作完成!")
    else:
        print("\n❌ 操作失败，请检查错误信息")
