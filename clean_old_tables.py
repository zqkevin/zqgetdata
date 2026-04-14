# -*- coding: utf-8 -*-
"""
清理旧的数据库表
删除重构后遗留的旧表 (football_match, spf_odds 等)
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from config import config
from sqlalchemy import create_engine, text

def clean_old_tables():
    """删除旧的数据库表"""
    db_config = config['local']
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    # 需要删除的旧表列表
    old_tables = [
        'football_match',      # 已被 tczq_match 和 bjdc_match 替代
        'spf_odds',            # 已被 tczq_spf_odds 和 bjdc_spf_odds 替代
        'handicap_spf_odds',   # 已被 tczq_handicap_spf_odds 和 bjdc_handicap_spf_odds 替代
        'score_odds',          # 已被 tczq_score_odds 和 bjdc_score_odds 替代
        'total_goal_odds',     # 已被 tczq_total_goal_odds 和 bjdc_total_goal_odds 替代
        'ht_ft_odds',          # 已被 tczq_ht_ft_odds 和 bjdc_ht_ft_odds 替代
        'match_result',        # 已被 tczq_match_result 和 bjdc_match_result 替代
        'odds_change_log',     # 已被 tczq_odds_change_log 和 bjdc_odds_change_log 替代
    ]
    
    print("=" * 60)
    print("=== 清理旧的数据库表 ===")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # 先禁用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            deleted_count = 0
            for table_name in old_tables:
                try:
                    # 检查表是否存在
                    result = conn.execute(text(
                        f"SELECT COUNT(*) FROM information_schema.tables "
                        f"WHERE table_schema = '{db_config['database']}' AND table_name = '{table_name}'"
                    )).fetchone()
                    
                    if result[0] > 0:
                        # 删除表
                        conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
                        print(f"✓ 已删除旧表：{table_name}")
                        deleted_count += 1
                    else:
                        print(f"- 表 {table_name} 不存在，跳过")
                        
                except Exception as e:
                    print(f"✗ 删除表 {table_name} 失败：{str(e)}")
            
            # 重新启用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
            
            print("\n" + "=" * 60)
            print(f"清理完成！共删除 {deleted_count} 个旧表")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\n❌ 清理失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = clean_old_tables()
    if success:
        print("\n✅ 清理操作完成!")
    else:
        print("\n❌ 清理操作失败，请检查错误信息")
