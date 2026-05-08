# -*- coding: utf-8 -*-
"""
自动获取TCBK赛果并生成修复SQL
"""
import sys
sys.path.insert(0, 'get_data')

from app.common.req_sporttery_api import SportteryAPI
import json

# 服务器上的比赛列表
matches_from_server = [
  {"match_id": 2039391}, {"match_id": 2039392}, {"match_id": 2039393}, {"match_id": 2039394}, {"match_id": 2039395},
  {"match_id": 2039396}, {"match_id": 2039397}, {"match_id": 2039398}, {"match_id": 2039399}, {"match_id": 2039400},
  {"match_id": 2039425}, {"match_id": 2039426}, {"match_id": 2039427}, {"match_id": 2039428}, {"match_id": 2039429},
  {"match_id": 2039430}, {"match_id": 2039431}, {"match_id": 2039432}, {"match_id": 2039433}, {"match_id": 2039434},
  {"match_id": 2039435}, {"match_id": 2039436}, {"match_id": 2039442}, {"match_id": 2039443}, {"match_id": 2039444},
  {"match_id": 2039445}, {"match_id": 2039446}, {"match_id": 2039518}, {"match_id": 2039519}, {"match_id": 2039520},
  {"match_id": 2039521}, {"match_id": 2039522}, {"match_id": 2039523}, {"match_id": 2039524}, {"match_id": 2039525},
  {"match_id": 2039526}, {"match_id": 2039527}, {"match_id": 2039528}, {"match_id": 2039529}, {"match_id": 2039530},
  {"match_id": 2039531}, {"match_id": 2039532}, {"match_id": 2039533}, {"match_id": 2039534}, {"match_id": 2039535}
]

# 调用API获取赛果
api = SportteryAPI()
results = api.get_basketball_match_results('2026-04-26', '2026-05-04')

print(f"从API获取到 {len(results)} 条赛果数据\n")

# 建立matchId索引
api_by_id = {r['matchId']: r for r in results}

# 生成SQL
insert_sqls = []
update_sqls = []
success_count = 0
fail_count = 0

for match in matches_from_server:
    match_id = match['match_id']
    api_result = api_by_id.get(match_id)
    
    if not api_result:
        fail_count += 1
        continue
    
    home_score = api_result.get('homeScore')
    away_score = api_result.get('awayScore')
    
    if home_score is None or away_score is None:
        fail_count += 1
        continue
    
    # 生成INSERT语句（使用ON DUPLICATE KEY UPDATE避免重复）
    insert_sql = f"INSERT INTO tcbk_result (match_id, home_score, away_score, status, created_at, updated_at) VALUES ({match_id}, {home_score}, {away_score}, {api_result.get('status', 2)}, NOW(), NOW()) ON DUPLICATE KEY UPDATE home_score=VALUES(home_score), away_score=VALUES(away_score), status=VALUES(status), updated_at=NOW();"
    insert_sqls.append(insert_sql)
    
    # 生成UPDATE语句
    update_sql = f"UPDATE tcbk_match SET match_status = 8 WHERE match_id = {match_id};"
    update_sqls.append(update_sql)
    
    success_count += 1

print(f"处理完成 - 成功: {success_count}, 失败: {fail_count}\n")
print("="*80)
print("-- 执行以下SQL更新服务器数据库")
print("="*80)

for sql in insert_sqls:
    print(sql)

for sql in update_sqls:
    print(sql)
