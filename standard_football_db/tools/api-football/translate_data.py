"""
翻译API-Football获取的数据
将英文名称翻译为中文，并保存为双语数据
"""
import json
from pathlib import Path
from baidu_translate import translate_teams, translate_leagues, load_translation_cache

# 数据目录
DATA_DIR = Path(__file__).parent / "data_optimized"

def translate_asian_leagues_data():
    """
    翻译亚洲联赛数据
    """
    print("=" * 80)
    print("🌏 翻译亚洲联赛数据")
    print("=" * 80)
    
    # 加载数据
    data_file = DATA_DIR / "phase1_league_teams.json"
    if not data_file.exists():
        print(f"❌ 数据文件不存在: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        leagues_data = json.load(f)
    
    print(f"\n📂 加载数据: {data_file.name}")
    print(f"   联赛数量: {len(leagues_data)}")
    
    # 提取所有球队
    all_teams = []
    league_names = list(leagues_data.keys())
    
    for league_name, league_info in leagues_data.items():
        if 'teams' in league_info:
            all_teams.extend(league_info['teams'])
    
    print(f"   球队总数: {len(all_teams)}")
    
    # 翻译联赛名称
    print("\n" + "=" * 80)
    # 将联赛名称转换为列表格式
    league_list = [{'name': name} for name in league_names]
    league_translations = translate_leagues(league_list, 'translations_cache.json')
    
    # 翻译球队名称
    print("\n" + "=" * 80)
    team_translations = translate_teams(all_teams, 'translations_cache.json')
    
    # 更新数据，添加中文字段
    print("\n" + "=" * 80)
    print("💾 更新数据，添加中文字段")
    print("=" * 80)
    
    for league_name, league_info in leagues_data.items():
        # 添加联赛中文名
        league_name_en = league_name
        league_info['name_zh'] = league_translations.get(league_name_en, league_name_en)
        
        print(f"\n⚽ {league_name_en} → {league_info['name_zh']}")
        
        # 添加球队中文名
        if 'teams' in league_info:
            for team in league_info['teams']:
                team_name_en = team.get('name', '')
                team['name_zh'] = team_translations.get(team_name_en, team_name_en)
                
                # 添加国家中文名
                country_en = team.get('country', '')
                if country_en:
                    # 国家名也需要翻译
                    country_cache = load_translation_cache('translations_cache.json')
                    team['country_zh'] = country_cache.get(country_en, country_en)
    
    # 保存翻译后的数据
    output_file = DATA_DIR / "phase1_league_teams_bilingual.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(leagues_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 双语数据已保存: {output_file}")
    
    # 生成翻译统计报告
    stats = {
        'leagues_total': len(leagues_data),
        'teams_total': len(all_teams),
        'league_translations': len([name for name, info in leagues_data.items() if info.get('name_zh')]),
        'team_translations': sum([
            len([t for t in info.get('teams', []) if t.get('name_zh')])
            for info in leagues_data.values()
        ])
    }
    
    stats_file = DATA_DIR / "translation_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 翻译统计:")
    print(f"   联赛: {stats['league_translations']}/{stats['leagues_total']}")
    print(f"   球队: {stats['team_translations']}/{stats['teams_total']}")


def create_bilingual_mapping():
    """
    创建中英文映射表（供其他项目使用）
    """
    print("\n" + "=" * 80)
    print("📋 创建中英文映射表")
    print("=" * 80)
    
    cache = load_translation_cache('translations_cache.json')
    
    if not cache:
        print("⚠️  缓存为空，请先运行翻译任务")
        return
    
    # 分类整理
    mapping = {
        'teams': {},
        'leagues': {},
        'countries': {}
    }
    
    for en_name, zh_name in cache.items():
        if zh_name is None:
            continue
        
        # 简单分类（可以根据需要优化）
        if any(keyword in en_name.lower() for keyword in ['league', 'cup', 'championship']):
            mapping['leagues'][en_name] = zh_name
        elif any(keyword in en_name.lower() for keyword in ['china', 'japan', 'korea', 'england', 'france']):
            mapping['countries'][en_name] = zh_name
        else:
            mapping['teams'][en_name] = zh_name
    
    # 保存映射表
    mapping_file = DATA_DIR / "bilingual_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 映射表已保存: {mapping_file}")
    print(f"   球队: {len(mapping['teams'])}")
    print(f"   联赛: {len(mapping['leagues'])}")
    print(f"   国家: {len(mapping['countries'])}")


if __name__ == '__main__':
    # 执行翻译
    translate_asian_leagues_data()
    
    # 创建映射表
    create_bilingual_mapping()
    
    print("\n" + "=" * 80)
    print("🎉 所有翻译任务完成！")
    print("=" * 80)
