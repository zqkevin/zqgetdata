"""
完善球员数据：翻译所有球员并自动拆分名字和姓氏
"""
import json
import time
from pathlib import Path
import sys

# 添加api_football_test目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "api_football_test"))
from baidu_translate import translate_text, load_translation_cache, save_translation_cache

DATA_DIR = Path(__file__).parent / "data"
CACHE_FILE = Path(__file__).parent / "translations_cache.json"


def split_name(full_name):
    """
    拆分全名为名字和姓氏
    
    Args:
        full_name: 全名（如 "Lucas Emanuel" 或 "卢卡斯·伊曼纽尔"）
    
    Returns:
        (first_name, last_name) 元组
    """
    if not full_name or full_name.strip() == '':
        return None, None
    
    # 中文名称：按分隔符拆分
    if any(c in full_name for c in ['·', ' ', '・']):
        # 尝试常见分隔符
        for sep in ['·', ' ', '・']:
            if sep in full_name:
                parts = full_name.split(sep)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
                elif len(parts) > 2:
                    # 多个部分：第一部分是名，其余是姓
                    return parts[0].strip(), ' '.join(parts[1:]).strip()
    
    # 英文名称：按空格拆分
    if ' ' in full_name:
        parts = full_name.split(' ')
        if len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) > 2:
            # 多个单词：第一个是名，最后一个是姓，中间的是中间名（归入姓）
            return parts[0], ' '.join(parts[1:])
    
    # 无法拆分，返回None
    return None, None


def translate_player_name(name_en):
    """
    翻译球员名称（带缓存）
    
    Args:
        name_en: 英文姓名
    
    Returns:
        中文姓名
    """
    if not name_en or name_en.strip() == '':
        return None
    
    # 加载缓存
    cache = load_translation_cache(str(CACHE_FILE))
    
    # 检查缓存
    if name_en in cache:
        return cache[name_en]
    
    # 调用翻译API
    name_zh = translate_text(name_en, 'en', 'zh')
    
    # 保存到缓存
    if name_zh:
        cache[name_en] = name_zh
        save_translation_cache(cache, str(CACHE_FILE))
    
    # 控制频率
    time.sleep(1.2)
    
    return name_zh


def complete_player_data():
    """
    完善所有球员数据：翻译并拆分名字
    """
    file_path = DATA_DIR / "teams_with_players.json"
    
    print("=" * 80)
    print("👥 完善球员数据")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    print(f"\n📂 加载数据: {len(teams)} 支球队\n")
    
    total_players = 0
    translated_players = 0
    need_translate = 0
    
    # 统计需要翻译的球员数量
    for team in teams:
        players = team.get('players', [])
        total_players += len(players)
        
        for player in players:
            if not player.get('name_zh_full'):
                need_translate += 1
    
    print(f"📊 统计信息:")
    print(f"   总球员数: {total_players}")
    print(f"   需要翻译: {need_translate}")
    print(f"   已翻译: {total_players - need_translate}")
    print()
    
    # 开始翻译
    current = 0
    for i, team in enumerate(teams, 1):
        team_name = team.get('name_en', '')
        players = team.get('players', [])
        
        print(f"[{i}/{len(teams)}] 球队: {team_name} ({len(players)} 名球员)")
        
        for j, player in enumerate(players, 1):
            name_en = player.get('name_en', '')
            name_en_full = player.get('name_en_full', '')
            
            # 如果已经有中文全名，只需拆分
            if player.get('name_zh_full'):
                name_zh_full = player['name_zh_full']
                
                # 拆分中文名字
                if not player.get('first_name_zh') or not player.get('last_name_zh'):
                    first_zh, last_zh = split_name(name_zh_full)
                    if first_zh:
                        player['first_name_zh'] = first_zh
                    if last_zh:
                        player['last_name_zh'] = last_zh
                
                # 拆分英文名字（如果还没有）
                if not player.get('first_name_en') or not player.get('last_name_en'):
                    first_en, last_en = split_name(name_en_full or name_en)
                    if first_en:
                        player['first_name_en'] = first_en
                    if last_en:
                        player['last_name_en'] = last_en
                
                continue
            
            # 需要翻译
            current += 1
            print(f"   [{current}/{need_translate}] 翻译: {name_en_full or name_en}")
            
            # 翻译全名
            name_zh_full = translate_player_name(name_en_full or name_en)
            if name_zh_full:
                player['name_zh_full'] = name_zh_full
                player['name_zh'] = name_zh_full  # 兼容旧字段
                translated_players += 1
                print(f"      ✅ {name_zh_full}")
                
                # 拆分中文名字
                first_zh, last_zh = split_name(name_zh_full)
                if first_zh:
                    player['first_name_zh'] = first_zh
                if last_zh:
                    player['last_name_zh'] = last_zh
            
            # 拆分英文名字
            first_en, last_en = split_name(name_en_full or name_en)
            if first_en:
                player['first_name_en'] = first_en
            if last_en:
                player['last_name_en'] = last_en
    
    # 保存数据
    print(f"\n💾 保存数据...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成!")
    print(f"   总球员数: {total_players}")
    print(f"   新翻译: {translated_players}")
    print(f"   已保存: {file_path}")


if __name__ == '__main__':
    complete_player_data()
