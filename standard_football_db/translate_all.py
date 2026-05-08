"""
统一翻译和数据整理工具
遍历所有JSON数据文件，翻译英文名称为中文，并按照标准字段规范整理数据
"""
import json
import time
from pathlib import Path
import sys

# 添加api_football_test目录到路径，以便导入百度翻译模块
sys.path.insert(0, str(Path(__file__).parent.parent / "api_football_test"))
from baidu_translate import translate_text, load_translation_cache, save_translation_cache

# 数据目录
DATA_DIR = Path(__file__).parent / "data"

# 缓存文件
CACHE_FILE = Path(__file__).parent / "translations_cache.json"


def translate_with_cache(text, from_lang='en', to_lang='zh'):
    """
    带缓存的翻译函数
    
    Args:
        text: 要翻译的文本
        from_lang: 源语言
        to_lang: 目标语言
    
    Returns:
        翻译后的文本
    """
    if not text or text.strip() == '':
        return None
    
    # 加载缓存
    cache = load_translation_cache(str(CACHE_FILE))
    
    # 检查缓存
    if text in cache:
        return cache[text]
    
    # 调用翻译API
    translated = translate_text(text, from_lang, to_lang)
    
    # 保存到缓存
    if translated:
        cache[text] = translated
        save_translation_cache(cache, str(CACHE_FILE))
    
    # 控制频率
    time.sleep(1.2)
    
    return translated


def get_short_name(full_name):
    """
    从全称生成简称（简单规则）
    
    Args:
        full_name: 全名
    
    Returns:
        简称
    """
    if not full_name:
        return None
    
    # 移除常见后缀
    short = full_name
    for suffix in [' FC', ' Club', ' United', ' City', ' Association']:
        if short.endswith(suffix):
            short = short[:-len(suffix)]
            break
    
    return short if short != full_name else None


def translate_countries():
    """
    翻译countries.json
    """
    print("\n" + "=" * 80)
    print("🌍 翻译 countries.json")
    print("=" * 80)
    
    file_path = DATA_DIR / "countries.json"
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        countries = json.load(f)
    
    print(f"📂 加载数据: {len(countries)} 个国家/地区")
    
    # 统计需要翻译的数量
    need_translate = [c for c in countries if not c.get('name_zh')]
    print(f"   需要翻译: {len(need_translate)} 个")
    
    # 翻译国家名称
    for i, country in enumerate(need_translate, 1):
        name_en = country.get('name_en', '')
        if name_en:
            print(f"[{i}/{len(need_translate)}] 翻译: {name_en}")
            name_zh = translate_with_cache(name_en)
            if name_zh:
                country['name_zh'] = name_zh
                print(f"   ✅ {name_zh}")
            
            # 翻译父区域名称
            parent_name_en = country.get('parent_area_name_en', '')
            if parent_name_en and not country.get('parent_area_name_zh'):
                parent_name_zh = translate_with_cache(parent_name_en)
                if parent_name_zh:
                    country['parent_area_name_zh'] = parent_name_zh
    
    # 保存数据
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(countries, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存: {file_path}")


def translate_leagues():
    """
    翻译leagues.json并清理冗余字段
    """
    print("\n" + "=" * 80)
    print("⚽ 翻译 leagues.json")
    print("=" * 80)
    
    file_path = DATA_DIR / "leagues.json"
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        leagues = json.load(f)
    
    print(f"📂 加载数据: {len(leagues)} 个联赛")
    
    # 统计需要翻译的数量
    need_translate = [l for l in leagues if not l.get('name_zh_full')]
    print(f"   需要翻译: {len(need_translate)} 个")
    
    # 翻译联赛名称
    for i, league in enumerate(need_translate, 1):
        name_en = league.get('name_en', '')
        name_en_full = league.get('name_en_full', '')
        
        if name_en_full and not league.get('name_zh_full'):
            print(f"[{i}/{len(need_translate)}] 翻译: {name_en_full}")
            
            # 翻译全称
            name_zh_full = translate_with_cache(name_en_full)
            if name_zh_full:
                league['name_zh_full'] = name_zh_full
                print(f"   ✅ 全称: {name_zh_full}")
            
            # 生成简称（如果有英文简称）
            name_en_short = league.get('name_en_short')
            if name_en_short and not league.get('name_zh_short'):
                name_zh_short = translate_with_cache(name_en_short)
                if name_zh_short:
                    league['name_zh_short'] = name_zh_short
                    print(f"   ✅ 简称: {name_zh_short}")
            elif not league.get('name_zh_short') and name_zh_full:
                # 如果没有简称，从全称生成
                short_candidate = get_short_name(name_zh_full)
                if short_candidate:
                    league['name_zh_short'] = short_candidate
        
        # 清理冗余字段：删除旧的 name_zh 字段
        if 'name_zh' in league and 'name_zh_full' in league:
            del league['name_zh']
            print(f"   🗑️  删除冗余字段: name_zh")
        
        # 翻译区域名称
        area_name_en = league.get('area_name_en', '')
        if area_name_en and not league.get('area_name_zh'):
            area_name_zh = translate_with_cache(area_name_en)
            if area_name_zh:
                league['area_name_zh'] = area_name_zh
    
    # 保存数据
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(leagues, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存: {file_path}")


def translate_teams_and_players():
    """
    翻译teams_with_players.json（球队和球员）
    """
    print("\n" + "=" * 80)
    print("🏆 翻译 teams_with_players.json")
    print("=" * 80)
    
    file_path = DATA_DIR / "teams_with_players.json"
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    print(f"📂 加载数据: {len(teams)} 支球队")
    
    # 统计需要翻译的球队数量
    teams_need_translate = [t for t in teams if not t.get('name_zh_full')]
    print(f"   需要翻译球队: {len(teams_need_translate)} 支")
    
    # 翻译球队名称
    for i, team in enumerate(teams_need_translate, 1):
        name_en = team.get('name_en', '')
        name_en_full = team.get('name_en_full', '')
        name_en_short = team.get('name_en_short', '')
        
        print(f"\n[{i}/{len(teams_need_translate)}] 球队: {name_en_full or name_en}")
        
        # 翻译球队全称
        if name_en_full and not team.get('name_zh_full'):
            name_zh_full = translate_with_cache(name_en_full)
            if name_zh_full:
                team['name_zh_full'] = name_zh_full
                print(f"   ✅ 全称: {name_zh_full}")
        
        # 翻译球队简称
        if name_en_short and not team.get('name_zh_short'):
            name_zh_short = translate_with_cache(name_en_short)
            if name_zh_short:
                team['name_zh_short'] = name_zh_short
                print(f"   ✅ 简称: {name_zh_short}")
        elif not team.get('name_zh_short') and team.get('name_zh_full'):
            # 如果没有简称，从全称生成
            short_candidate = get_short_name(team['name_zh_full'])
            if short_candidate:
                team['name_zh_short'] = short_candidate
                print(f"   ✅ 简称(生成): {short_candidate}")
        
        # 翻译区域名称
        area_name_en = team.get('area_name_en', '')
        if area_name_en and not team.get('area_name_zh'):
            area_name_zh = translate_with_cache(area_name_en)
            if area_name_zh:
                team['area_name_zh'] = area_name_zh
        
        # 翻译教练名称
        coach = team.get('coach')
        if coach:
            coach_name_en = coach.get('name_en', '')
            if coach_name_en and not coach.get('name_zh'):
                coach_name_zh = translate_with_cache(coach_name_en)
                if coach_name_zh:
                    coach['name_zh'] = coach_name_zh
                    print(f"   ✅ 教练: {coach_name_zh}")
        
        # 翻译球员名称（限制数量，避免过多请求）
        players = team.get('players', [])
        players_need_translate = [p for p in players if not p.get('name_zh_full')]
        
        if players_need_translate:
            print(f"   📝 球员: {len(players_need_translate)} 人（仅翻译前5人作为示例）")
            
            for j, player in enumerate(players_need_translate[:5], 1):
                player_name_en = player.get('name_en', '')
                player_name_full = player.get('name_en_full', '')
                
                if player_name_full and not player.get('name_zh_full'):
                    player_name_zh = translate_with_cache(player_name_full)
                    if player_name_zh:
                        player['name_zh_full'] = player_name_zh
                        
                        # 翻译名字和姓氏
                        first_name_en = player.get('first_name_en')
                        last_name_en = player.get('last_name_en')
                        
                        if first_name_en and not player.get('first_name_zh'):
                            first_name_zh = translate_with_cache(first_name_en)
                            if first_name_zh:
                                player['first_name_zh'] = first_name_zh
                        
                        if last_name_en and not player.get('last_name_zh'):
                            last_name_zh = translate_with_cache(last_name_en)
                            if last_name_zh:
                                player['last_name_zh'] = last_name_zh
            
            if len(players_need_translate) > 5:
                print(f"   ⚠️  剩余 {len(players_need_translate) - 5} 名球员未翻译（可后续批量处理）")
    
    # 保存数据
    print(f"\n💾 保存数据...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存: {file_path}")


def main():
    """
    主函数：执行所有翻译任务
    """
    print("=" * 80)
    print("🌐 统一翻译和数据整理工具")
    print("=" * 80)
    print("\n⚠️  注意：翻译大量数据需要较长时间，请确保网络连接稳定")
    print("   建议使用缓存机制，避免重复翻译")
    
    # 询问用户选择
    print("\n请选择要执行的任务:")
    print("1. 翻译 countries.json")
    print("2. 翻译 leagues.json")
    print("3. 翻译 teams_with_players.json（耗时较长）")
    print("4. 全部翻译")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == '1':
        translate_countries()
    elif choice == '2':
        translate_leagues()
    elif choice == '3':
        translate_teams_and_players()
    elif choice == '4':
        translate_countries()
        translate_leagues()
        translate_teams_and_players()
    else:
        print("❌ 无效选项")
        return
    
    print("\n" + "=" * 80)
    print("🎉 所有任务完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
