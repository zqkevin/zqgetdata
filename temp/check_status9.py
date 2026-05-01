import pymysql

conn = pymysql.connect(
    host='115.190.125.52',
    port=3306,
    user='soccer_data',
    password='pety93033',
    database='soccer_data'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

print("=" * 120)
print("检查 TCZQ status=9 的比赛")
print("=" * 120)

cur.execute("""
    SELECT m.match_id, ht.team_full_name as home_name, at.team_full_name as away_name, 
           m.match_time, m.remark, r.id as has_result 
    FROM tczq_match m 
    LEFT JOIN team ht ON m.home_team_id = ht.id
    LEFT JOIN team at ON m.away_team_id = at.id
    LEFT JOIN tczq_match_result r ON m.match_id = r.match_id 
    WHERE m.status = 9
    ORDER BY m.match_time
""")

rows = cur.fetchall()
print(f"\nTCZQ status=9: 共 {len(rows)} 场\n")

for r in rows:
    home = r['home_name'][:15] if r['home_name'] else ''
    away = r['away_name'][:15] if r['away_name'] else ''
    has_result = '✓有' if r['has_result'] else '✗无'
    remark = str(r['remark'])[:40] if r['remark'] else ''
    print(f"  {r['match_id']} | {home} vs {away} | {r['match_time']} | 赛果:{has_result} | {remark}")

print("\n" + "=" * 120)
print("检查 BJDC status=9 的比赛")
print("=" * 120)

cur.execute("""
    SELECT m.match_id, ht.team_full_name as home_name, at.team_full_name as away_name, 
           m.match_time, m.remark, r.id as has_result 
    FROM bjdc_match m 
    LEFT JOIN team ht ON m.home_team_id = ht.id
    LEFT JOIN team at ON m.away_team_id = at.id
    LEFT JOIN bjdc_match_result r ON m.match_id = r.match_id 
    WHERE m.status = 9
    ORDER BY m.match_time
""")

rows = cur.fetchall()
print(f"\nBJDC status=9: 共 {len(rows)} 场\n")

for r in rows:
    home = r['home_name'][:15] if r['home_name'] else ''
    away = r['away_name'][:15] if r['away_name'] else ''
    has_result = '✓有' if r['has_result'] else '✗无'
    remark = str(r['remark'])[:40] if r['remark'] else ''
    print(f"  {r['match_id']} | {home} vs {away} | {r['match_time']} | 赛果:{has_result} | {remark}")

print("\n" + "=" * 120)

conn.close()
