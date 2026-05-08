"""
修正countries.json中的错误翻译
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def fix_translation_errors():
    """
    修正常见的翻译错误
    """
    file_path = DATA_DIR / "countries.json"
    
    print("=" * 80)
    print("🔧 修正翻译错误")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        countries = json.load(f)
    
    # 定义修正映射表
    corrections = {
        '火鸡': '土耳其',  # Turkey
        '企业形象系统': '独联体',  # CIS (Commonwealth of Independent States)
        # 可以继续添加其他需要修正的翻译
    }
    
    fixed_count = 0
    
    for country in countries:
        name_zh = country.get('name_zh', '')
        if name_zh in corrections:
            old_name = name_zh
            new_name = corrections[name_zh]
            country['name_zh'] = new_name
            fixed_count += 1
            print(f"   ✅ {country['name_en']}: '{old_name}' → '{new_name}'")
    
    # 保存数据
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(countries, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已修正 {fixed_count} 个错误翻译")
    print(f"✅ 已保存: {file_path}")


if __name__ == '__main__':
    fix_translation_errors()
