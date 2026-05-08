# -*- coding: utf-8 -*-
"""
处理TCBK异常比赛赛果修复
从API获取赛果，生成INSERT和UPDATE SQL语句
"""
import json

# 服务器上的比赛列表（从MCP查询得到）
matches_from_server = [
  {"match_id": 2039391, "match_date": "2026-04-26", "home_team_all_name": "曼雷萨", "away_team_all_name": "布尔戈斯", "match_status": 0},
  {"match_id": 2039392, "match_date": "2026-04-27", "home_team_all_name": "法兰克福", "away_team_all_name": "柏林阿尔巴", "match_status": 0},
  {"match_id": 2039393, "match_date": "2026-04-27", "home_team_all_name": "多伦多猛龙", "away_team_all_name": "克利夫兰骑士", "match_status": 0},
  {"match_id": 2039394, "match_date": "2026-04-27", "home_team_all_name": "波特兰开拓者", "away_team_all_name": "圣安东尼奥马刺", "match_status": 0},
  {"match_id": 2039395, "match_date": "2026-04-27", "home_team_all_name": "休斯敦火箭", "away_team_all_name": "洛杉矶湖人", "match_status": 0},
  {"match_id": 2039396, "match_date": "2026-04-28", "home_team_all_name": "开姆尼茨", "away_team_all_name": "班堡", "match_status": 0},
  {"match_id": 2039397, "match_date": "2026-04-28", "home_team_all_name": "拜仁慕尼黑", "away_team_all_name": "罗斯托克海狼", "match_status": 0},
  {"match_id": 2039398, "match_date": "2026-04-28", "home_team_all_name": "奥兰多魔术", "away_team_all_name": "底特律活塞", "match_status": 0},
  {"match_id": 2039399, "match_date": "2026-04-28", "home_team_all_name": "菲尼克斯太阳", "away_team_all_name": "俄克拉荷马城雷霆", "match_status": 0},
  {"match_id": 2039400, "match_date": "2026-04-28", "home_team_all_name": "丹佛掘金", "away_team_all_name": "明尼苏达森林狼", "match_status": 0},
  {"match_id": 2039425, "match_date": "2026-04-29", "home_team_all_name": "奥林匹亚科斯", "away_team_all_name": "摩纳哥", "match_status": 0},
  {"match_id": 2039428, "match_date": "2026-04-29", "home_team_all_name": "圣安东尼奥马刺", "away_team_all_name": "波特兰开拓者", "match_status": 0},
  {"match_id": 2039427, "match_date": "2026-04-29", "home_team_all_name": "纽约尼克斯", "away_team_all_name": "亚特兰大老鹰", "match_status": 0},
  {"match_id": 2039426, "match_date": "2026-04-29", "home_team_all_name": "巴伦西亚", "away_team_all_name": "帕纳辛纳科斯", "match_status": 0},
  {"match_id": 2039429, "match_date": "2026-04-30", "home_team_all_name": "马拉加", "away_team_all_name": "大加那利", "match_status": 0},
  {"match_id": 2039430, "match_date": "2026-04-30", "home_team_all_name": "底特律活塞", "away_team_all_name": "奥兰多魔术", "match_status": 0},
  {"match_id": 2039431, "match_date": "2026-04-30", "home_team_all_name": "克利夫兰骑士", "away_team_all_name": "多伦多猛龙", "match_status": 0},
  {"match_id": 2039432, "match_date": "2026-04-30", "home_team_all_name": "洛杉矶湖人", "away_team_all_name": "休斯敦火箭", "match_status": 0},
  {"match_id": 2039442, "match_date": "2026-05-01", "home_team_all_name": "法兰克福", "away_team_all_name": "波恩", "match_status": 0},
  {"match_id": 2039436, "match_date": "2026-05-01", "home_team_all_name": "明尼苏达森林狼", "away_team_all_name": "丹佛掘金", "match_status": 0},
  {"match_id": 2039434, "match_date": "2026-05-01", "home_team_all_name": "巴伦西亚", "away_team_all_name": "帕纳辛纳科斯", "match_status": 0},
  {"match_id": 2039433, "match_date": "2026-05-01", "home_team_all_name": "奥林匹亚科斯", "away_team_all_name": "摩纳哥", "match_status": 0},
  {"match_id": 2039435, "match_date": "2026-05-01", "home_team_all_name": "亚特兰大老鹰", "away_team_all_name": "纽约尼克斯", "match_status": 0},
  {"match_id": 2039443, "match_date": "2026-05-02", "home_team_all_name": "拜仁慕尼黑", "away_team_all_name": "柏林阿尔巴", "match_status": 9},
  {"match_id": 2039444, "match_date": "2026-05-02", "home_team_all_name": "奥兰多魔术", "away_team_all_name": "底特律活塞", "match_status": 9},
  {"match_id": 2039445, "match_date": "2026-05-02", "home_team_all_name": "多伦多猛龙", "away_team_all_name": "克利夫兰骑士", "match_status": 9},
  {"match_id": 2039446, "match_date": "2026-05-02", "home_team_all_name": "休斯敦火箭", "away_team_all_name": "洛杉矶湖人", "match_status": 9},
  {"match_id": 2039523, "match_date": "2026-05-03", "home_team_all_name": "不伦瑞克雄狮", "away_team_all_name": "路德维希堡", "match_status": 9},
  {"match_id": 2039530, "match_date": "2026-05-03", "home_team_all_name": "拜仁慕尼黑", "away_team_all_name": "费希塔", "match_status": 9},
  {"match_id": 2039529, "match_date": "2026-05-03", "home_team_all_name": "柏林阿尔巴", "away_team_all_name": "开姆尼茨", "match_status": 9},
  {"match_id": 2039528, "match_date": "2026-05-03", "home_team_all_name": "毕尔巴鄂", "away_team_all_name": "格拉纳达", "match_status": 9},
  {"match_id": 2039527, "match_date": "2026-05-03", "home_team_all_name": "皇家马德里", "away_team_all_name": "穆尔西亚天主大学", "match_status": 9},
  {"match_id": 2039526, "match_date": "2026-05-03", "home_team_all_name": "曼雷萨", "away_team_all_name": "巴伦西亚", "match_status": 9},
  {"match_id": 2039525, "match_date": "2026-05-03", "home_team_all_name": "布尔戈斯", "away_team_all_name": "列伊达", "match_status": 9},
  {"match_id": 2039524, "match_date": "2026-05-03", "home_team_all_name": "特里尔角斗士", "away_team_all_name": "奥尔登堡", "match_status": 9},
  {"match_id": 2039522, "match_date": "2026-05-03", "home_team_all_name": "特内里费", "away_team_all_name": "安道尔BC", "match_status": 9},
  {"match_id": 2039521, "match_date": "2026-05-03", "home_team_all_name": "罗斯托克海狼", "away_team_all_name": "耶拿科学城", "match_status": 9},
  {"match_id": 2039520, "match_date": "2026-05-03", "home_team_all_name": "维尔茨堡", "away_team_all_name": "乌尔姆", "match_status": 9},
  {"match_id": 2039519, "match_date": "2026-05-03", "home_team_all_name": "赫罗纳", "away_team_all_name": "萨拉戈萨", "match_status": 9},
  {"match_id": 2039518, "match_date": "2026-05-03", "home_team_all_name": "约文图特", "away_team_all_name": "马拉加", "match_status": 9},
  {"match_id": 2039531, "match_date": "2026-05-04", "home_team_all_name": "巴斯克尼亚", "away_team_all_name": "卢戈", "match_status": 9},
  {"match_id": 2039532, "match_date": "2026-05-04", "home_team_all_name": "班堡", "away_team_all_name": "汉堡塔楼", "match_status": 9},
  {"match_id": 2039533, "match_date": "2026-05-04", "home_team_all_name": "巴塞罗那", "away_team_all_name": "大加那利", "match_status": 9},
  {"match_id": 2039534, "match_date": "2026-05-04", "home_team_all_name": "底特律活塞", "away_team_all_name": "奥兰多魔术", "match_status": 9},
  {"match_id": 2039535, "match_date": "2026-05-04", "home_team_all_name": "克利夫兰骑士", "away_team_all_name": "多伦多猛龙", "match_status": 9}
]

# API返回的赛果数据（从终端输出复制）
api_results = [
    {"matchId": 2039535, "matchDate": "2026-05-04", "allHomeTeam": "克利夫兰骑士", "allAwayTeam": "多伦多猛龙", "homeScore": 102, "awayScore": 114, "status": 2},
    {"matchId": 2039534, "matchDate": "2026-05-04", "allHomeTeam": "底特律活塞", "allAwayTeam": "奥兰多魔术", "homeScore": 94, "awayScore": 116, "status": 2},
    {"matchId": 2039533, "matchDate": "2026-05-04", "allHomeTeam": "巴塞罗那", "allAwayTeam": "大加那利", "homeScore": 69, "awayScore": 91, "status": 2}
    # ... 这里需要完整的61条数据
]

# 建立matchId索引
api_by_id = {r['matchId']: r for r in api_results}

# 生成SQL
insert_sqls = []
update_sqls = []
success_count = 0
fail_count = 0

for match in matches_from_server:
    match_id = match['match_id']
    api_result = api_by_id.get(match_id)
    
    if not api_result:
        print(f"❌ 未找到match_id={match_id}的赛果")
        fail_count += 1
        continue
    
    home_score = api_result.get('homeScore')
    away_score = api_result.get('awayScore')
    
    if home_score is None or away_score is None:
        print(f"❌ match_id={match_id} 缺少比分数据")
        fail_count += 1
        continue
    
    # 生成INSERT语句
    insert_sql = f"INSERT INTO tcbk_result (match_id, home_score, away_score, status, created_at, updated_at) VALUES ({match_id}, {home_score}, {away_score}, {api_result.get('status', 2)}, NOW(), NOW()) ON DUPLICATE KEY UPDATE home_score={home_score}, away_score={away_score}, status={api_result.get('status', 2)}, updated_at=NOW();"
    insert_sqls.append(insert_sql)
    
    # 生成UPDATE语句
    update_sql = f"UPDATE tcbk_match SET match_status = 8 WHERE match_id = {match_id};"
    update_sqls.append(update_sql)
    
    success_count += 1
    print(f"✅ {match['home_team_all_name']} {home_score}:{away_score} {match['away_team_all_name']}")

print(f"\n{'='*60}")
print(f"处理完成 - 成功: {success_count}, 失败: {fail_count}")
print(f"{'='*60}\n")

print("-- INSERT语句（tcbk_result表）")
for sql in insert_sqls:
    print(sql)

print("\n-- UPDATE语句（tcbk_match表）")
for sql in update_sqls:
    print(sql)
