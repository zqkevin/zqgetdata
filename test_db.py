# -*- coding: utf-8 -*-
"""
数据库测试脚本
用于验证数据库连接和查询是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import localdb
from database.tczq_models import TczqMatch
from sqlalchemy import text

print("=== 数据库测试脚本 ===")

# 测试1: 直接使用SQL查询
print("\n测试1: 直接使用SQL查询")
try:
    # 创建一个新的会话
    session = localdb.session
    
    # 执行SQL查询
    result = session.execute(text("SELECT * FROM tczq_match WHERE status = 0"))
    rows = result.fetchall()
    
    print(f"查询到 {len(rows)} 条记录")
    if rows:
        print("记录示例:")
        for row in rows[:2]:  # 只显示前2条
            print(row)
    else:
        print("没有找到记录")
        
    # 关闭会话
    session.close()
    
except Exception as e:
    print(f"SQL查询失败: {str(e)}")
    import traceback
    traceback.print_exc()

# 测试2: 使用SQLAlchemy ORM查询
print("\n测试2: 使用SQLAlchemy ORM查询")
try:
    # 创建一个新的会话
    session = localdb.session
    
    # 使用ORM查询
    matches = session.query(TczqMatch).filter(TczqMatch.status == 0).all()
    
    print(f"查询到 {len(matches)} 条记录")
    if matches:
        print("记录示例:")
        for match in matches[:2]:  # 只显示前2条
            print(f"比赛ID: {match.match_id}, 比赛名称: {match.match_name}")
    else:
        print("没有找到记录")
        
    # 关闭会话
    session.close()
    
except Exception as e:
    print(f"ORM查询失败: {str(e)}")
    import traceback
    traceback.print_exc()

# 测试3: 测试添加记录
print("\n测试3: 测试添加记录")
try:
    # 创建一个新的会话
    session = localdb.session
    
    # 创建一个测试比赛记录
    test_match = TczqMatch(
        match_id=999999,
        match_num_str="TEST999",
        match_num_date="20231231",
        match_week="周五",
        match_date="2023-12-31",
        match_time="20:00",
        business_date="20231231",
        tax_date_no="20231231",
        league_id=2,
        home_team_id=1,
        home_team_code="HTEST",
        home_team_all_name="测试主队",
        home_team_abb_name="测试主",
        home_team_abb_en_name="HTEST",
        home_rank="1",
        away_team_id=2,
        away_team_code="ATEST",
        away_team_all_name="测试客队",
        away_team_abb_name="测试客",
        away_team_abb_en_name="ATEST",
        away_rank="2",
        base_home_team_id=1,
        base_away_team_id=2,
        match_name="测试比赛",
        group_name="测试组",
        line_num="1",
        betting_single=1,
        betting_all_up=1,
        remark="测试记录",
        status=0
    )
    
    # 添加记录
    session.add(test_match)
    session.commit()
    print("成功添加测试记录")
    
    # 关闭会话
    session.close()
    
except Exception as e:
    print(f"添加记录失败: {str(e)}")
    import traceback
    traceback.print_exc()
    # 回滚事务
    session.rollback()
    session.close()

# 测试4: 再次查询验证记录是否添加成功
print("\n测试4: 再次查询验证记录是否添加成功")
try:
    # 创建一个新的会话
    session = localdb.session
    
    # 使用ORM查询
    test_match = session.query(TczqMatch).filter(TczqMatch.match_id == 999999).first()
    
    if test_match:
        print(f"找到测试记录: 比赛ID: {test_match.match_id}, 比赛名称: {test_match.match_name}")
    else:
        print("没有找到测试记录")
        
    # 关闭会话
    session.close()
    
except Exception as e:
    print(f"验证查询失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")