"""
统计TheSportsDB和API-Football的现有数据
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "tools"

def stats_thesportsdb():
    """统计TheSportsDB数据"""
    print("=" * 80)
    print("📊 TheSportsDB 数据统计")
    print("=" * 80)
    
    file_path = DATA_DIR / "thesportsdb" / "data" / "detailed_team_analysis.json"
    
    if not file_path.exists():
        print("❌ 文件不存在")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📂 球队总数: {len(data)}")
    
    # 统计有球员数据的球队
    teams_with_players = [t for t in data if t.get('players') and len(t.get('players', [])) > 0]
    print(f"📝 含球员数据的球队: {len(teams_with_players)}")
    
    total_players = sum(len(t.get('players', [])) for t in data)
    print(f"⚽ 总球员数: {total_players}")
    
    # 检查翻译状态
    translated_teams = 0
    need_translate = []
    
    for team in data:
        team_info = team.get('team_info', {})
        strTeam = team_info.get('strTeam', '')
        strDescriptionCN = team_info.get('strDescriptionCN')
        
        if strDescriptionCN and strDescriptionCN.strip():
            translated_teams += 1
        else:
            need_translate.append(strTeam)
    
    print(f"\n✅ 已翻译球队描述: {translated_teams}")
    print(f"❌ 需要翻译的球队描述: {len(need_translate)}")
    
    if need_translate:
        print(f"\n需要翻译的球队:")
        for name in need_translate[:10]:  # 只显示前10个
            print(f"   - {name}")
        if len(need_translate) > 10:
            print(f"   ... 还有 {len(need_translate) - 10} 个")


def stats_api_football():
    """统计API-Football数据"""
    print("\n" + "=" * 80)
    print("📊 API-Football 数据统计")
    print("=" * 80)
    
    file_path = DATA_DIR / "api-football" / "data" / "leagues_info.json"
    
    if not file_path.exists():
        print("❌ 文件不存在")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        leagues = json.load(f)
    
    print(f"\n📂 联赛总数: {len(leagues)}")
    
    # 统计国家和赛季
    countries = set()
    total_seasons = 0
    
    for name, info in leagues.items():
        countries.add(info.get('country', ''))
        seasons = info.get('seasons', [])
        total_seasons += len(seasons)
    
    print(f"🌍 涉及国家/地区: {len(countries)}")
    print(f"📅 总赛季数: {total_seasons}")
    
    print(f"\n联赛列表:")
    for i, (name, info) in enumerate(leagues.items(), 1):
        country = info.get('country', '')
        league_id = info.get('id', '')
        seasons = info.get('seasons', [])
        current_season = next((s for s in seasons if s.get('current')), None)
        
        print(f"   {i}. {name}")
        print(f"      ID: {league_id}, 国家: {country}")
        if current_season:
            print(f"      当前赛季: {current_season.get('year')} ({current_season.get('start')} 至 {current_season.get('end')})")
    
    # 检查是否有中文翻译
    has_chinese = any('\u4e00' <= char <= '\u9fff' for name in leagues.keys())
    print(f"\n✅ 包含中文名称: {'是' if has_chinese else '否'}")


if __name__ == '__main__':
    stats_thesportsdb()
    stats_api_football()
