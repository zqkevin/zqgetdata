"""
football-data.org API 数据探索工具
独立测试项目 - 不与现有项目关联
"""
import requests
import json
from datetime import datetime
from pathlib import Path

# API配置
API_TOKEN = "b95b11f44dde401bb5f8de79364f59c6"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": API_TOKEN
}

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_json(data, filename):
    """保存JSON数据到文件"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {filepath}")

def get_rate_limit_info(response):
    """获取速率限制信息"""
    return {
        'requests_available_minute': response.headers.get('X-Requests-Available-Minute', 'N/A'),
        'requests_remaining_minute': response.headers.get('X-Requests-Remaining-Minute', 'N/A'),
        'credit_limit': response.headers.get('X-Credits-Limit', 'N/A'),
        'credits_remaining': response.headers.get('X-Credits-Remaining', 'N/A')
    }

def explore_competitions():
    """探索竞赛数据"""
    print("\n" + "="*80)
    print("1. 探索竞赛 (Competitions)")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/competitions", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        rate_info = get_rate_limit_info(response)
        
        print(f"\n速率限制信息:")
        for key, value in rate_info.items():
            print(f"  {key}: {value}")
        
        print(f"\n总竞赛数: {data.get('count')}")
        print(f"过滤器: {data.get('filters')}")
        
        competitions = data.get('competitions', [])
        print(f"\n可用竞赛列表 ({len(competitions)}个):")
        
        comp_summary = []
        for comp in competitions:
            summary = {
                'id': comp.get('id'),
                'name': comp.get('name'),
                'code': comp.get('code'),
                'type': comp.get('type'),
                'area': comp.get('area', {}).get('name'),
                'current_season': comp.get('currentSeason', {}).get('startDate'),
                'emblem': comp.get('emblem')
            }
            comp_summary.append(summary)
            print(f"  - [{comp.get('code')}] {comp.get('name')} ({comp.get('area', {}).get('name')})")
        
        # 保存完整数据
        save_json({
            'rate_limit': rate_info,
            'competitions': comp_summary,
            'full_data': competitions
        }, 'competitions.json')
        
        return competitions
    else:
        print(f"错误: HTTP {response.status_code}")
        print(response.text)
        return []

def explore_areas():
    """探索区域/国家数据"""
    print("\n" + "="*80)
    print("2. 探索区域/国家 (Areas)")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/areas", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        rate_info = get_rate_limit_info(response)
        
        print(f"\n速率限制信息:")
        for key, value in rate_info.items():
            print(f"  {key}: {value}")
        
        print(f"\n总区域数: {data.get('count')}")
        
        areas = data.get('areas', [])
        print(f"\n示例区域 (前20个):")
        
        area_summary = []
        for area in areas[:20]:
            summary = {
                'id': area.get('id'),
                'name': area.get('name'),
                'code': area.get('countryCode'),
                'flag': area.get('flag')
            }
            area_summary.append(summary)
            print(f"  - [{area.get('countryCode')}] {area.get('name')}")
        
        # 保存完整数据
        save_json({
            'rate_limit': rate_info,
            'total_count': data.get('count'),
            'sample_areas': area_summary,
            'full_data': areas
        }, 'areas.json')
        
        return areas
    else:
        print(f"错误: HTTP {response.status_code}")
        print(response.text)
        return []

def explore_teams(competition_code='PL'):
    """探索球队数据"""
    print("\n" + "="*80)
    print(f"3. 探索球队 (Teams) - 以 {competition_code} 为例")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/competitions/{competition_code}/teams", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        rate_info = get_rate_limit_info(response)
        
        print(f"\n速率限制信息:")
        for key, value in rate_info.items():
            print(f"  {key}: {value}")
        
        print(f"\n竞赛: {data.get('competition', {}).get('name')}")
        print(f"赛季: {data.get('season', {}).get('startDate')} - {data.get('season', {}).get('endDate')}")
        
        teams = data.get('teams', [])
        print(f"\n球队数量: {len(teams)}")
        
        if teams:
            print(f"\n第一支球队的完整数据结构:")
            first_team = teams[0]
            
            # 打印所有字段
            print("\n球队字段列表:")
            for key in first_team.keys():
                value = first_team[key]
                if isinstance(value, (dict, list)):
                    print(f"  - {key}: {type(value).__name__} (长度: {len(value)})")
                else:
                    print(f"  - {key}: {value}")
            
            # 保存完整的球队数据
            save_json({
                'rate_limit': rate_info,
                'competition': data.get('competition'),
                'season': data.get('season'),
                'teams': teams
            }, f'teams_{competition_code}.json')
        
        return teams
    else:
        print(f"错误: HTTP {response.status_code}")
        print(response.text)
        return []

def explore_single_team(team_id=64):
    """探索单个球队的详细信息（包括球员）"""
    print("\n" + "="*80)
    print(f"4. 探索单个球队详情 (Team ID: {team_id})")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/teams/{team_id}", headers=HEADERS)
    
    if response.status_code == 200:
        team_data = response.json()
        rate_info = get_rate_limit_info(response)
        
        print(f"\n速率限制信息:")
        for key, value in rate_info.items():
            print(f"  {key}: {value}")
        
        print(f"\n球队基本信息:")
        print(f"  名称: {team_data.get('name')}")
        print(f"  简称: {team_data.get('shortName')}")
        print(f"  缩写: {team_data.get('tla')}")
        print(f"  成立年份: {team_data.get('founded')}")
        print(f"  颜色: {team_data.get('clubColors')}")
        print(f"  场馆: {team_data.get('venue')}")
        print(f"  网站: {team_data.get('website')}")
        
        # 教练信息
        coach = team_data.get('coach', {})
        if coach:
            print(f"\n教练:")
            print(f"  姓名: {coach.get('name')}")
            print(f"  国籍: {coach.get('nationality')}")
        
        # 球员阵容
        squad = team_data.get('squad', [])
        print(f"\n球员阵容 (共{len(squad)}人):")
        
        player_summary = []
        for player in squad[:10]:  # 只显示前10个
            print(f"  - {player.get('name')} ({player.get('position')}) - #{player.get('shirtNumber')}")
            player_summary.append(player)
        
        # 保存完整数据
        save_json({
            'rate_limit': rate_info,
            'team': team_data,
            'squad_sample': player_summary
        }, f'team_detail_{team_id}.json')
        
        return team_data
    else:
        print(f"错误: HTTP {response.status_code}")
        print(response.text)
        return None

def explore_matches():
    """探索比赛数据"""
    print("\n" + "="*80)
    print("5. 探索比赛 (Matches)")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/matches", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        rate_info = get_rate_limit_info(response)
        
        print(f"\n速率限制信息:")
        for key, value in rate_info.items():
            print(f"  {key}: {value}")
        
        result_set = data.get('resultSet', {})
        print(f"\n结果集:")
        print(f"  计数: {result_set.get('count')}")
        print(f"  比赛数: {result_set.get('played')}")
        
        matches = data.get('matches', [])
        print(f"\n今日比赛数量: {len(matches)}")
        
        if matches:
            print(f"\n第一场比赛的数据结构:")
            first_match = matches[0]
            
            print("\n比赛字段列表:")
            for key in first_match.keys():
                value = first_match[key]
                if isinstance(value, (dict, list)):
                    print(f"  - {key}: {type(value).__name__}")
                else:
                    print(f"  - {key}: {value}")
        
        # 保存数据
        save_json({
            'rate_limit': rate_info,
            'result_set': result_set,
            'matches_sample': matches[:5],  # 只保存前5场
            'full_matches': matches
        }, 'matches.json')
        
        return matches
    else:
        print(f"错误: HTTP {response.status_code}")
        print(response.text)
        return []

def generate_summary_report(all_data):
    """生成数据摘要报告"""
    print("\n" + "="*80)
    print("数据摘要报告")
    print("="*80)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'api_version': 'v4',
        'summary': {}
    }
    
    # 竞赛统计
    if 'competitions' in all_data:
        comps = all_data['competitions']
        report['summary']['competitions'] = {
            'total': len(comps),
            'by_country': {},
            'codes': [c.get('code') for c in comps]
        }
        
        # 按国家分组
        for comp in comps:
            country = comp.get('area', {}).get('name', 'Unknown')
            if country not in report['summary']['competitions']['by_country']:
                report['summary']['competitions']['by_country'][country] = []
            report['summary']['competitions']['by_country'][country].append(comp.get('code'))
    
    # 区域统计
    if 'areas' in all_data:
        report['summary']['areas'] = {
            'total': len(all_data['areas'])
        }
    
    # 球队统计
    if 'teams_PL' in all_data:
        teams = all_data['teams_PL']
        report['summary']['teams_sample'] = {
            'competition': 'Premier League',
            'total': len(teams),
            'fields_available': list(teams[0].keys()) if teams else []
        }
    
    # 保存报告
    save_json(report, 'summary_report.json')
    
    # 打印报告
    print(f"\n时间戳: {report['timestamp']}")
    print(f"API版本: {report['api_version']}")
    
    if 'competitions' in report['summary']:
        comp_stats = report['summary']['competitions']
        print(f"\n竞赛统计:")
        print(f"  总数: {comp_stats['total']}")
        print(f"  涉及国家/地区: {len(comp_stats['by_country'])}")
        for country, codes in comp_stats['by_country'].items():
            print(f"    - {country}: {', '.join(codes)}")
    
    if 'teams_sample' in report['summary']:
        team_stats = report['summary']['teams_sample']
        print(f"\n球队数据 (示例: {team_stats['competition']}):")
        print(f"  球队数: {team_stats['total']}")
        print(f"  可用字段: {', '.join(team_stats['fields_available'])}")

def main():
    print("="*80)
    print("football-data.org API 数据探索")
    print(f"开始时间: {datetime.now()}")
    print("="*80)
    
    all_data = {}
    
    try:
        # 1. 探索竞赛
        competitions = explore_competitions()
        all_data['competitions'] = competitions
        
        # 等待一下避免速率限制
        import time
        time.sleep(2)
        
        # 2. 探索区域
        areas = explore_areas()
        all_data['areas'] = areas
        
        time.sleep(2)
        
        # 3. 探索球队（英超）
        teams_pl = explore_teams('PL')
        all_data['teams_PL'] = teams_pl
        
        time.sleep(2)
        
        # 4. 探索单个球队详情
        team_detail = explore_single_team(64)  # Liverpool
        all_data['team_detail_64'] = team_detail
        
        time.sleep(2)
        
        # 5. 探索比赛
        matches = explore_matches()
        all_data['matches'] = matches
        
        # 生成摘要报告
        generate_summary_report(all_data)
        
        print("\n" + "="*80)
        print("探索完成！")
        print(f"所有数据已保存到: {OUTPUT_DIR}")
        print("="*80)
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
