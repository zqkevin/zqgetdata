"""
清理leagues.json中的冗余字段
删除 name_zh 字段，只保留 name_zh_full 和 name_zh_short
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def clean_leagues():
    """
    清理leagues.json
    """
    file_path = DATA_DIR / "leagues.json"
    
    print("=" * 80)
    print("🧹 清理 leagues.json 冗余字段")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        leagues = json.load(f)
    
    print(f"\n📂 加载数据: {len(leagues)} 个联赛")
    
    cleaned_count = 0
    
    for league in leagues:
        # 如果有 name_zh_full，则删除 name_zh
        if 'name_zh' in league and 'name_zh_full' in league:
            old_value = league['name_zh']
            del league['name_zh']
            cleaned_count += 1
            print(f"   🗑️  {league['name_en']}: 删除 name_zh='{old_value}'")
    
    # 保存数据
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(leagues, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已清理 {cleaned_count} 个冗余字段")
    print(f"✅ 已保存: {file_path}")


if __name__ == '__main__':
    clean_leagues()
