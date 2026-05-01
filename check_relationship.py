import pymysql

conn = pymysql.connect(
    host='115.190.125.52',
    port=3306,
    user='soccer_data',
    password='pety93033',
    database='soccer_data'
)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 检查TCZQ的关联关系
cursor.execute("""
    SELECT m.id as match_db_id, m.match_id as match_api_id, r.match_id as result_match_id 
    FROM tczq_match m 
    LEFT JOIN tczq_match_result r ON m.id = r.match_id 
    WHERE m.status = 2 
    LIMIT 5
""")
rows = cursor.fetchall()
print('TCZQ Match-Result relationship check:')
for r in rows:
    print(f"  DB ID: {r['match_db_id']}, API ID: {r['match_api_id']}, Result match_id: {r['result_match_id']}")

# 检查正确的关联方式
cursor.execute("""
    SELECT COUNT(*) as count 
    FROM tczq_match m 
    INNER JOIN tczq_match_result r ON m.match_id = r.match_id 
    WHERE m.status = 2
""")
correct_count = cursor.fetchone()['count']
print(f"\nCorrect join (m.match_id = r.match_id): {correct_count} matches have results")

cursor.execute("""
    SELECT COUNT(*) as count 
    FROM tczq_match m 
    INNER JOIN tczq_match_result r ON m.id = r.match_id 
    WHERE m.status = 2
""")
wrong_count = cursor.fetchone()['count']
print(f"Wrong join (m.id = r.match_id): {wrong_count} matches have results")

conn.close()
