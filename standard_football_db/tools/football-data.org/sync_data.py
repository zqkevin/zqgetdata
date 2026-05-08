"""
标准化足球数据库 - 数据同步脚本
从 football-data.org API 获取标准化的国家、联赛、球队、球员数据
"""
import requests
import json
from datetime import datetime
from pathlib import Path
import time

# API配置
API_TOKEN = "b95b11f44dde401bb5f8de79364f59c6"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": API_TOKEN
}

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_json(data, filename):
    """保存JSON数据到文件"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {filepath}")

def get_all_countries():
    """获取所有国家/地区（包含多语言支持）"""
    print("\n" + "="*80)
    print("1. 获取国家/地区数据")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/areas", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        areas = data.get('areas', [])
        
        print(f"总共 {len(areas)} 个国家/地区")
        
        # 提取关键信息（多语言支持）
        countries = []
        for area in areas:
            country = {
                'id': area.get('id'),
                # 英文名称（API默认提供）
                'name_en': area.get('name'),
                'code': area.get('countryCode'),
                'flag': area.get('flag'),
                'parent_area_id': area.get('parentAreaId'),
                'parent_area_name_en': area.get('parentArea'),
                # 中文名称需要后续翻译或手动维护
                'name_zh': None,  # 待填充
                'parent_area_name_zh': None  # 待填充
            }
            countries.append(country)
        
        save_json(countries, 'countries.json')
        print(f"✓ 成功获取 {len(countries)} 个国家/地区（英文）")
        print(f"⚠ 注意: 中文名称需要后续翻译或手动维护")
        
        return countries
    else:
        print(f"✗ 错误: HTTP {response.status_code}")
        return []

def get_all_competitions():
    """获取所有竞赛（联赛，包含多语言支持）"""
    print("\n" + "="*80)
    print("2. 获取联赛数据")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/competitions", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        competitions = data.get('competitions', [])
        
        print(f"总共 {len(competitions)} 个竞赛")
        
        # 提取关键信息（多语言支持）
        leagues = []
        for comp in competitions:
            league = {
                'id': comp.get('id'),
                # 英文名称（API默认提供）
                'name_en': comp.get('name'),
                'name_en_full': comp.get('name'),  # 全称同name_en
                'code': comp.get('code'),
                'type': comp.get('type'),
                'emblem': comp.get('emblem'),
                'area_id': comp.get('area', {}).get('id'),
                'area_name_en': comp.get('area', {}).get('name'),
                'area_code': comp.get('area', {}).get('code'),
                # 中文名称需要后续翻译
                'name_zh': None,
                'name_zh_full': None,
                'name_zh_short': None,  # 中文简称
                'area_name_zh': None,
                'current_season': {
                    'start_date': comp.get('currentSeason', {}).get('startDate'),
                    'end_date': comp.get('currentSeason', {}).get('endDate'),
                    'current_matchday': comp.get('currentSeason', {}).get('currentMatchday')
                }
            }
            leagues.append(league)
            print(f"  - [{comp.get('code')}] {comp.get('name')} ({comp.get('area', {}).get('name')})")
        
        save_json(leagues, 'leagues.json')
        print(f"✓ 成功获取 {len(leagues)} 个联赛（英文）")
        print(f"⚠ 注意: 中文名称需要后续翻译或手动维护")
        
        # 等待避免速率限制
        time.sleep(2)
        
        return leagues
    else:
        print(f"✗ 错误: HTTP {response.status_code}")
        return []

def get_teams_by_league(league_code):
    """获取指定联赛的所有球队"""
    print(f"\n  获取 {league_code} 的球队...")
    
    response = requests.get(f"{BASE_URL}/competitions/{league_code}/teams", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        teams = data.get('teams', [])
        
        print(f"    找到 {len(teams)} 支球队")
        
        # 提取关键信息
        team_list = []
        for team in teams:
            team_data = {
                'id': team.get('id'),
                # 英文名称（API默认提供）
                'name_en': team.get('name'),
                'name_en_full': team.get('name'),  # 英文全称
                'name_en_short': team.get('shortName'),  # 英文简称
                'tla': team.get('tla'),  # 三字缩写
                'crest': team.get('crest'),
                'founded': team.get('founded'),
                'venue': team.get('venue'),
                'website': team.get('website'),
                'club_colors': team.get('clubColors'),
                'address': team.get('address'),
                'area_id': team.get('area', {}).get('id'),
                'area_name_en': team.get('area', {}).get('name'),
                'league_code': league_code,
                # 中文名称需要后续翻译
                'name_zh': None,
                'name_zh_full': None,  # 中文全称
                'name_zh_short': None,  # 中文简称
                'area_name_zh': None,
                # 教练信息
                'coach': {
                    'id': team.get('coach', {}).get('id'),
                    'name_en': team.get('coach', {}).get('name'),
                    'name_zh': None,  # 中文姓名待翻译
                    'nationality': team.get('coach', {}).get('nationality'),
                    'contract_start': team.get('coach', {}).get('contract', {}).get('start'),
                    'contract_until': team.get('coach', {}).get('contract', {}).get('until')
                },
                # 球员阵容
                'squad_count': len(team.get('squad', [])),
                'players': []
            }
            
            # 提取球员信息（多语言支持）
            for player in team.get('squad', []):
                player_data = {
                    'id': player.get('id'),
                    # 英文名称（API默认提供）
                    'name_en': player.get('name'),
                    'name_en_full': player.get('name'),
                    'first_name_en': player.get('firstName'),
                    'last_name_en': player.get('lastName'),
                    'date_of_birth': player.get('dateOfBirth'),
                    'nationality': player.get('nationality'),
                    'position': player.get('position'),
                    'shirt_number': player.get('shirtNumber'),
                    # 中文名称需要后续翻译
                    'name_zh': None,
                    'name_zh_full': None,
                    'first_name_zh': None,
                    'last_name_zh': None
                }
                team_data['players'].append(player_data)
            
            team_list.append(team_data)
        
        return team_list
    else:
        print(f"    ✗ 错误: HTTP {response.status_code}")
        return []

def get_all_teams(leagues):
    """获取所有联赛的球队"""
    print("\n" + "="*80)
    print("3. 获取球队和球员数据")
    print("="*80)
    
    all_teams = []
    
    for i, league in enumerate(leagues, 1):
        league_code = league.get('code')
        print(f"\n[{i}/{len(leagues)}] 处理联赛: {league.get('name')}")
        
        teams = get_teams_by_league(league_code)
        all_teams.extend(teams)
        
        print(f"    ✓ 完成 (累计 {len(all_teams)} 支球队)")
        
        # 每次请求后等待，避免速率限制
        if i < len(leagues):
            time.sleep(6)  # 6秒延迟，确保不超过10次/分钟
    
    # 保存所有球队数据
    save_json(all_teams, 'teams_with_players.json')
    print(f"\n✓ 成功获取 {len(all_teams)} 支球队的完整数据（含球员）")
    
    return all_teams

def generate_summary(countries, leagues, teams):
    """生成数据摘要"""
    print("\n" + "="*80)
    print("4. 生成数据摘要")
    print("="*80)
    
    # 统计球员总数
    total_players = sum(len(team.get('players', [])) for team in teams)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'statistics': {
            'total_countries': len(countries),
            'total_leagues': len(leagues),
            'total_teams': len(teams),
            'total_players': total_players,
            'average_players_per_team': round(total_players / len(teams), 1) if teams else 0
        },
        'leagues_summary': [
            {
                'code': league.get('code'),
                'name': league.get('name'),
                'country': league.get('area_name')
            }
            for league in leagues
        ],
        'sample_teams': [
            {
                'name': team.get('name'),
                'short_name': team.get('short_name'),
                'league': team.get('league_code'),
                'player_count': team.get('squad_count')
            }
            for team in teams[:10]  # 前10支球队作为示例
        ]
    }
    
    save_json(summary, 'summary.json')
    
    print(f"\n数据统计:")
    print(f"  国家/地区: {summary['statistics']['total_countries']}")
    print(f"  联赛: {summary['statistics']['total_leagues']}")
    print(f"  球队: {summary['statistics']['total_teams']}")
    print(f"  球员: {summary['statistics']['total_players']}")
    print(f"  平均每队球员数: {summary['statistics']['average_players_per_team']}")

def main():
    print("="*80)
    print("标准化足球数据库 - 数据同步")
    print(f"开始时间: {datetime.now()}")
    print("="*80)
    
    try:
        # 1. 获取国家数据
        countries = get_all_countries()
        time.sleep(2)
        
        # 2. 获取联赛数据
        leagues = get_all_competitions()
        
        # 3. 获取所有球队和球员
        teams = get_all_teams(leagues)
        
        # 4. 生成摘要
        generate_summary(countries, leagues, teams)
        
        print("\n" + "="*80)
        print("✓ 数据同步完成！")
        print(f"所有数据已保存到: {OUTPUT_DIR}")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
