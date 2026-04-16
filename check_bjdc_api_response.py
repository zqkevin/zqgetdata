# -*- coding: utf-8 -*-
"""
查看北京单场赛果 API 返回的原始数据
特别关注比赛取消时的数据结构
"""
import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.common.req_sporttery_api import SportteryAPI
from app.database import localdb, BjdcMatch


def check_api_response():
    """检查 API 返回的原始数据"""
    
    api = SportteryAPI()
    
    # 获取最近几天的赛果数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print("=" * 80)
    print(f"查询时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print("=" * 80)
    
    # 调用 API
    results = api.get_football_match_result(
        match_begin_date=start_date.strftime('%Y-%m-%d'),
        match_end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if not results:
        print("\n❌ API 返回空数据")
        return
    
    print(f"\n✅ 共获取 {len(results)} 条赛果记录\n")
    
    # 查找包含 'N/A' 或 '取消' 的记录
    abnormal_results = []
    normal_results = []
    
    for result in results:
        home_score = result.get('homeScore')
        away_score = result.get('awayScore')
        result_status = result.get('resultStatus', '')
        match_result_status = result.get('matchResultStatus', '')
        
        # 检查是否为异常状态
        is_abnormal = (
            home_score == 'N/A' or 
            away_score == 'N/A' or 
            home_score == '取消' or 
            away_score == '取消' or
            result_status in ['取消', '延期', '腰斩']
        )
        
        if is_abnormal:
            abnormal_results.append(result)
        else:
            normal_results.append(result)
    
    # 输出统计信息
    print(f"正常比赛: {len(normal_results)} 场")
    print(f"异常比赛: {len(abnormal_results)} 场")
    print()
    
    # 显示异常比赛的详细信息
    if abnormal_results:
        print("=" * 80)
        print("异常比赛详情:")
        print("=" * 80)
        
        for i, result in enumerate(abnormal_results, 1):
            print(f"\n--- 异常比赛 #{i} ---")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 检查数据库中的对应记录
            match_id = result.get('matchId')
            if match_id:
                try:
                    match = localdb.query(BjdcMatch).filter_by(match_id=int(match_id)).first()
                    if match:
                        print(f"\n📊 数据库中的比赛信息:")
                        print(f"  match_id: {match.match_id}")
                        print(f"  status: {match.status}")
                        print(f"  remark: {match.remark}")
                        home_name = match.home_team.team_full_name if match.home_team else '未知'
                        away_name = match.away_team.team_full_name if match.away_team else '未知'
                        print(f"  比赛: {home_name} vs {away_name}")
                        print(f"  开赛时间: {match.match_time}")
                except Exception as e:
                    print(f"  ⚠️ 查询数据库失败: {e}")
    
    # 显示一个正常比赛的示例（用于对比）
    if normal_results:
        print("\n" + "=" * 80)
        print("正常比赛示例（第一条）:")
        print("=" * 80)
        print(json.dumps(normal_results[0], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        check_api_response()
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
