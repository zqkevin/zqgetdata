"""
扩展数据源管理
用于补充 football-data.org 未覆盖的联赛和球队
"""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"

def load_json(filename):
    """加载JSON文件"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(data, filename):
    """保存JSON文件"""
    filepath = DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {filepath}")

# ==================== 扩展联赛数据示例 ====================

EXTENDED_LEAGUES = [
    {
        "id": 3001,
        "name_en": "J1 League",
        "name_en_full": "Meiji Yasuda J1 League",
        "name_zh": "日职联",
        "name_zh_full": "日本职业足球甲级联赛",
        "code": "J1",
        "type": "LEAGUE",
        "emblem": None,
        "area_id": 2088,
        "area_name_en": "Japan",
        "area_name_zh": "日本",
        "area_code": "JPN",
        "tier": 1,  # 联赛级别
        "current_season": {
            "start_date": "2024-02-23",
            "end_date": "2024-12-07",
            "current_matchday": None
        }
    },
    {
        "id": 3002,
        "name_en": "K League 1",
        "name_en_full": "Hana Bank K League 1",
        "name_zh": "韩K联",
        "name_zh_full": "韩国职业足球经典联赛",
        "code": "KL1",
        "type": "LEAGUE",
        "emblem": None,
        "area_id": 2097,
        "area_name_en": "South Korea",
        "area_name_zh": "韩国",
        "area_code": "KOR",
        "tier": 1,
        "current_season": {
            "start_date": "2024-03-01",
            "end_date": "2024-12-01",
            "current_matchday": None
        }
    },
    {
        "id": 3003,
        "name_en": "Saudi Pro League",
        "name_en_full": "Roshn Saudi League",
        "name_zh": "沙职联",
        "name_zh_full": "沙特职业足球联赛",
        "code": "SPL",
        "type": "LEAGUE",
        "emblem": None,
        "area_id": 2182,
        "area_name_en": "Saudi Arabia",
        "area_name_zh": "沙特阿拉伯",
        "area_code": "SAU",
        "tier": 1,
        "current_season": {
            "start_date": "2024-08-22",
            "end_date": "2025-05-27",
            "current_matchday": None
        }
    },
    {
        "id": 3004,
        "name_en": "Chinese Super League",
        "name_en_full": "China Ping An Chinese Football Association Super League",
        "name_zh": "中超",
        "name_zh_full": "中国足球协会超级联赛",
        "code": "CSL",
        "type": "LEAGUE",
        "emblem": None,
        "area_id": 2044,
        "area_name_en": "China",
        "area_name_zh": "中国",
        "area_code": "CHN",
        "tier": 1,
        "current_season": {
            "start_date": "2024-03-01",
            "end_date": "2024-11-02",
            "current_matchday": None
        }
    }
]

# ==================== 扩展球队数据示例 ====================

EXTENDED_TEAMS = {
    "J1": [  # 日职联球队示例
        {
            "id": 4001,
            "name_en": "Vissel Kobe",
            "name_en_full": "Vissel Kobe",
            "name_en_short": "Vissel",
            "tla": "VIS",
            "name_zh": "神户胜利船",
            "name_zh_full": "神户胜利船足球俱乐部",
            "crest": None,
            "founded": 1966,
            "venue": "Noevir Stadium Kobe",
            "league_code": "J1",
            "area_id": 2088,
            "area_name_en": "Japan",
            "area_name_zh": "日本",
            "coach": None,
            "squad_count": 0,
            "players": []
        },
        {
            "id": 4002,
            "name_en": "Yokohama F. Marinos",
            "name_en_full": "Yokohama F. Marinos",
            "name_en_short": "Marinos",
            "tla": "YFM",
            "name_zh": "横滨水手",
            "name_zh_full": "横滨F·水手足球俱乐部",
            "crest": None,
            "founded": 1972,
            "venue": "Nissan Stadium",
            "league_code": "J1",
            "area_id": 2088,
            "area_name_en": "Japan",
            "area_name_zh": "日本",
            "coach": None,
            "squad_count": 0,
            "players": []
        }
    ],
    "KL1": [  # 韩K联球队示例
        {
            "id": 4101,
            "name_en": "Jeonbuk Hyundai Motors",
            "name_en_full": "Jeonbuk Hyundai Motors FC",
            "name_en_short": "Jeonbuk",
            "tla": "JHM",
            "name_zh": "全北现代",
            "name_zh_full": "全北现代汽车足球俱乐部",
            "crest": None,
            "founded": 1994,
            "venue": "Jeonju World Cup Stadium",
            "league_code": "KL1",
            "area_id": 2097,
            "area_name_en": "South Korea",
            "area_name_zh": "韩国",
            "coach": None,
            "squad_count": 0,
            "players": []
        }
    ],
    "SPL": [  # 沙职联球队示例
        {
            "id": 4201,
            "name_en": "Al Nassr FC",
            "name_en_full": "Al Nassr Football Club",
            "name_en_short": "Al Nassr",
            "tla": "NAS",
            "name_zh": "利雅得胜利",
            "name_zh_full": "利雅得胜利足球俱乐部",
            "crest": None,
            "founded": 1955,
            "venue": "Mrsool Park",
            "league_code": "SPL",
            "area_id": 2182,
            "area_name_en": "Saudi Arabia",
            "area_name_zh": "沙特阿拉伯",
            "coach": None,
            "squad_count": 0,
            "players": []
        },
        {
            "id": 4202,
            "name_en": "Al Hilal SFC",
            "name_en_full": "Al Hilal Saudi Football Club",
            "name_en_short": "Al Hilal",
            "tla": "HIL",
            "name_zh": "利雅得新月",
            "name_zh_full": "利雅得新月足球俱乐部",
            "crest": None,
            "founded": 1957,
            "venue": "King Fahd International Stadium",
            "league_code": "SPL",
            "area_id": 2182,
            "area_name_en": "Saudi Arabia",
            "area_name_zh": "沙特阿拉伯",
            "coach": None,
            "squad_count": 0,
            "players": []
        }
    ]
}

def add_extended_leagues():
    """添加扩展联赛数据"""
    print("\n" + "="*80)
    print("添加扩展联赛数据")
    print("="*80)
    
    # 加载现有联赛
    leagues = load_json('leagues.json')
    if not leagues:
        leagues = []
    
    # 获取现有ID列表
    existing_ids = {l.get('id') for l in leagues}
    
    # 添加新联赛
    added_count = 0
    for ext_league in EXTENDED_LEAGUES:
        if ext_league['id'] not in existing_ids:
            leagues.append(ext_league)
            added_count += 1
            print(f"  ✓ 添加: {ext_league['name_zh']} ({ext_league['code']})")
    
    # 保存
    save_json(leagues, 'leagues.json')
    print(f"\n✓ 成功添加 {added_count} 个扩展联赛")
    
    return added_count

def add_extended_teams():
    """添加扩展球队数据"""
    print("\n" + "="*80)
    print("添加扩展球队数据")
    print("="*80)
    
    # 加载现有球队
    teams = load_json('teams_with_players.json')
    if not teams:
        teams = []
    
    # 获取现有ID列表
    existing_ids = {t.get('id') for t in teams}
    
    # 添加新球队
    added_count = 0
    for league_code, league_teams in EXTENDED_TEAMS.items():
        print(f"\n处理联赛: {league_code}")
        for ext_team in league_teams:
            if ext_team['id'] not in existing_ids:
                teams.append(ext_team)
                added_count += 1
                print(f"  ✓ 添加: {ext_team.get('name_zh')} ({ext_team.get('name_en')})")
    
    # 保存
    save_json(teams, 'teams_with_players.json')
    print(f"\n✓ 成功添加 {added_count} 支扩展球队")
    
    return added_count

def update_summary():
    """更新数据摘要"""
    print("\n" + "="*80)
    print("更新数据摘要")
    print("="*80)
    
    leagues = load_json('leagues.json')
    teams = load_json('teams_with_players.json')
    
    # 统计扩展数据
    extended_leagues = [l for l in leagues if l.get('id', 0) >= 3000]
    extended_teams = [t for t in teams if t.get('id', 0) >= 4000]
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'statistics': {
            'total_leagues': len(leagues),
            'extended_leagues': len(extended_leagues),
            'total_teams': len(teams),
            'extended_teams': len(extended_teams)
        },
        'extended_leagues_list': [
            {
                'code': l.get('code'),
                'name_zh': l.get('name_zh'),
                'name_en': l.get('name_en'),
                'country_zh': l.get('area_name_zh')
            }
            for l in extended_leagues
        ]
    }
    
    save_json(summary, 'summary.json')
    
    print(f"\n数据统计:")
    print(f"  总联赛数: {len(leagues)} (其中扩展: {len(extended_leagues)})")
    print(f"  总球队数: {len(teams)} (其中扩展: {len(extended_teams)})")

def main():
    print("="*80)
    print("扩展数据源管理工具")
    print("="*80)
    
    try:
        # 1. 添加扩展联赛
        add_extended_leagues()
        
        # 2. 添加扩展球队
        add_extended_teams()
        
        # 3. 更新摘要
        update_summary()
        
        print("\n" + "="*80)
        print("✓ 扩展数据添加完成！")
        print("="*80)
        print("\n提示:")
        print("1. 可以在 EXTENDED_LEAGUES 和 EXTENDED_TEAMS 中添加更多数据")
        print("2. 建议从可靠来源获取准确的球队和球员信息")
        print("3. 可以集成其他API自动获取这些数据")
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
