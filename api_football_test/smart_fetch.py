"""
API-Football 智能数据获取脚本
严格遵守免费账户限制：每月100次请求
优化策略：批量获取、缓存数据、最小化请求
"""
import requests
import json
import time
from pathlib import Path
from datetime import datetime

# API配置
API_KEY = "9480faad2e61ec9679b42ca60e0f344a"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "data_smart"
OUTPUT_DIR.mkdir(exist_ok=True)

# 速率限制控制
REQUEST_COUNT = 0
MAX_REQUESTS = 95  # 留5次余量
LAST_REQUEST_TIME = 0
MIN_INTERVAL = 1.5  # 每次请求至少间隔1.5秒

def check_rate_limit():
    """检查速率限制"""
    global REQUEST_COUNT, LAST_REQUEST_TIME
    
    if REQUEST_COUNT >= MAX_REQUESTS:
        raise Exception(f"已达到最大请求次数限制 ({MAX_REQUESTS})")
    
    # 确保最小间隔
    current_time = time.time()
    elapsed = current_time - LAST_REQUEST_TIME
    if elapsed < MIN_INTERVAL:
        sleep_time = MIN_INTERVAL - elapsed
        print(f"    ⏱ 等待 {sleep_time:.1f}秒 (速率控制)")
        time.sleep(sleep_time)
    
    LAST_REQUEST_TIME = time.time()
    REQUEST_COUNT += 1

def make_request(endpoint, params=None):
    """发送API请求（带速率控制）"""
    check_rate_limit()
    
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        # 检查响应头中的配额信息
        remaining = response.headers.get('x-ratelimit-requests-remaining', 'N/A')
        print(f"    📊 剩余请求: {remaining}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"    ⚠️  速率限制！等待60秒...")
            time.sleep(60)
            # 重试一次
            return make_request(endpoint, params)
        else:
            print(f"    ✗ HTTP {response.status_code}: {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"    ✗ 请求错误: {str(e)}")
        return None

def save_json(data, filename):
    """保存JSON数据"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {filepath}")

def get_league_teams(league_id, season=2024):
    """获取联赛球队（高效：一次请求获取所有球队）"""
    print(f"\n  获取联赛 {league_id} 的球队...")
    
    data = make_request("teams", {"league": league_id, "season": season})
    
    if data and data.get('response'):
        teams = []
        for item in data['response']:
            team = item.get('team', {})
            venue = item.get('venue', {})
            
            team_data = {
                'id': team.get('id'),
                'name': team.get('name'),
                'code': team.get('code'),
                'country': team.get('country'),
                'founded': team.get('founded'),
                'logo': team.get('logo'),
                'venue': venue.get('name'),
                'capacity': venue.get('capacity'),
            }
            teams.append(team_data)
        
        print(f"    ✓ 成功获取 {len(teams)} 支球队")
        return teams
    else:
        print(f"    ✗ 未获取到数据")
        return []

def get_team_squad(team_id, season=2024):
    """获取球队阵容（高效：一次请求获取所有球员）"""
    print(f"    获取球队 {team_id} 的阵容...")
    
    data = make_request("players/squads", {"team": team_id, "season": season})
    
    if data and data.get('response'):
        players = data['response'][0].get('players', [])
        print(f"      ✓ 成功获取 {len(players)} 名球员")
        return players
    else:
        print(f"      ✗ 未获取到球员数据")
        return []

def smart_fetch_asian_leagues():
    """智能获取亚洲联赛数据（优化请求次数）"""
    print("\n" + "="*80)
    print("智能获取亚洲联赛数据")
    print("="*80)
    
    # 只获取最重要的4个亚洲联赛
    asian_leagues = {
        "日职联_J1": 98,
        "韩K联_K1": 292,
        "沙职联_SPL": 307,
        "中超_CSL": 169,
    }
    
    all_data = {}
    
    for league_name, league_id in asian_leagues.items():
        print(f"\n{'='*60}")
        print(f"处理: {league_name} (ID: {league_id})")
        print(f"{'='*60}")
        
        # 1次请求：获取所有球队
        teams = get_league_teams(league_id, 2024)
        
        if not teams:
            continue
        
        # 策略：只获取前2支球队的完整阵容作为示例
        # 这样每个联赛只需要 1 + 2 = 3次请求
        sample_teams = []
        for i, team in enumerate(teams[:2]):
            print(f"\n  [{i+1}/2] {team['name']}")
            
            # 1次请求：获取球员阵容
            players = get_team_squad(team['id'], 2024)
            
            team_with_players = team.copy()
            team_with_players['players'] = players
            team_with_players['player_count'] = len(players)
            
            sample_teams.append(team_with_players)
            
            # 显示进度
            used = REQUEST_COUNT
            remaining = MAX_REQUESTS - used
            print(f"      已用请求: {used}/{MAX_REQUESTS}, 剩余: {remaining}")
        
        all_data[league_name] = {
            'league_id': league_id,
            'total_teams': len(teams),
            'teams_list': [t['name'] for t in teams],  # 只保存队名列表
            'sample_teams': sample_teams,  # 详细数据
            'requests_used': 3  # 1次球队 + 2次阵容
        }
        
        print(f"\n  ✓ {league_name} 完成 (总{len(teams)}队, 详细分析2队)")
        print(f"  本联赛使用请求: 3次")
    
    return all_data

def generate_final_report(asian_data):
    """生成最终报告"""
    print("\n" + "="*80)
    print("生成最终报告")
    print("="*80)
    
    total_teams = sum(d['total_teams'] for d in asian_data.values())
    total_players = sum(
        sum(t.get('player_count', 0) for t in d.get('sample_teams', []))
        for d in asian_data.values()
    )
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'account': 'zqkevin6006@gmail.com (免费)',
        'api_usage': {
            'total_requests_used': REQUEST_COUNT,
            'max_requests': MAX_REQUESTS,
            'remaining': MAX_REQUESTS - REQUEST_COUNT,
            'usage_percentage': round(REQUEST_COUNT / MAX_REQUESTS * 100, 1)
        },
        'data_summary': {
            'leagues_covered': len(asian_data),
            'total_teams_found': total_teams,
            'teams_detailed': sum(len(d.get('sample_teams', [])) for d in asian_data.values()),
            'total_players_fetched': total_players
        },
        'leagues_detail': [
            {
                'name': name,
                'league_id': data['league_id'],
                'teams_count': data['total_teams'],
                'sample_analyzed': len(data.get('sample_teams', [])),
                'requests_used': data.get('requests_used', 0)
            }
            for name, data in asian_data.items()
        ],
        'efficiency_analysis': {
            'requests_per_league': 3,
            'teams_per_request': round(total_teams / REQUEST_COUNT, 1) if REQUEST_COUNT > 0 else 0,
            'strategy': '获取所有球队列表 + 每联赛2支球队完整阵容'
        },
        'recommendation': {
            'current_usage': f'{REQUEST_COUNT}/{MAX_REQUESTS} ({REQUEST_COUNT/MAX_REQUESTS*100:.1f}%)',
            'monthly_budget': '100 requests',
            'can_fetch_more': MAX_REQUESTS - REQUEST_COUNT > 10,
            'suggestion': '当前策略高效，可继续获取更多联赛或球队详情'
        }
    }
    
    save_json(report, 'final_report.json')
    
    print(f"\n📊 数据统计:")
    print(f"  API请求使用: {REQUEST_COUNT}/{MAX_REQUESTS} ({report['api_usage']['usage_percentage']}%)")
    print(f"  覆盖联赛: {len(asian_data)}个")
    print(f"  获取球队: {total_teams}支")
    print(f"  详细分析: {report['data_summary']['teams_detailed']}支球队")
    print(f"  获取球员: {total_players}名")
    
    return report

def main():
    print("="*80)
    print("API-Football 智能数据获取")
    print(f"账户: zqkevin6006@gmail.com (免费)")
    print(f"配额: {MAX_REQUESTS}次请求/月")
    print(f"开始时间: {datetime.now()}")
    print("="*80)
    
    try:
        # 智能获取亚洲联赛数据
        asian_data = smart_fetch_asian_leagues()
        
        # 保存原始数据
        save_json(asian_data, 'asian_leagues_smart.json')
        
        # 生成报告
        report = generate_final_report(asian_data)
        
        print("\n" + "="*80)
        print("✓ 智能数据获取完成！")
        print(f"所有数据已保存到: {OUTPUT_DIR}")
        print("="*80)
        
        if report['recommendation']['can_fetch_more']:
            remaining = MAX_REQUESTS - REQUEST_COUNT
            print(f"\n💡 提示: 还有 {remaining} 次请求可用")
            print("   可以继续获取更多联赛或球队详情")
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
