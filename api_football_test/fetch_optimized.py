"""
API-Football 分阶段数据获取脚本
严格按照优化策略执行，避免重复，最大化利用配额
"""
import requests
import json
import time
from pathlib import Path
from datetime import datetime, date

# API配置
API_KEY = "9480faad2e61ec9679b42ca60e0f344a"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "data_optimized"
OUTPUT_DIR.mkdir(exist_ok=True)

# 配额控制
MAX_DAILY_REQUESTS = 80  # 每天最多80次（留20次余量）
MIN_INTERVAL = 2.0  # 每次请求间隔2秒
REQUEST_COUNT_FILE = OUTPUT_DIR / "request_count.json"

def load_request_count():
    """加载今日请求计数"""
    if REQUEST_COUNT_FILE.exists():
        with open(REQUEST_COUNT_FILE, 'r') as f:
            data = json.load(f)
            if data.get('date') == str(date.today()):
                return data.get('count', 0)
    return 0

def save_request_count(count):
    """保存今日请求计数"""
    data = {
        'date': str(date.today()),
        'count': count
    }
    with open(REQUEST_COUNT_FILE, 'w') as f:
        json.dump(data, f)

DAILY_COUNT = load_request_count()
LAST_REQUEST_TIME = 0

def check_rate_limit():
    """检查速率限制和每日配额"""
    global DAILY_COUNT, LAST_REQUEST_TIME
    
    if DAILY_COUNT >= MAX_DAILY_REQUESTS:
        raise Exception(f"今日配额已用完 ({DAILY_COUNT}/{MAX_DAILY_REQUESTS})")
    
    # 确保最小间隔
    current_time = time.time()
    elapsed = current_time - LAST_REQUEST_TIME
    if elapsed < MIN_INTERVAL:
        sleep_time = MIN_INTERVAL - elapsed
        print(f"    ⏱ 等待 {sleep_time:.1f}秒 (速率控制)")
        time.sleep(sleep_time)
    
    LAST_REQUEST_TIME = time.time()
    DAILY_COUNT += 1
    save_request_count(DAILY_COUNT)

def make_request(endpoint, params=None):
    """发送API请求（带完整控制）"""
    check_rate_limit()
    
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        # 显示配额信息
        remaining = response.headers.get('x-ratelimit-requests-remaining', 'N/A')
        print(f"    📊 今日已用: {DAILY_COUNT}/{MAX_DAILY_REQUESTS}, API剩余: {remaining}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"    ⚠️  速率限制！等待60秒...")
            time.sleep(60)
            return make_request(endpoint, params)  # 重试
        else:
            print(f"    ✗ HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"    ✗ 错误: {str(e)}")
        return None

def save_json(data, filename):
    """保存JSON数据"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {filepath}")

def get_league_teams(league_id, season=2024):
    """获取联赛所有球队"""
    print(f"\n  获取联赛 {league_id} 的球队列表...")
    
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
                'national': team.get('national'),
                'logo': team.get('logo'),
                'venue_name': venue.get('name'),
                'venue_city': venue.get('city'),
                'venue_capacity': venue.get('capacity'),
            }
            teams.append(team_data)
        
        print(f"    ✓ 成功获取 {len(teams)} 支球队")
        return teams
    else:
        print(f"    ✗ 未获取到数据")
        return []

def get_team_squad(team_id, team_name, season=2024):
    """获取球队阵容"""
    print(f"    获取 {team_name} 的阵容...")
    
    data = make_request("players/squads", {"team": team_id, "season": season})
    
    if data and data.get('response'):
        players = data['response'][0].get('players', [])
        print(f"      ✓ 成功获取 {len(players)} 名球员")
        return players
    else:
        print(f"      ✗ 未获取到球员数据")
        return []

def phase1_get_league_lists():
    """阶段1: 获取4个亚洲联赛的球队列表"""
    print("\n" + "="*80)
    print("阶段1: 获取亚洲4大联赛球队列表")
    print("="*80)
    
    asian_leagues = {
        "日职联_J1": 98,
        "韩K联_K1": 292,
        "沙职联_SPL": 307,
        "中超_CSL": 169,
    }
    
    all_teams = {}
    
    for league_name, league_id in asian_leagues.items():
        print(f"\n{'-'*60}")
        print(f"联赛: {league_name} (ID: {league_id})")
        print(f"{'-'*60}")
        
        teams = get_league_teams(league_id, 2024)
        
        if teams:
            all_teams[league_name] = {
                'league_id': league_id,
                'teams': teams,
                'team_count': len(teams)
            }
            print(f"  ✓ {league_name} 完成: {len(teams)}支球队")
        else:
            print(f"  ✗ {league_name} 失败")
    
    # 保存球队列表
    save_json(all_teams, 'phase1_league_teams.json')
    
    total_teams = sum(d['team_count'] for d in all_teams.values())
    print(f"\n✓ 阶段1完成: 共获取 {total_teams} 支球队")
    print(f"  今日已用请求: {DAILY_COUNT}/{MAX_DAILY_REQUESTS}")
    
    return all_teams

def phase2_get_sample_squads(all_teams, teams_per_league=2):
    """阶段2: 获取每联赛示例球队的阵容"""
    print("\n" + "="*80)
    print(f"阶段2: 获取每联赛前{teams_per_league}支球队的阵容")
    print("="*80)
    
    squads_data = {}
    
    for league_name, league_data in all_teams.items():
        print(f"\n{'-'*60}")
        print(f"联赛: {league_name}")
        print(f"{'-'*60}")
        
        teams = league_data['teams'][:teams_per_league]
        league_squads = []
        
        for i, team in enumerate(teams, 1):
            print(f"\n  [{i}/{teams_per_league}] {team['name']}")
            
            players = get_team_squad(team['id'], team['name'], 2024)
            
            team_with_squad = team.copy()
            team_with_squad['players'] = players
            team_with_squad['player_count'] = len(players)
            
            league_squads.append(team_with_squad)
            
            print(f"      进度: {DAILY_COUNT}/{MAX_DAILY_REQUESTS}")
        
        squads_data[league_name] = league_squads
        print(f"\n  ✓ {league_name} 完成: {len(league_squads)}支球队阵容")
    
    # 保存阵容数据
    save_json(squads_data, 'phase2_sample_squads.json')
    
    total_squads = sum(len(v) for v in squads_data.values())
    total_players = sum(
        sum(t.get('player_count', 0) for t in v)
        for v in squads_data.values()
    )
    
    print(f"\n✓ 阶段2完成:")
    print(f"  获取阵容: {total_squads}支球队")
    print(f"  获取球员: {total_players}名")
    print(f"  今日已用请求: {DAILY_COUNT}/{MAX_DAILY_REQUESTS}")
    
    return squads_data

def generate_phase_report(all_teams, squads_data):
    """生成阶段报告"""
    print("\n" + "="*80)
    print("生成阶段报告")
    print("="*80)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'phase': '1-2',
        'account': 'zqkevin6006@gmail.com',
        'quota_usage': {
            'daily_used': DAILY_COUNT,
            'daily_max': MAX_DAILY_REQUESTS,
            'remaining': MAX_DAILY_REQUESTS - DAILY_COUNT,
            'usage_percentage': round(DAILY_COUNT / MAX_DAILY_REQUESTS * 100, 1)
        },
        'data_summary': {
            'leagues_covered': len(all_teams),
            'total_teams': sum(d['team_count'] for d in all_teams.values()),
            'squads_fetched': sum(len(v) for v in squads_data.values()),
            'total_players': sum(
                sum(t.get('player_count', 0) for t in v)
                for v in squads_data.values()
            )
        },
        'leagues_detail': [
            {
                'name': name,
                'league_id': data['league_id'],
                'teams_count': data['team_count'],
                'squads_sampled': len(squads_data.get(name, []))
            }
            for name, data in all_teams.items()
        ],
        'next_steps': {
            'recommendation': '继续获取剩余球队的完整阵容',
            'estimated_requests': sum(
                d['team_count'] - 2  # 减去已获取的2支
                for d in all_teams.values()
            ),
            'can_continue_today': (MAX_DAILY_REQUESTS - DAILY_COUNT) > 20
        }
    }
    
    save_json(report, 'phase_report.json')
    
    print(f"\n📊 阶段报告:")
    print(f"  覆盖联赛: {report['data_summary']['leagues_covered']}个")
    print(f"  球队总数: {report['data_summary']['total_teams']}支")
    print(f"  已获阵容: {report['data_summary']['squads_fetched']}支")
    print(f"  球员总数: {report['data_summary']['total_players']}名")
    print(f"  今日配额: {DAILY_COUNT}/{MAX_DAILY_REQUESTS} ({report['quota_usage']['usage_percentage']}%)")
    
    if report['next_steps']['can_continue_today']:
        remaining = report['next_steps']['estimated_requests']
        print(f"\n💡 提示: 今日还可获取约 {remaining} 支球队的阵容")
    else:
        print(f"\n⏸️  今日配额即将用完，建议明天继续")
    
    return report

def main():
    print("="*80)
    print("API-Football 分阶段数据获取")
    print(f"账户: zqkevin6006@gmail.com")
    print(f"日期: {date.today()}")
    print(f"今日已用: {DAILY_COUNT}/{MAX_DAILY_REQUESTS}")
    print("="*80)
    
    try:
        # 阶段1: 获取联赛球队列表
        all_teams = phase1_get_league_lists()
        
        # 阶段2: 获取示例球队阵容
        squads_data = phase2_get_sample_squads(all_teams, teams_per_league=2)
        
        # 生成报告
        report = generate_phase_report(all_teams, squads_data)
        
        print("\n" + "="*80)
        print("✓ 分阶段数据获取完成！")
        print(f"所有数据已保存到: {OUTPUT_DIR}")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
