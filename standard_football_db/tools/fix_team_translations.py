"""
批量修正teams_with_players.json中的翻译错误
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def fix_team_translation_errors():
    """
    修正常见的球队翻译错误
    """
    file_path = DATA_DIR / "teams_with_players.json"
    
    print("=" * 80)
    print("🔧 批量修正球队翻译错误")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    print(f"\n📂 加载数据: {len(teams)} 支球队\n")
    
    # 定义修正映射表
    corrections = {
        # 球队名称修正
        '加利福尼亚州巴拉那': '巴拉纳竞技',  # CA Paranaense
        '亚利桑那': '阿尔克马尔',  # AZ
        '日本电气股份有限公司': '奈梅亨',  # NEC
        
        # 教练名称修正（如果有）
    }
    
    # 简称修正映射
    short_name_corrections = {
        'N-乙酰半胱氨酸': '布雷达',  # NAC Breda
        'ajax': '阿贾克斯',  # AFC Ajax
        '继续': '前进之鹰',  # Go Ahead Eagles
        '通信卫星': '特尔斯达',  # Telstar 1963
        '波斯尼亚人H。': '波黑',  # Bosnia-Herzegovina
    }
    
    fixed_count = 0
    
    for team in teams:
        name_en = team.get('name_en', '')
        
        # 修正全称
        name_zh_full = team.get('name_zh_full', '')
        if name_zh_full in corrections:
            old_value = name_zh_full
            new_value = corrections[name_zh_full]
            team['name_zh_full'] = new_value
            fixed_count += 1
            print(f"   ✅ {name_en}: '{old_value}' → '{new_value}' (全称)")
        
        # 修正简称
        name_zh_short = team.get('name_zh_short', '')
        if name_zh_short in short_name_corrections:
            old_value = name_zh_short
            new_value = short_name_corrections[name_zh_short]
            team['name_zh_short'] = new_value
            fixed_count += 1
            print(f"   ✅ {name_en}: '{old_value}' → '{new_value}' (简称)")
    
    # 保存数据
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已修正 {fixed_count} 个翻译错误")
    print(f"✅ 已保存: {file_path}")


if __name__ == '__main__':
    fix_team_translation_errors()
