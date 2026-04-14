# -*- coding: utf-8 -*-
"""
查询数据库中的足球赔率和赔率历史记录并打印出来
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.database import localdb, TczqMatch, TczqScoreOdds, TczqHandicapSpfOdds, TczqSpfOdds, TczqHalfTimeFullTimeOdds, TczqTotalGoalOdds, TczqOddsHistory, TczqOddsHistoryHad, TczqOddsHistoryHhad, TczqOddsHistoryHafu, TczqOddsHistoryTtg, TczqOddsHistoryCrs

def query_football_odds():
    """
    查询足球赔率和赔率历史记录并打印
    """
    print("=== 查询足球赔率和赔率历史记录开始 ===")
    
    try:
        # 查询所有足球比赛记录
        matches = localdb.query(TczqMatch).all()
        
        print(f"\n总共查询到 {len(matches)} 条足球比赛记录：")
        print("=" * 120)
        
        for match in matches:
            # 获取联赛名称
            league_name = match.league.league_name if match.league else "未知联赛"
            
            print(f"\n[比赛信息]")
            print(f"比赛ID: {match.match_id}")
            print(f"比赛编号: {match.match_num_str}")
            print(f"比赛时间: {match.match_date} {match.match_time}")
            print(f"联赛: {league_name}")
            print(f"对阵双方: {match.home_team_abb_name} vs {match.away_team_abb_name}")
            print("-" * 120)
            
            # 查询当前赔率
            print("[当前赔率信息]")
            
            # 胜平负赔率
            if match.had and match.had.h > 0 and match.had.d > 0 and match.had.a > 0:
                print(f"胜平负赔率 (HAD): 主胜-{match.had.h}, 平局-{match.had.d}, 客胜-{match.had.a}")
            else:
                print(f"胜平负赔率 (HAD): 暂无数据或数据不完整")
            
            # 让球胜平负赔率
            if match.hhad and match.hhad.h > 0 and match.hhad.d > 0 and match.hhad.a > 0:
                print(f"让球胜平负赔率 (HHAD): 主胜-{match.hhad.h}, 平局-{match.hhad.d}, 客胜-{match.hhad.a}, 让球数-{match.hhad.goal_line}")
            else:
                print(f"让球胜平负赔率 (HHAD): 暂无数据或数据不完整")
            
            # 总进球数赔率
            if match.ttg:
                print(f"总进球数赔率 (TTG): 0球-{match.ttg.s0}, 1球-{match.ttg.s1}, 2球-{match.ttg.s2}, 3球-{match.ttg.s3}, 4球-{match.ttg.s4}, 5球-{match.ttg.s5}, 6球-{match.ttg.s6}, 7+球-{match.ttg.s7}")
            else:
                print(f"总进球数赔率 (TTG): 暂无数据")
            
            # 半全场赔率
            if match.hafu:
                print(f"半全场赔率 (HAFU): 主胜主胜-{match.hafu.hh}, 主胜平局-{match.hafu.hd}, 主胜客胜-{match.hafu.ha}")
                print(f"                平局主胜-{match.hafu.dh}, 平局平局-{match.hafu.dd}, 平局客胜-{match.hafu.da}")
                print(f"                客胜主胜-{match.hafu.ah}, 客胜平局-{match.hafu.ad}, 客胜客胜-{match.hafu.aa}")
            else:
                print(f"半全场赔率 (HAFU): 暂无数据")
            
            # 总进球赔率
            if match.crs:
                print(f"总进球赔率 (CRS): 部分数据略...")
            else:
                print(f"总进球赔率 (CRS): 暂无数据")
            
            print("-" * 120)
            
            # 查询赔率历史
            odds_histories = localdb.query(TczqOddsHistory).filter_by(match_id=match.match_id).all()
            
            if odds_histories:
                print(f"[赔率历史记录 ({len(odds_histories)} 条)]")
                
                for i, odds_history in enumerate(odds_histories, 1):
                    print(f"\n  [历史记录 {i}]")
                    print(f"  更新时间: {odds_history.updated_at}")
                    
                    # 查询具体赔率历史
                    had_history = localdb.query(TczqOddsHistoryHad).filter_by(odds_history_id=odds_history.id).first()
                    if had_history:
                        print(f"  胜平负历史: 主胜-{had_history.h}, 平局-{had_history.d}, 客胜-{had_history.a}, 更新时间-{had_history.update_time}")
                    
                    hhad_history = localdb.query(TczqOddsHistoryHhad).filter_by(odds_history_id=odds_history.id).first()
                    if hhad_history:
                        print(f"  让球胜平负历史: 主胜-{hhad_history.h}, 平局-{hhad_history.d}, 客胜-{hhad_history.a}, 让球数-{hhad_history.goal_line}, 更新时间-{hhad_history.update_time}")
                    
                    hafu_history = localdb.query(TczqOddsHistoryHafu).filter_by(odds_history_id=odds_history.id).first()
                    if hafu_history:
                        print(f"  半全场历史: 部分数据略... 更新时间-{hafu_history.update_time}")
                    
                    ttg_history = localdb.query(TczqOddsHistoryTtg).filter_by(odds_history_id=odds_history.id).first()
                    if ttg_history:
                        print(f"  总进球数历史: 0球-{ttg_history.s0}, 1球-{ttg_history.s1}, 2球-{ttg_history.s2}, 3球-{ttg_history.s3}, 更新时间-{ttg_history.update_time}")
                    
                    crs_history = localdb.query(TczqOddsHistoryCrs).filter_by(odds_history_id=odds_history.id).first()
                    if crs_history:
                        print(f"  总进球历史: 部分数据略... 更新时间-{crs_history.update_time}")
            else:
                print(f"[赔率历史记录] 暂无数据")
            
            print("=" * 120)
            
    except Exception as e:
        print(f"\n查询足球赔率和赔率历史失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        localdb.close()
    
    print("=== 查询足球赔率和赔率历史记录结束 ===")

def query_specific_match_odds(match_id):
    """
    查询指定比赛的赔率和赔率历史记录
    
    Args:
        match_id: 比赛ID
    """
    print(f"=== 查询比赛ID: {match_id} 的赔率和赔率历史记录开始 ===")
    
    try:
        # 查询指定比赛
        match = localdb.query(TczqMatch).filter_by(match_id=match_id).first()
        
        if not match:
            print(f"未找到比赛ID为 {match_id} 的比赛记录")
            return
        
        # 获取联赛名称
        league_name = match.league.league_name if match.league else "未知联赛"
        
        print(f"\n[比赛信息]")
        print(f"比赛ID: {match.match_id}")
        print(f"比赛编号: {match.match_num_str}")
        print(f"比赛时间: {match.match_date} {match.match_time}")
        print(f"联赛: {league_name}")
        print(f"对阵双方: {match.home_team_abb_name} vs {match.away_team_abb_name}")
        print("-" * 120)
        
        # 查询当前赔率
        print("[当前赔率信息]")
        
        # 胜平负赔率
        if match.had and match.had.h > 0 and match.had.d > 0 and match.had.a > 0:
            print(f"胜平负赔率 (HAD): 主胜-{match.had.h}, 平局-{match.had.d}, 客胜-{match.had.a}")
        else:
            print(f"胜平负赔率 (HAD): 暂无数据或数据不完整")
        
        # 让球胜平负赔率
        if match.hhad and match.hhad.h > 0 and match.hhad.d > 0 and match.hhad.a > 0:
            print(f"让球胜平负赔率 (HHAD): 主胜-{match.hhad.h}, 平局-{match.hhad.d}, 客胜-{match.hhad.a}, 让球数-{match.hhad.goal_line}")
        else:
            print(f"让球胜平负赔率 (HHAD): 暂无数据或数据不完整")
        
        # 总进球数赔率
        if match.ttg:
            print(f"总进球数赔率 (TTG): 0球-{match.ttg.s0}, 1球-{match.ttg.s1}, 2球-{match.ttg.s2}, 3球-{match.ttg.s3}, 4球-{match.ttg.s4}, 5球-{match.ttg.s5}, 6球-{match.ttg.s6}, 7+球-{match.ttg.s7}")
        else:
            print(f"总进球数赔率 (TTG): 暂无数据")
        
        # 半全场赔率
        if match.hafu:
            print(f"半全场赔率 (HAFU): 主胜主胜-{match.hafu.hh}, 主胜平局-{match.hafu.hd}, 主胜客胜-{match.hafu.ha}")
            print(f"                平局主胜-{match.hafu.dh}, 平局平局-{match.hafu.dd}, 平局客胜-{match.hafu.da}")
            print(f"                客胜主胜-{match.hafu.ah}, 客胜平局-{match.hafu.ad}, 客胜客胜-{match.hafu.aa}")
        else:
            print(f"半全场赔率 (HAFU): 暂无数据")
        
        # 总进球赔率
        if match.crs:
            print(f"总进球赔率 (CRS): 部分数据略...")
        else:
            print(f"总进球赔率 (CRS): 暂无数据")
        
        print("-" * 120)
        
        # 查询赔率历史
        odds_histories = localdb.query(TczqOddsHistory).filter_by(match_id=match.match_id).all()
        
        if odds_histories:
            print(f"[赔率历史记录 ({len(odds_histories)} 条)]")
            
            for i, odds_history in enumerate(odds_histories, 1):
                print(f"\n  [历史记录 {i}]")
                print(f"  更新时间: {odds_history.updated_at}")
                
                # 查询具体赔率历史
                had_history = localdb.query(TczqOddsHistoryHad).filter_by(odds_history_id=odds_history.id).first()
                if had_history:
                    print(f"  胜平负历史: 主胜-{had_history.h}, 平局-{had_history.d}, 客胜-{had_history.a}, 更新时间-{had_history.update_time}")
                
                hhad_history = localdb.query(TczqOddsHistoryHhad).filter_by(odds_history_id=odds_history.id).first()
                if hhad_history:
                    print(f"  让球胜平负历史: 主胜-{hhad_history.h}, 平局-{hhad_history.d}, 客胜-{hhad_history.a}, 让球数-{hhad_history.goal_line}, 更新时间-{hhad_history.update_time}")
                
                hafu_history = localdb.query(TczqOddsHistoryHafu).filter_by(odds_history_id=odds_history.id).first()
                if hafu_history:
                    print(f"  半全场历史: 部分数据略... 更新时间-{hafu_history.update_time}")
                
                ttg_history = localdb.query(TczqOddsHistoryTtg).filter_by(odds_history_id=odds_history.id).first()
                if ttg_history:
                    print(f"  总进球数历史: 0球-{ttg_history.s0}, 1球-{ttg_history.s1}, 2球-{ttg_history.s2}, 3球-{ttg_history.s3}, 更新时间-{ttg_history.update_time}")
                
                crs_history = localdb.query(TczqOddsHistoryCrs).filter_by(odds_history_id=odds_history.id).first()
                if crs_history:
                    print(f"  总进球历史: 部分数据略... 更新时间-{crs_history.update_time}")
        else:
            print(f"[赔率历史记录] 暂无数据")
        
        print("=" * 120)
        
    except Exception as e:
        print(f"\n查询指定比赛赔率和赔率历史失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        localdb.close()
    
    print(f"=== 查询比赛ID: {match_id} 的赔率和赔率历史记录结束 ===")

if __name__ == "__main__":
    from sqlalchemy import desc
    
    # 查询最新的10场比赛
    matches = localdb.query(TczqMatch).order_by(desc(TczqMatch.match_date), desc(TczqMatch.match_time)).limit(10).all()
    
    # 打印比赛和赔率信息
    for match in matches:
        print(f"\n比赛ID: {match.match_id}")
        # 获取联赛名称
        league_name = match.league.league_name if match.league else "未知联赛"
        print(f"联赛: {league_name}")
        print(f"比赛时间: {match.match_date} {match.match_time}")
        print(f"主队: {match.home_team_abb_name} VS 客队: {match.away_team_abb_name}")
        
        # 查询当前赔率
        # 胜平负赔率
        had = localdb.query(TczqHandicapSpfOdds).filter_by(match_id=match.match_id).first()
        if had and had.h > 0 and had.d > 0 and had.a > 0:
            print(f"胜平负赔率: 主胜-{had.h}, 平局-{had.d}, 客胜-{had.a}")
        else:
            print("胜平负赔率: 暂无数据或数据不完整")
        
        # 让球胜平负赔率
        hhad = localdb.query(TczqSpfOdds).filter_by(match_id=match.match_id).first()
        if hhad and hhad.h > 0 and hhad.d > 0 and hhad.a > 0:
            print(f"让球胜平负赔率: 让球-{hhad.goal_line}, 主胜-{hhad.h}, 平局-{hhad.d}, 客胜-{hhad.a}")
        else:
            print("让球胜平负赔率: 暂无数据或数据不完整")
        
        # 总进球数赔率
        ttg = localdb.query(TczqTotalGoalOdds).filter_by(match_id=match.match_id).first()
        if ttg:
            print(f"总进球数赔率: 0球-{ttg.s0}, 1球-{ttg.s1}, 2球-{ttg.s2}, 3球-{ttg.s3}, 4球-{ttg.s4}, 5球-{ttg.s5}, 6球-{ttg.s6}, 7+球-{ttg.s7}")
        else:
            print("总进球数赔率: 暂无数据")
        
        # 半全场赔率
        hafu = localdb.query(TczqHalfTimeFullTimeOdds).filter_by(match_id=match.match_id).first()
        if hafu:
            print(f"半全场赔率: 主胜主胜-{hafu.hh}, 主胜平局-{hafu.hd}, 主胜客胜-{hafu.ha}, 平局主胜-{hafu.dh}, 平局平局-{hafu.dd}, 平局客胜-{hafu.da}, 客胜主胜-{hafu.ah}, 客胜平局-{hafu.ad}, 客胜客胜-{hafu.aa}")
        else:
            print("半全场赔率: 暂无数据")
        
        # 查询赔率历史记录
        print(f"\n查询比赛 {match.match_id} 的赔率历史记录...")
        try:
            odds_histories = localdb.query(TczqOddsHistory).filter_by(match_id=match.match_id).order_by(desc(TczqOddsHistory.updated_at)).all()
            print(f"  查询到的赔率历史记录数量: {len(odds_histories)}")
            
            if odds_histories:
                print(f"  赔率历史记录数量: {len(odds_histories)}")
                # 打印最新的3条赔率历史记录
                for i, history in enumerate(odds_histories[:3]):
                    print(f"  历史记录 #{i+1} - 更新时间: {history.updated_at}, ID: {history.id}")
                    
                    # 查询对应的胜平负赔率历史
                    had_history = localdb.query(TczqOddsHistoryHad).filter_by(odds_history_id=history.id).first()
                    if had_history:
                        print(f"    胜平负历史赔率: 主胜-{had_history.h}, 平局-{had_history.d}, 客胜-{had_history.a}")
                    
                    # 查询对应的让球胜平负赔率历史
                    hhad_history = localdb.query(TczqOddsHistoryHhad).filter_by(odds_history_id=history.id).first()
                    if hhad_history:
                        print(f"    让球胜平负历史赔率: 让球-{hhad_history.goal_line}, 主胜-{hhad_history.h}, 平局-{hhad_history.d}, 客胜-{hhad_history.a}")
        except Exception as e:
            print(f"  查询赔率历史记录时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n共查询到 {len(matches)} 场比赛")
    # 关闭数据库连接
    localdb.close()