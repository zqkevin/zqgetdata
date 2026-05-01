import pymysql

conn = pymysql.connect(
    host='115.190.125.52',
    port=3306,
    user='soccer_data',
    password='pety93033',
    database='soccer_data'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# 检查TCZQ中没有赛果的status=9比赛
print("TCZQ status=9但没有赛果的比赛:")
cur.execute("""
    SELECT m.match_id, ht.team_full_name as home, at.team_full_name as away, 
           m.match_time, m.remark
    FROM tczq_match m 
    LEFT JOIN team ht ON m.home_team_id = ht.id
    LEFT JOIN team at ON m.away_team_id = at.id
    LEFT JOIN tczq_match_result r ON m.match_id = r.match_id 
    WHERE m.status = 9 AND r.id IS NULL
""")
rows = cur.fetchall()
for r in rows:
    print(f"  {r['match_id']} | {r['home']} vs {r['away']} | {r['match_time']} | remark: {r['remark']}")

print(f"\n共{len(rows)}场\n")

# 检查BJDC中没有赛果的status=9比赛
print("BJDC status=9但没有赛果的比赛:")
cur.execute("""
    SELECT m.match_id, ht.team_full_name as home, at.team_full_name as away, 
           m.match_time, m.remark
    FROM bjdc_match m 
    LEFT JOIN team ht ON m.home_team_id = ht.id
    LEFT JOIN team at ON m.away_team_id = at.id
    LEFT JOIN bjdc_match_result r ON m.match_id = r.match_id 
    WHERE m.status = 9 AND r.id IS NULL
""")
rows = cur.fetchall()
for r in rows:
    print(f"  {r['match_id']} | {r['home']} vs {r['away']} | {r['match_time']} | remark: {r['remark']}")

print(f"\n共{len(rows)}场")

conn.close()
