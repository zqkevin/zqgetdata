# -*- coding: utf-8 -*-
"""
检查远程服务器数据完整性和正常性
"""
import pymysql
from datetime import datetime, timedelta

def check_database():
    """检查数据库数据"""
    conn = pymysql.connect(
        host='115.190.125.52',
        port=3306,
        user='soccer_data',
        password='pety93033',
        database='soccer_data',
        charset='utf8mb4'
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("=" * 80)
    print("远程数据库数据完整性检查报告")
    print("=" * 80)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据库地址: 115.190.125.52:3306/soccer_data")
    print("=" * 80)
    
    # 1. 基础数据表检查
    print("\n【1】基础数据表")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) as count FROM league")
    league_count = cursor.fetchone()['count']
    print(f"联赛总数 (league): {league_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM team")
    team_count = cursor.fetchone()['count']
    print(f"球队总数 (team): {team_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM team_alias")
    alias_count = cursor.fetchone()['count']
    print(f"球队别名数 (team_alias): {alias_count}")
    
    # 2. TCZQ（体彩足球）数据检查
    print("\n【2】体彩足球 (TCZQ) 数据")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) as count FROM tczq_match")
    tczq_match_count = cursor.fetchone()['count']
    print(f"比赛总数 (tczq_match): {tczq_match_count}")
    
    cursor.execute("SELECT status, COUNT(*) as count FROM tczq_match GROUP BY status")
    status_rows = cursor.fetchall()
    print("  比赛状态分布:")
    for row in status_rows:
        status_map = {0: '未开赛', 1: '进行中', 2: '已结束', 3: '取消'}
        status_name = status_map.get(row['status'], f"未知({row['status']})")
        print(f"    {status_name}: {row['count']}")
    
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute(f"SELECT DATE(match_time) as match_date, COUNT(*) as count FROM tczq_match WHERE match_time >= '{seven_days_ago}' GROUP BY DATE(match_time) ORDER BY match_date")
    recent_matches = cursor.fetchall()
    print(f"  最近7天比赛数:")
    for row in recent_matches:
        print(f"    {row['match_date']}: {row['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM tczq_spf_odds")
    tczq_spf_count = cursor.fetchone()['count']
    print(f"胜平负赔率记录数 (tczq_spf_odds): {tczq_spf_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM tczq_handicap_spf_odds")
    tczq_handicap_count = cursor.fetchone()['count']
    print(f"让球胜平负赔率记录数 (tczq_handicap_spf_odds): {tczq_handicap_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM tczq_match_result")
    tczq_result_count = cursor.fetchone()['count']
    print(f"比赛结果记录数 (tczq_match_result): {tczq_result_count}")
    
    # 3. BJDC（北京单场）数据检查
    print("\n【3】北京单场 (BJDC) 数据")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) as count FROM bjdc_match")
    bjdc_match_count = cursor.fetchone()['count']
    print(f"比赛总数 (bjdc_match): {bjdc_match_count}")
    
    cursor.execute("SELECT status, COUNT(*) as count FROM bjdc_match GROUP BY status")
    bjdc_status_rows = cursor.fetchall()
    print("  比赛状态分布:")
    for row in bjdc_status_rows:
        status_map = {0: '未开赛', 1: '进行中', 2: '已结束', 3: '取消'}
        status_name = status_map.get(row['status'], f"未知({row['status']})")
        print(f"    {status_name}: {row['count']}")
    
    cursor.execute(f"SELECT DATE(match_time) as match_date, COUNT(*) as count FROM bjdc_match WHERE match_time >= '{seven_days_ago}' GROUP BY DATE(match_time) ORDER BY match_date")
    bjdc_recent = cursor.fetchall()
    print(f"  最近7天比赛数:")
    for row in bjdc_recent:
        print(f"    {row['match_date']}: {row['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM bjdc_spf_odds")
    bjdc_spf_count = cursor.fetchone()['count']
    print(f"胜平负赔率记录数 (bjdc_spf_odds): {bjdc_spf_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM bjdc_match_result")
    bjdc_result_count = cursor.fetchone()['count']
    print(f"比赛结果记录数 (bjdc_match_result): {bjdc_result_count}")
    
    # 4. TCBK（体彩篮球）数据检查
    print("\n【4】体彩篮球 (TCBK) 数据")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) as count FROM tcbk_match")
    tcbk_match_count = cursor.fetchone()['count']
    print(f"比赛总数 (tcbk_match): {tcbk_match_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM tcbk_spf")
    tcbk_spf_count = cursor.fetchone()['count']
    print(f"胜负赔率记录数 (tcbk_spf): {tcbk_spf_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM tcbk_match_result")
    tcbk_result_count = cursor.fetchone()['count']
    print(f"比赛结果记录数 (tcbk_match_result): {tcbk_result_count}")
    
    # 5. 数字彩票数据检查
    print("\n【5】数字彩票数据")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) as count FROM digital_lottery_types")
    lottery_type_count = cursor.fetchone()['count']
    print(f"彩票类型数 (digital_lottery_types): {lottery_type_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM digital_lottery_draws")
    lottery_draw_count = cursor.fetchone()['count']
    print(f"开奖记录数 (digital_lottery_draws): {lottery_draw_count}")
    
    # 6. 数据完整性检查
    print("\n【6】数据完整性检查")
    print("-" * 80)
    
    # 检查有比赛但没有结果的
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM tczq_match m 
        LEFT JOIN tczq_match_result r ON m.id = r.match_id 
        WHERE m.status = 2 AND r.id IS NULL
    """)
    missing_tczq_result = cursor.fetchone()['count']
    print(f"TCZQ已结束但缺少结果的比赛数: {missing_tczq_result}")
    
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM bjdc_match m 
        LEFT JOIN bjdc_match_result r ON m.id = r.match_id 
        WHERE m.status = 2 AND r.id IS NULL
    """)
    missing_bjdc_result = cursor.fetchone()['count']
    print(f"BJDC已结束但缺少结果的比赛数: {missing_bjdc_result}")
    
    # 检查最新数据的时间
    cursor.execute("SELECT MAX(match_time) as latest FROM tczq_match")
    latest_tczq = cursor.fetchone()['latest']
    print(f"\nTCZQ最新比赛时间: {latest_tczq}")
    
    cursor.execute("SELECT MAX(match_time) as latest FROM bjdc_match")
    latest_bjdc = cursor.fetchone()['latest']
    print(f"BJDC最新比赛时间: {latest_bjdc}")
    
    cursor.execute("SELECT MAX(created_at) as latest FROM tczq_spf_odds")
    latest_tczq_odds = cursor.fetchone()['latest']
    print(f"TCZQ最新赔率更新时间: {latest_tczq_odds}")
    
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_database()
