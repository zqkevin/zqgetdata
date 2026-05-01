import pymysql
from datetime import datetime

conn = pymysql.connect(
    host='115.190.125.52',
    port=3306,
    user='soccer_data',
    password='pety93033',
    database='soccer_data'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

print("检查TCZQ status=9且有赛果的比赛的时间线:")
print("=" * 120)

cur.execute("""
    SELECT m.match_id, ht.team_full_name as home, at.team_full_name as away, 
           m.match_time, m.status, m.updated_at as match_updated,
           r.updated_at as result_updated,
           TIMESTAMPDIFF(HOUR, m.match_time, m.updated_at) as hours_to_status_update,
           TIMESTAMPDIFF(HOUR, m.match_time, r.updated_at) as hours_to_result
    FROM tczq_match m 
    LEFT JOIN team ht ON m.home_team_id = ht.id
    LEFT JOIN team at ON m.away_team_id = at.id
    INNER JOIN tczq_match_result r ON m.match_id = r.match_id 
    WHERE m.status = 9
    ORDER BY m.match_time
    LIMIT 10
""")

rows = cur.fetchall()
for r in rows:
    print(f"\nMatch ID: {r['match_id']}")
    print(f"  比赛: {r['home']} vs {r['away']}")
    print(f"  比赛时间: {r['match_time']}")
    print(f"  状态更新时间: {r['match_updated']} (赛后{r['hours_to_status_update']}小时)")
    print(f"  赛果更新时间: {r['result_updated']} (赛后{r['hours_to_result']}小时)")
    
    if r['match_updated'] and r['result_updated']:
        if r['match_updated'] > r['result_updated']:
            print(f"  ⚠️ 状态更新晚于赛果更新 - 说明先保存赛果，后被标记为status=9")
        else:
            print(f"  ✓ 赛果更新晚于状态更新 - 说明先标记status=9，后获取赛果")

print("\n" + "=" * 120)
print(f"\n总共检查了{len(rows)}场比赛")

conn.close()
