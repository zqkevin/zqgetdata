"""
翻译质量检查工具
自动检测可能的翻译错误
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def check_translation_quality():
    """
    检查翻译质量，找出可能的问题
    """
    print("=" * 80)
    print("🔍 翻译质量检查")
    print("=" * 80)
    
    file_path = DATA_DIR / "countries.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        countries = json.load(f)
    
    print(f"\n📂 检查 {len(countries)} 个国家/地区的翻译\n")
    
    issues = []
    
    # 1. 检查缩写被误翻译的情况
    abbreviation_patterns = [
        ('企业形象系统', 'CIS'),
        ('企业', None),
        ('公司', None),
        ('品牌', None),
        ('系统', None),
    ]
    
    for country in countries:
        name_en = country.get('name_en', '')
        name_zh = country.get('name_zh', '')
        
        if not name_zh:
            continue
        
        # 检查是否包含可疑词汇
        for suspicious, expected_en in abbreviation_patterns:
            if suspicious in name_zh:
                issues.append({
                    'type': '疑似缩写误译',
                    'name_en': name_en,
                    'name_zh': name_zh,
                    'suspicious': suspicious,
                    'expected': expected_en
                })
    
    # 2. 检查过长的翻译（可能是描述而非名称）
    for country in countries:
        name_en = country.get('name_en', '')
        name_zh = country.get('name_zh', '')
        
        if name_zh and len(name_zh) > 20:
            issues.append({
                'type': '翻译过长',
                'name_en': name_en,
                'name_zh': name_zh,
                'length': len(name_zh)
            })
    
    # 3. 检查纯英文未翻译的情况
    for country in countries:
        name_en = country.get('name_en', '')
        name_zh = country.get('name_zh', '')
        
        if name_zh and name_zh == name_en:
            issues.append({
                'type': '未翻译',
                'name_en': name_en,
                'name_zh': name_zh
            })
    
    # 输出检查结果
    if issues:
        print(f"⚠️  发现 {len(issues)} 个潜在问题:\n")
        
        for i, issue in enumerate(issues, 1):
            print(f"[{i}] {issue['type']}")
            print(f"    英文: {issue['name_en']}")
            print(f"    中文: {issue['name_zh']}")
            
            if 'suspicious' in issue:
                print(f"    可疑词: {issue['suspicious']}")
                if issue.get('expected'):
                    print(f"    期望: {issue['expected']}")
            
            if 'length' in issue:
                print(f"    长度: {issue['length']} 字符")
            
            print()
    else:
        print("✅ 未发现明显问题！\n")
    
    # 统计信息
    translated = sum(1 for c in countries if c.get('name_zh'))
    print(f"📊 统计信息:")
    print(f"   总数: {len(countries)}")
    print(f"   已翻译: {translated}")
    print(f"   未翻译: {len(countries) - translated}")
    print(f"   问题数: {len(issues)}")
    print(f"   质量评分: {(translated - len(issues)) / len(countries) * 100:.1f}%")


if __name__ == '__main__':
    check_translation_quality()
