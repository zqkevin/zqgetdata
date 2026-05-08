"""
TheSportsDB API 测试脚本
免费API，每日100次请求限制
文档: https://www.thesportsdb.com/api.php
"""
import requests
import json
from pathlib import Path
from datetime import datetime

# API配置
# TheSportsDB 免费版使用 "2" 作为测试key，或直接不使用key
API_KEY = None  # 免费版可以不用key
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_json(data, filename):
    """保存JSON数据"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {filepath}")

def test_api_connection():
    """测试API连接"""
    print("\n" + "="*80)
    print("1. 测试API连接")
    print("="*80)
    
    # 搜索一个知名球队测试连接
    url = f"{BASE_URL}/searchteams.php"
    params = {"t": "Arsenal"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            print(f"✓ API连接成功！找到 {len(teams)} 个结果")
            
            if teams:
                print(f"\n示例数据:")
                team = teams[0]
                print(f"  球队: {team.get('strTeam')}")
                print(f"  联赛: {team.get('strLeague')}")
                print(f"  国家: {team.get('strCountry')}")
                
            return True
        else:
            print(f"✗ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def get_league_teams(league_name):
    """获取指定联赛的所有球队"""
    print(f"\n  获取联赛 '{league_name}' 的球队...")
    
    url = f"{BASE_URL}/search_all_teams.php"
    params = {"l": league_name}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            print(f"    找到 {len(teams)} 支球队")
            
            # 提取关键信息
            team_list = []
            for team in teams:
                team_data = {
                    'idTeam': team.get('idTeam'),
                    'strTeam': team.get('strTeam'),  # 队名
                    'strTeamShort': team.get('strTeamShort'),  # 简称
                    'strAlternate': team.get('strAlternate'),  # 别名
                    'intFormedYear': team.get('intFormedYear'),  # 成立年份
                    'strStadium': team.get('strStadium'),  # 体育场
                    'strCountry': team.get('strCountry'),  # 国家
                    'strLeague': team.get('strLeague'),  # 联赛
                    'strSport': team.get('strSport'),  # 运动类型
                    'strBadge': team.get('strBadge'),  # 队徽
                    'strLogo': team.get('strLogo'),  # Logo
                    'strDescriptionEN': team.get('strDescriptionEN', '')[:200],  # 英文描述（截取）
                    'strDescriptionCN': None,  # 中文描述（需手动添加）
                }
                team_list.append(team_data)
            
            return team_list
        else:
            print(f"    ✗ 错误: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"    ✗ 错误: {str(e)}")
        return []

def get_team_details(team_id):
    """获取球队详细信息"""
    print(f"  获取球队详情 (ID: {team_id})...")
    
    url = f"{BASE_URL}/lookupteam.php"
    params = {"id": team_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            
            if teams:
                team = teams[0]
                print(f"    ✓ 成功获取详情")
                return team
            else:
                print(f"    ✗ 未找到球队")
                return None
        else:
            print(f"    ✗ 错误: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"    ✗ 错误: {str(e)}")
        return None

def get_players_by_team(team_id):
    """获取球队的球员阵容"""
    print(f"  获取球队阵容 (ID: {team_id})...")
    
    url = f"{BASE_URL}/lookupplayers.php"
    params = {"id": team_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            players = data.get('player', [])
            print(f"    找到 {len(players)} 名球员")
            
            # 提取关键信息
            player_list = []
            for player in players:
                player_data = {
                    'idPlayer': player.get('idPlayer'),
                    'strPlayer': player.get('strPlayer'),  # 姓名
                    'strNationality': player.get('strNationality'),  # 国籍
                    'strPosition': player.get('strPosition'),  # 位置
                    'dateBorn': player.get('dateBorn'),  # 出生日期
                    'strNumber': player.get('strNumber'),  # 球衣号码
                    'strHeight': player.get('strHeight'),  # 身高
                    'strWeight': player.get('strWeight'),  # 体重
                    'strThumb': player.get('strThumb'),  # 头像
                }
                player_list.append(player_data)
            
            return player_list
        else:
            print(f"    ✗ 错误: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"    ✗ 错误: {str(e)}")
        return []

def explore_leagues():
    """探索主要联赛"""
    print("\n" + "="*80)
    print("2. 探索主要联赛")
    print("="*80)
    
    # 测试的联赛列表
    leagues_to_test = [
        "English Premier League",  # 英超
        "Spanish La Liga",  # 西甲
        "German Bundesliga",  # 德甲
        "Italian Serie A",  # 意甲
        "French Ligue 1",  # 法甲
        "Japanese J1 League",  # 日职联
        "Korean K League",  # 韩K联
        "Saudi Professional League",  # 沙职联
        "Chinese Super League",  # 中超
    ]
    
    all_leagues_data = {}
    
    for league in leagues_to_test:
        print(f"\n测试联赛: {league}")
        teams = get_league_teams(league)
        
        if teams:
            all_leagues_data[league] = {
                'league_name': league,
                'team_count': len(teams),
                'teams': teams[:5]  # 只保存前5支作为示例
            }
            print(f"  ✓ 成功获取 {len(teams)} 支球队（保存前5支示例）")
        else:
            print(f"  ✗ 未找到数据")
        
        # 延迟避免速率限制
        import time
        time.sleep(1)
    
    save_json(all_leagues_data, 'leagues_exploration.json')
    print(f"\n✓ 联赛探索完成，共测试 {len(leagues_to_test)} 个联赛")
    
    return all_leagues_data

def detailed_team_analysis():
    """详细球队分析"""
    print("\n" + "="*80)
    print("3. 详细球队分析示例")
    print("="*80)
    
    # 选择几个代表性球队进行详细分析
    sample_teams = [
        ("Arsenal", "133604"),  # 阿森纳
        ("Real Madrid", "133602"),  # 皇马
        ("Vissel Kobe", "134777"),  # 神户胜利船（日职联）
    ]
    
    detailed_data = []
    
    for team_name, team_id in sample_teams:
        print(f"\n分析球队: {team_name}")
        
        # 获取球队详情
        details = get_team_details(team_id)
        
        if details:
            # 获取球员阵容
            players = get_players_by_team(team_id)
            
            team_analysis = {
                'team_info': details,
                'players': players,
                'player_count': len(players)
            }
            
            detailed_data.append(team_analysis)
            print(f"  ✓ 完成分析（{len(players)} 名球员）")
        
        # 延迟
        import time
        time.sleep(1)
    
    save_json(detailed_data, 'detailed_team_analysis.json')
    print(f"\n✓ 详细分析完成，共分析 {len(detailed_data)} 支球队")
    
    return detailed_data

def generate_summary(leagues_data, detailed_data):
    """生成摘要报告"""
    print("\n" + "="*80)
    print("4. 生成摘要报告")
    print("="*80)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'api_info': {
            'name': 'TheSportsDB',
            'version': 'v1',
            'free_tier_limit': '100 requests/day',
            'api_key_used': API_KEY
        },
        'leagues_tested': len(leagues_data),
        'leagues_with_data': sum(1 for l in leagues_data.values() if l['team_count'] > 0),
        'teams_analyzed': len(detailed_data),
        'total_players_found': sum(d.get('player_count', 0) for d in detailed_data),
        'leagues_summary': [
            {
                'league': name,
                'teams_found': data['team_count'],
                'sample_teams': [t['strTeam'] for t in data['teams']]
            }
            for name, data in leagues_data.items()
        ],
        'coverage_assessment': {
            'european_leagues': '✅ 覆盖良好',
            'asian_leagues': '⚠️ 部分覆盖（需要验证）',
            'chinese_leagues': '❓ 需要测试',
            'data_quality': '中等（免费版本）'
        }
    }
    
    save_json(summary, 'summary_report.json')
    
    print(f"\nTheSportsDB API 评估:")
    print(f"  测试联赛数: {summary['leagues_tested']}")
    print(f"  有数据的联赛: {summary['leagues_with_data']}")
    print(f"  详细分析球队: {summary['teams_analyzed']}")
    print(f"  总球员数: {summary['total_players_found']}")

def main():
    print("="*80)
    print("TheSportsDB API 测试")
    print(f"开始时间: {datetime.now()}")
    print("="*80)
    
    try:
        # 1. 测试API连接
        if not test_api_connection():
            print("\n✗ API连接失败，终止测试")
            return
        
        # 2. 探索联赛
        leagues_data = explore_leagues()
        
        # 3. 详细球队分析
        detailed_data = detailed_team_analysis()
        
        # 4. 生成摘要
        generate_summary(leagues_data, detailed_data)
        
        print("\n" + "="*80)
        print("✓ TheSportsDB API 测试完成！")
        print(f"所有数据已保存到: {OUTPUT_DIR}")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
