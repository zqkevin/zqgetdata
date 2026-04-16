# -*- coding: utf-8 -*-
"""
修复赛果表字段允许 NULL 值
用于处理比赛取消、延期等异常状态的比分数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import localdb


def alter_result_tables():
    """修改赛果表字段，允许 NULL 值"""
    
    tables_to_alter = [
        'bjdc_match_result',
        'tczq_match_result', 
        'jcbk_match_result',
        'tcbk_match_result'
    ]
    
    columns_to_alter = [
        'home_team_goals',
        'away_team_goals',
        'half_time_home_goals',
        'half_time_away_goals',
        'total_goals'
    ]
    
    try:
        # 使用 localdb 的 engine 执行原生 SQL
        with localdb.engine.connect() as conn:
            for table in tables_to_alter:
                print(f"\n处理表: {table}")
                
                # 检查表是否存在
                check_sql = text(f"SHOW TABLES LIKE '{table}'")
                result = conn.execute(check_sql).fetchone()
                
                if not result:
                    print(f"  ⚠️ 表 {table} 不存在，跳过")
                    continue
                
                for column in columns_to_alter:
                    try:
                        # 修改列为允许 NULL
                        alter_sql = text(f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` INT NULL DEFAULT 0")
                        conn.execute(alter_sql)
                        conn.commit()
                        print(f"  ✓ {column} 已修改为允许 NULL")
                    except Exception as e:
                        print(f"  ✗ {column} 修改失败: {e}")
        
        print("\n✅ 所有表结构修改完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 修改表结构失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("修复赛果表字段 - 允许 NULL 值")
    print("=" * 60)
    
    success = alter_result_tables()
    
    if success:
        print("\n提示: 现在可以正常保存异常状态的比赛赛果（比分显示为 NULL）")
    else:
        print("\n错误: 请检查数据库连接和权限")
        sys.exit(1)
