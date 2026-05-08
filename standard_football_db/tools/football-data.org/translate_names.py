"""
中文名称映射工具
用于为英文数据添加中文翻译
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_json(filename):
    """加载JSON文件"""
    filepath = DATA_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filename):
    """保存JSON文件"""
    filepath = DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {filepath}")

# ==================== 中文名称映射表 ====================

# 国家中文名称映射
COUNTRY_ZH_MAP = {
    "England": "英格兰",
    "Spain": "西班牙",
    "Germany": "德国",
    "Italy": "意大利",
    "France": "法国",
    "Brazil": "巴西",
    "Netherlands": "荷兰",
    "Portugal": "葡萄牙",
    "Europe": "欧洲",
    "South America": "南美洲",
    "World": "世界",
    # 可以继续添加...
}

# 联赛中文名称映射
LEAGUE_ZH_MAP = {
    "Premier League": {
        "full": "英格兰超级联赛",
        "short": "英超"
    },
    "Championship": {
        "full": "英格兰冠军联赛",
        "short": "英冠"
    },
    "Primera Division": {
        "full": "西班牙甲级联赛",
        "short": "西甲"
    },
    "Bundesliga": {
        "full": "德国甲级联赛",
        "short": "德甲"
    },
    "Serie A": {
        "full": "意大利甲级联赛",
        "short": "意甲"
    },
    "Ligue 1": {
        "full": "法国甲级联赛",
        "short": "法甲"
    },
    "Eredivisie": {
        "full": "荷兰甲级联赛",
        "short": "荷甲"
    },
    "Primeira Liga": {
        "full": "葡萄牙超级联赛",
        "short": "葡超"
    },
    "Campeonato Brasileiro Série A": {
        "full": "巴西甲级联赛",
        "short": "巴甲"
    },
    "UEFA Champions League": {
        "full": "欧洲冠军联赛",
        "short": "欧冠"
    },
    "European Championship": {
        "full": "欧洲足球锦标赛",
        "short": "欧洲杯"
    },
    "Copa Libertadores": {
        "full": "南美解放者杯",
        "short": "解放者杯"
    },
    "FIFA World Cup": {
        "full": "国际足联世界杯",
        "short": "世界杯"
    },
}

# 球队中文名称映射（示例，需要补充完整）
TEAM_ZH_MAP = {
    "Arsenal FC": {
        "full": "阿森纳足球俱乐部",
        "short": "阿森纳"
    },
    "Liverpool FC": {
        "full": "利物浦足球俱乐部",
        "short": "利物浦"
    },
    "Manchester United FC": {
        "full": "曼彻斯特联足球俱乐部",
        "short": "曼联"
    },
    "Manchester City FC": {
        "full": "曼彻斯特城足球俱乐部",
        "short": "曼城"
    },
    "Chelsea FC": {
        "full": "切尔西足球俱乐部",
        "short": "切尔西"
    },
    # 可以继续添加更多球队...
}

def translate_countries():
    """翻译国家名称"""
    print("\n" + "="*80)
    print("翻译国家/地区名称")
    print("="*80)
    
    countries = load_json('countries.json')
    updated_count = 0
    
    for country in countries:
        name_en = country.get('name_en')
        if name_en and name_en in COUNTRY_ZH_MAP:
            country['name_zh'] = COUNTRY_ZH_MAP[name_en]
            updated_count += 1
        
        parent_en = country.get('parent_area_name_en')
        if parent_en and parent_en in COUNTRY_ZH_MAP:
            country['parent_area_name_zh'] = COUNTRY_ZH_MAP[parent_en]
    
    save_json(countries, 'countries.json')
    print(f"✓ 已翻译 {updated_count} 个国家/地区")

def translate_leagues():
    """翻译联赛名称"""
    print("\n" + "="*80)
    print("翻译联赛名称")
    print("="*80)
    
    leagues = load_json('leagues.json')
    updated_count = 0
    
    for league in leagues:
        name_en = league.get('name_en')
        if name_en and name_en in LEAGUE_ZH_MAP:
            league['name_zh'] = LEAGUE_ZH_MAP[name_en]['short']
            league['name_zh_full'] = LEAGUE_ZH_MAP[name_en]['full']
            updated_count += 1
        
        area_en = league.get('area_name_en')
        if area_en and area_en in COUNTRY_ZH_MAP:
            league['area_name_zh'] = COUNTRY_ZH_MAP[area_en]
    
    save_json(leagues, 'leagues.json')
    print(f"✓ 已翻译 {updated_count} 个联赛")

def translate_teams():
    """翻译球队名称"""
    print("\n" + "="*80)
    print("翻译球队名称")
    print("="*80)
    
    teams = load_json('teams_with_players.json')
    updated_count = 0
    
    for team in teams:
        name_en = team.get('name_en')
        if name_en and name_en in TEAM_ZH_MAP:
            team['name_zh'] = TEAM_ZH_MAP[name_en]['short']
            team['name_zh_full'] = TEAM_ZH_MAP[name_en]['full']
            updated_count += 1
        
        area_en = team.get('area_name_en')
        if area_en and area_en in COUNTRY_ZH_MAP:
            team['area_name_zh'] = COUNTRY_ZH_MAP[area_en]
    
    save_json(teams, 'teams_with_players.json')
    print(f"✓ 已翻译 {updated_count} 支球队")
    print(f"⚠ 注意: 还有 {len(teams) - updated_count} 支球队需要手动添加中文映射")

def show_statistics():
    """显示翻译统计"""
    print("\n" + "="*80)
    print("翻译统计")
    print("="*80)
    
    countries = load_json('countries.json')
    leagues = load_json('leagues.json')
    teams = load_json('teams_with_players.json')
    
    # 统计已翻译的数量
    countries_translated = sum(1 for c in countries if c.get('name_zh'))
    leagues_translated = sum(1 for l in leagues if l.get('name_zh'))
    teams_translated = sum(1 for t in teams if t.get('name_zh'))
    
    print(f"\n国家/地区: {countries_translated}/{len(countries)} 已翻译")
    print(f"联赛: {leagues_translated}/{len(leagues)} 已翻译")
    print(f"球队: {teams_translated}/{len(teams)} 已翻译")
    
    # 列出未翻译的球队
    untranslated_teams = [t for t in teams if not t.get('name_zh')]
    if untranslated_teams:
        print(f"\n未翻译的球队示例 (前10个):")
        for team in untranslated_teams[:10]:
            print(f"  - {team.get('name_en')} ({team.get('league_code')})")

def main():
    print("="*80)
    print("中文名称映射工具")
    print("="*80)
    
    try:
        # 1. 翻译国家
        translate_countries()
        
        # 2. 翻译联赛
        translate_leagues()
        
        # 3. 翻译球队
        translate_teams()
        
        # 4. 显示统计
        show_statistics()
        
        print("\n" + "="*80)
        print("✓ 翻译完成！")
        print("="*80)
        print("\n提示:")
        print("1. 可以在 TEAM_ZH_MAP 中添加更多球队的中文映射")
        print("2. 运行此脚本会更新 data/ 目录下的JSON文件")
        print("3. 建议定期更新映射表以覆盖更多球队")
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
