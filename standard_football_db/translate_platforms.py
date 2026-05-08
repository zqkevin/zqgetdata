"""
翻译TheSportsDB和API-Football的数据
"""
import json
import time
import sys
from pathlib import Path

# 添加baidu_translate目录到路径
sys.path.insert(0, str(Path(__file__).parent / "tools" / "baidu_translate"))
from baidu_translate import translate_text, load_translation_cache, save_translation_cache

DATA_DIR = Path(__file__).parent / "tools"
CACHE_FILE = Path(__file__).parent / "tools" / "baidu_translate" / "translations_cache.json"


def translate_thesportsdb():
    """翻译TheSportsDB的球队描述"""
    print("=" * 80)
    print("🌐 翻译 TheSportsDB 数据")
    print("=" * 80)
    
    file_path = DATA_DIR / "thesportsdb" / "data" / "detailed_team_analysis.json"
    
    if not file_path.exists():
        print("❌ 文件不存在")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📂 加载数据: {len(data)} 条记录\n")
    
    # 去重（只处理唯一的球队）
    unique_teams = {}
    for item in data:
        team_info = item.get('team_info', {})
        team_id = team_info.get('idTeam', '')
        if team_id and team_id not in unique_teams:
            unique_teams[team_id] = item
    
    print(f"🔍 去重后: {len(unique_teams)} 支唯一球队\n")
    
    translated_count = 0
    
    for team_id, item in unique_teams.items():
        team_info = item.get('team_info', {})
        strTeam = team_info.get('strTeam', '')
        strDescriptionEN = team_info.get('strDescriptionEN', '')
        
        print(f"📝 球队: {strTeam} (ID: {team_id})")
        
        # 翻译球队描述
        if strDescriptionEN and not team_info.get('strDescriptionCN'):
            print(f"   🔄 翻译描述...")
            
            # 由于描述很长，分段翻译或跳过
            # 这里我们只翻译前500字符作为示例
            desc_preview = strDescriptionEN[:500] + "..." if len(strDescriptionEN) > 500 else strDescriptionEN
            
            # 检查缓存
            cache = load_translation_cache(str(CACHE_FILE))
            
            if desc_preview in cache:
                desc_zh = cache[desc_preview]
                print(f"   ✅ 从缓存获取")
            else:
                # 翻译简短版本
                desc_zh = translate_text(desc_preview[:200], 'en', 'zh')  # 只翻译前200字符
                if desc_zh:
                    cache[desc_preview[:200]] = desc_zh
                    save_translation_cache(cache, str(CACHE_FILE))
                    time.sleep(1.2)
                    print(f"   ✅ 已翻译: {desc_zh[:50]}...")
            
            team_info['strDescriptionCN'] = desc_zh
            translated_count += 1
        
        # 翻译其他可能的字段
        strCountry = team_info.get('strCountry', '')
        if strCountry:
            cache = load_translation_cache(str(CACHE_FILE))
            if strCountry not in cache:
                country_zh = translate_text(strCountry, 'en', 'zh')
                if country_zh:
                    cache[strCountry] = country_zh
                    save_translation_cache(cache, str(CACHE_FILE))
                    time.sleep(1.2)
                    print(f"   🌍 国家: {strCountry} → {country_zh}")
                team_info['strCountryZH'] = country_zh
            else:
                team_info['strCountryZH'] = cache[strCountry]
                print(f"   🌍 国家: {strCountry} → {cache[strCountry]} (缓存)")
    
    # 保存数据
    print(f"\n💾 保存数据...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成!")
    print(f"   翻译球队描述: {translated_count}")
    print(f"   已保存: {file_path}")


def translate_api_football():
    """翻译API-Football的联赛和国家名称"""
    print("\n" + "=" * 80)
    print("🌐 翻译 API-Football 数据")
    print("=" * 80)
    
    file_path = DATA_DIR / "api-football" / "data" / "leagues_info.json"
    
    if not file_path.exists():
        print("❌ 文件不存在")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        leagues = json.load(f)
    
    print(f"\n📂 加载数据: {len(leagues)} 个联赛\n")
    
    # API-Football的数据已经有中文键名，但我们需要提取纯英文名称
    # 并添加标准化的中文字段
    
    translated_count = 0
    
    for league_name_cn_en, info in leagues.items():
        # 解析键名："英超 (Premier League)" → "Premier League"
        if '(' in league_name_cn_en and ')' in league_name_cn_en:
            name_en = league_name_cn_en.split('(')[1].split(')')[0].strip()
            name_cn = league_name_cn_en.split('(')[0].strip()
        else:
            name_en = league_name_cn_en
            name_cn = None
        
        print(f"📝 联赛: {name_en}")
        
        # 翻译国家名称
        country_en = info.get('country', '')
        if country_en:
            cache = load_translation_cache(str(CACHE_FILE))
            
            if country_en not in cache:
                country_zh = translate_text(country_en, 'en', 'zh')
                if country_zh:
                    cache[country_en] = country_zh
                    save_translation_cache(cache, str(CACHE_FILE))
                    time.sleep(1.2)
                    print(f"   🌍 国家: {country_en} → {country_zh}")
                
                # 添加到info中
                info['country_zh'] = country_zh
                translated_count += 1
            else:
                info['country_zh'] = cache[country_en]
                print(f"   🌍 国家: {country_en} → {cache[country_en]} (缓存)")
        
        # 添加标准化的名称字段
        info['name_en'] = name_en
        if name_cn:
            info['name_zh'] = name_cn
        else:
            # 如果没有中文，尝试翻译
            cache = load_translation_cache(str(CACHE_FILE))
            if name_en not in cache:
                name_zh = translate_text(name_en, 'en', 'zh')
                if name_zh:
                    cache[name_en] = name_zh
                    save_translation_cache(cache, str(CACHE_FILE))
                    time.sleep(1.2)
                    info['name_zh'] = name_zh
                    print(f"   ✅ 联赛名: {name_en} → {name_zh}")
                    translated_count += 1
            else:
                info['name_zh'] = cache[name_en]
                print(f"   ✅ 联赛名: {name_en} → {cache[name_en]} (缓存)")
    
    # 保存数据
    print(f"\n💾 保存数据...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(leagues, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成!")
    print(f"   新增翻译: {translated_count}")
    print(f"   已保存: {file_path}")


if __name__ == '__main__':
    translate_thesportsdb()
    translate_api_football()
