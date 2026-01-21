# -*- coding: utf-8 -*-
"""
体彩足球赛果数据导入测试脚本
用于验证tczq_models.py中的赛果和赔率历史模型，并测试将result.json数据导入到数据库
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from database.tczq_models import (
    TczqMatch, TczqResult, TczqMatchResult, TczqOddsHistory,
    TczqOddsHistoryCrs, TczqOddsHistoryHhad, TczqOddsHistoryTtg,
    TczqOddsHistoryHad, TczqOddsHistoryHafu, TczqOddsSingle
)

def get_db_session():
    """
    获取数据库会话
    """
    db_config = config['local']
    engine = create_engine(
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    Session = sessionmaker(bind=engine)
    return Session()

def import_result_from_json(json_file_path):
    """
    从JSON文件导入赛果数据到数据库
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"成功读取JSON文件: {json_file_path}")
        print(f"比赛ID: {data.get('oddsHistory', {}).get('matchId', '未知')}")
        
        # 获取数据库会话
        session = get_db_session()
        
        # 获取比赛ID
        match_id = data.get('oddsHistory', {}).get('matchId')
        if not match_id:
            print("错误: 无法获取比赛ID")
            return False
        
        # 检查比赛是否存在
        match = session.query(TczqMatch).filter_by(match_id=match_id).first()
        if not match:
            print(f"警告: 比赛ID {match_id} 不存在于tczq_match表中，将创建新记录")
            
            # 创建比赛主表记录（如果不存在）
            odds_history = data.get('oddsHistory', {})
            match = TczqMatch(
                match_id=match_id,
                league_id=odds_history.get('leagueId'),
                league_all_name=odds_history.get('leagueAllName'),
                league_abb_name=odds_history.get('leagueAbbName'),
                home_team_id=odds_history.get('homeTeamId'),
                home_team_all_name=odds_history.get('homeTeamAllName'),
                home_team_abb_name=odds_history.get('homeTeamAbbName'),
                away_team_id=odds_history.get('awayTeamId'),
                away_team_all_name=odds_history.get('awayTeamAllName'),
                away_team_abb_name=odds_history.get('awayTeamAbbName')
            )
            session.add(match)
            session.flush()  # 获取自动生成的ID
        
        print("导入赛果数据...")
        
        # 创建或更新比赛赛果记录
        result = session.query(TczqResult).filter_by(match_id=match_id).first()
        if not result:
            result = TczqResult(
                match_id=match_id
            )
            session.add(result)
        
        # 更新赛果记录
        result.is_cancel = data.get('isCancel')
        result.full_score = data.get('sectionsNo999')
        result.all_home_team = data.get('oddsHistory', {}).get('homeTeamAllName')
        result.all_away_team = data.get('oddsHistory', {}).get('awayTeamAllName')
        result.home_team = data.get('oddsHistory', {}).get('homeTeamAbbName')
        result.away_team = data.get('oddsHistory', {}).get('awayTeamAbbName')
        result.league_id = data.get('oddsHistory', {}).get('leagueId')
        
        session.flush()  # 获取自动生成的ID
        
        # 处理matchResultList
        print("导入玩法结果数据...")
        match_result_list = data.get('matchResultList', [])
        
        # 先删除原有记录
        session.query(TczqMatchResult).filter_by(result_id=result.id).delete()
        
        for item in match_result_list:
            match_result = TczqMatchResult(
                result_id=result.id,
                code=item.get('code'),
                combination=item.get('combination'),
                combination_desc=item.get('combinationDesc'),
                goal_line=item.get('goalLine'),
                line_status=item.get('lineStatus'),
                match_id=item.get('matchId'),
                odds=item.get('odds'),
                odds_goal_line=item.get('oddsGoalLine'),
                odds_type=item.get('oddsType'),
                pool_id=item.get('poolId'),
                pool_totals=item.get('poolTotals'),
                refund_status=item.get('refundStatus')
            )
            session.add(match_result)
        
        # 处理oddsHistory
        print("导入赔率历史数据...")
        odds_history_data = data.get('oddsHistory', {})
        
        # 创建或更新赔率历史记录
        odds_history = session.query(TczqOddsHistory).filter_by(result_id=result.id).first()
        if not odds_history:
            odds_history = TczqOddsHistory(
                result_id=result.id
            )
            session.add(odds_history)
        
        # 更新赔率历史记录
        odds_history.match_id = odds_history_data.get('matchId')
        odds_history.home_team_id = odds_history_data.get('homeTeamId')
        odds_history.away_team_id = odds_history_data.get('awayTeamId')
        odds_history.home_team_all_name = odds_history_data.get('homeTeamAllName')
        odds_history.home_team_abb_name = odds_history_data.get('homeTeamAbbName')
        odds_history.away_team_all_name = odds_history_data.get('awayTeamAllName')
        odds_history.away_team_abb_name = odds_history_data.get('awayTeamAbbName')
        odds_history.league_id = odds_history_data.get('leagueId')
        
        session.flush()  # 获取自动生成的ID
        
        # 处理crsList
        print("导入总进球赔率历史...")
        crs_list = odds_history_data.get('crsList', [])
        
        # 先删除原有记录
        session.query(TczqOddsHistoryCrs).filter_by(odds_history_id=odds_history.id).delete()
        
        for item in crs_list:
            crs = TczqOddsHistoryCrs(
                odds_history_id=odds_history.id,
                
                # 赔率字段
                s00s00=float(item.get('s00s00')) if item.get('s00s00') and item.get('s00s00') != 'null' else None,
                s00s01=float(item.get('s00s01')) if item.get('s00s01') and item.get('s00s01') != 'null' else None,
                s00s02=float(item.get('s00s02')) if item.get('s00s02') and item.get('s00s02') != 'null' else None,
                s00s03=float(item.get('s00s03')) if item.get('s00s03') and item.get('s00s03') != 'null' else None,
                s00s04=float(item.get('s00s04')) if item.get('s00s04') and item.get('s00s04') != 'null' else None,
                s00s05=float(item.get('s00s05')) if item.get('s00s05') and item.get('s00s05') != 'null' else None,
                
                s01s00=float(item.get('s01s00')) if item.get('s01s00') and item.get('s01s00') != 'null' else None,
                s01s01=float(item.get('s01s01')) if item.get('s01s01') and item.get('s01s01') != 'null' else None,
                s01s02=float(item.get('s01s02')) if item.get('s01s02') and item.get('s01s02') != 'null' else None,
                s01s03=float(item.get('s01s03')) if item.get('s01s03') and item.get('s01s03') != 'null' else None,
                s01s04=float(item.get('s01s04')) if item.get('s01s04') and item.get('s01s04') != 'null' else None,
                s01s05=float(item.get('s01s05')) if item.get('s01s05') and item.get('s01s05') != 'null' else None,
                
                s02s00=float(item.get('s02s00')) if item.get('s02s00') and item.get('s02s00') != 'null' else None,
                s02s01=float(item.get('s02s01')) if item.get('s02s01') and item.get('s02s01') != 'null' else None,
                s02s02=float(item.get('s02s02')) if item.get('s02s02') and item.get('s02s02') != 'null' else None,
                s02s03=float(item.get('s02s03')) if item.get('s02s03') and item.get('s02s03') != 'null' else None,
                s02s04=float(item.get('s02s04')) if item.get('s02s04') and item.get('s02s04') != 'null' else None,
                s02s05=float(item.get('s02s05')) if item.get('s02s05') and item.get('s02s05') != 'null' else None,
                
                s03s00=float(item.get('s03s00')) if item.get('s03s00') and item.get('s03s00') != 'null' else None,
                s03s01=float(item.get('s03s01')) if item.get('s03s01') and item.get('s03s01') != 'null' else None,
                s03s02=float(item.get('s03s02')) if item.get('s03s02') and item.get('s03s02') != 'null' else None,
                s03s03=float(item.get('s03s03')) if item.get('s03s03') and item.get('s03s03') != 'null' else None,
                
                s04s00=float(item.get('s04s00')) if item.get('s04s00') and item.get('s04s00') != 'null' else None,
                s04s01=float(item.get('s04s01')) if item.get('s04s01') and item.get('s04s01') != 'null' else None,
                s04s02=float(item.get('s04s02')) if item.get('s04s02') and item.get('s04s02') != 'null' else None,
                
                s05s00=float(item.get('s05s00')) if item.get('s05s00') and item.get('s05s00') != 'null' else None,
                s05s01=float(item.get('s05s01')) if item.get('s05s01') and item.get('s05s01') != 'null' else None,
                s05s02=float(item.get('s05s02')) if item.get('s05s02') and item.get('s05s02') != 'null' else None,
                
                s_1sh=float(item.get('s-1sh')) if item.get('s-1sh') and item.get('s-1sh') != 'null' else None,
                s_1sd=float(item.get('s-1sd')) if item.get('s-1sd') and item.get('s-1sd') != 'null' else None,
                s_1sa=float(item.get('s-1sa')) if item.get('s-1sa') and item.get('s-1sa') != 'null' else None,
                
                # 赔率变化
                s00s00f=int(item.get('s00s00f')) if item.get('s00s00f') and item.get('s00s00f') != 'null' else None,
                s00s01f=int(item.get('s00s01f')) if item.get('s00s01f') and item.get('s00s01f') != 'null' else None,
                s00s02f=int(item.get('s00s02f')) if item.get('s00s02f') and item.get('s00s02f') != 'null' else None,
                s00s03f=int(item.get('s00s03f')) if item.get('s00s03f') and item.get('s00s03f') != 'null' else None,
                s00s04f=int(item.get('s00s04f')) if item.get('s00s04f') and item.get('s00s04f') != 'null' else None,
                s00s05f=int(item.get('s00s05f')) if item.get('s00s05f') and item.get('s00s05f') != 'null' else None,
                
                s01s00f=int(item.get('s01s00f')) if item.get('s01s00f') and item.get('s01s00f') != 'null' else None,
                s01s01f=int(item.get('s01s01f')) if item.get('s01s01f') and item.get('s01s01f') != 'null' else None,
                s01s02f=int(item.get('s01s02f')) if item.get('s01s02f') and item.get('s01s02f') != 'null' else None,
                s01s03f=int(item.get('s01s03f')) if item.get('s01s03f') and item.get('s01s03f') != 'null' else None,
                s01s04f=int(item.get('s01s04f')) if item.get('s01s04f') and item.get('s01s04f') != 'null' else None,
                s01s05f=int(item.get('s01s05f')) if item.get('s01s05f') and item.get('s01s05f') != 'null' else None,
                
                s02s00f=int(item.get('s02s00f')) if item.get('s02s00f') and item.get('s02s00f') != 'null' else None,
                s02s01f=int(item.get('s02s01f')) if item.get('s02s01f') and item.get('s02s01f') != 'null' else None,
                s02s02f=int(item.get('s02s02f')) if item.get('s02s02f') and item.get('s02s02f') != 'null' else None,
                s02s03f=int(item.get('s02s03f')) if item.get('s02s03f') and item.get('s02s03f') != 'null' else None,
                s02s04f=int(item.get('s02s04f')) if item.get('s02s04f') and item.get('s02s04f') != 'null' else None,
                s02s05f=int(item.get('s02s05f')) if item.get('s02s05f') and item.get('s02s05f') != 'null' else None,
                
                s03s00f=int(item.get('s03s00f')) if item.get('s03s00f') and item.get('s03s00f') != 'null' else None,
                s03s01f=int(item.get('s03s01f')) if item.get('s03s01f') and item.get('s03s01f') != 'null' else None,
                s03s02f=int(item.get('s03s02f')) if item.get('s03s02f') and item.get('s03s02f') != 'null' else None,
                s03s03f=int(item.get('s03s03f')) if item.get('s03s03f') and item.get('s03s03f') != 'null' else None,
                
                s04s00f=int(item.get('s04s00f')) if item.get('s04s00f') and item.get('s04s00f') != 'null' else None,
                s04s01f=int(item.get('s04s01f')) if item.get('s04s01f') and item.get('s04s01f') != 'null' else None,
                s04s02f=int(item.get('s04s02f')) if item.get('s04s02f') and item.get('s04s02f') != 'null' else None,
                
                s05s00f=int(item.get('s05s00f')) if item.get('s05s00f') and item.get('s05s00f') != 'null' else None,
                s05s01f=int(item.get('s05s01f')) if item.get('s05s01f') and item.get('s05s01f') != 'null' else None,
                s05s02f=int(item.get('s05s02f')) if item.get('s05s02f') and item.get('s05s02f') != 'null' else None,
                
                s_1shf=int(item.get('s-1shf')) if item.get('s-1shf') and item.get('s-1shf') != 'null' else None,
                s_1sdf=int(item.get('s-1sdf')) if item.get('s-1sdf') and item.get('s-1sdf') != 'null' else None,
                s_1saf=int(item.get('s-1saf')) if item.get('s-1saf') and item.get('s-1saf') != 'null' else None,
                
                goal_line=item.get('goalLine'),
                update_date=item.get('updateDate'),
                update_time=item.get('updateTime')
            )
            session.add(crs)
        
        # 处理hhadList
        print("导入让球胜平负赔率历史...")
        hhad_list = odds_history_data.get('hhadList', [])
        
        # 先删除原有记录
        session.query(TczqOddsHistoryHhad).filter_by(odds_history_id=odds_history.id).delete()
        
        for item in hhad_list:
            hhad = TczqOddsHistoryHhad(
                odds_history_id=odds_history.id,
                h=float(item.get('h')) if item.get('h') and item.get('h') != 'null' else None,
                d=float(item.get('d')) if item.get('d') and item.get('d') != 'null' else None,
                a=float(item.get('a')) if item.get('a') and item.get('a') != 'null' else None,
                hf=int(item.get('hf')) if item.get('hf') and item.get('hf') != 'null' else None,
                df=int(item.get('df')) if item.get('df') and item.get('df') != 'null' else None,
                af=int(item.get('af')) if item.get('af') and item.get('af') != 'null' else None,
                goal_line=item.get('goalLine'),
                update_date=item.get('updateDate'),
                update_time=item.get('updateTime')
            )
            session.add(hhad)
        
        # 处理ttgList
        print("导入总进球数赔率历史...")
        ttg_list = odds_history_data.get('ttgList', [])
        
        # 先删除原有记录
        session.query(TczqOddsHistoryTtg).filter_by(odds_history_id=odds_history.id).delete()
        
        for item in ttg_list:
            ttg = TczqOddsHistoryTtg(
                odds_history_id=odds_history.id,
                s0=float(item.get('s0')) if item.get('s0') and item.get('s0') != 'null' else None,
                s1=float(item.get('s1')) if item.get('s1') and item.get('s1') != 'null' else None,
                s2=float(item.get('s2')) if item.get('s2') and item.get('s2') != 'null' else None,
                s3=float(item.get('s3')) if item.get('s3') and item.get('s3') != 'null' else None,
                s4=float(item.get('s4')) if item.get('s4') and item.get('s4') != 'null' else None,
                s5=float(item.get('s5')) if item.get('s5') and item.get('s5') != 'null' else None,
                s6=float(item.get('s6')) if item.get('s6') and item.get('s6') != 'null' else None,
                s7=float(item.get('s7')) if item.get('s7') and item.get('s7') != 'null' else None,
                s0f=int(item.get('s0f')) if item.get('s0f') and item.get('s0f') != 'null' else None,
                s1f=int(item.get('s1f')) if item.get('s1f') and item.get('s1f') != 'null' else None,
                s2f=int(item.get('s2f')) if item.get('s2f') and item.get('s2f') != 'null' else None,
                s3f=int(item.get('s3f')) if item.get('s3f') and item.get('s3f') != 'null' else None,
                s4f=int(item.get('s4f')) if item.get('s4f') and item.get('s4f') != 'null' else None,
                s5f=int(item.get('s5f')) if item.get('s5f') and item.get('s5f') != 'null' else None,
                s6f=int(item.get('s6f')) if item.get('s6f') and item.get('s6f') != 'null' else None,
                s7f=int(item.get('s7f')) if item.get('s7f') and item.get('s7f') != 'null' else None,
                goal_line=item.get('goalLine'),
                update_date=item.get('updateDate'),
                update_time=item.get('updateTime')
            )
            session.add(ttg)
        
        # 处理hadList
        print("导入胜平负赔率历史...")
        had_list = odds_history_data.get('hadList', [])
        
        # 先删除原有记录
        session.query(TczqOddsHistoryHad).filter_by(odds_history_id=odds_history.id).delete()
        
        for item in had_list:
            had = TczqOddsHistoryHad(
                odds_history_id=odds_history.id,
                h=float(item.get('h')) if item.get('h') and item.get('h') != 'null' else None,
                d=float(item.get('d')) if item.get('d') and item.get('d') != 'null' else None,
                a=float(item.get('a')) if item.get('a') and item.get('a') != 'null' else None,
                hf=int(item.get('hf')) if item.get('hf') and item.get('hf') != 'null' else None,
                df=int(item.get('df')) if item.get('df') and item.get('df') != 'null' else None,
                af=int(item.get('af')) if item.get('af') and item.get('af') != 'null' else None,
                goal_line=item.get('goalLine'),
                update_date=item.get('updateDate'),
                update_time=item.get('updateTime')
            )
            session.add(had)
        
        # 处理hafuList
        print("导入半全场赔率历史...")
        hafu_list = odds_history_data.get('hafuList', [])
        
        # 先删除原有记录
        session.query(TczqOddsHistoryHafu).filter_by(odds_history_id=odds_history.id).delete()
        
        for item in hafu_list:
            hafu = TczqOddsHistoryHafu(
                odds_history_id=odds_history.id,
                hh=float(item.get('hh')) if item.get('hh') and item.get('hh') != 'null' else None,
                hd=float(item.get('hd')) if item.get('hd') and item.get('hd') != 'null' else None,
                ha=float(item.get('ha')) if item.get('ha') and item.get('ha') != 'null' else None,
                dh=float(item.get('dh')) if item.get('dh') and item.get('dh') != 'null' else None,
                dd=float(item.get('dd')) if item.get('dd') and item.get('dd') != 'null' else None,
                da=float(item.get('da')) if item.get('da') and item.get('da') != 'null' else None,
                ah=float(item.get('ah')) if item.get('ah') and item.get('ah') != 'null' else None,
                ad=float(item.get('ad')) if item.get('ad') and item.get('ad') != 'null' else None,
                aa=float(item.get('aa')) if item.get('aa') and item.get('aa') != 'null' else None,
                hhf=int(item.get('hhf')) if item.get('hhf') and item.get('hhf') != 'null' else None,
                hdf=int(item.get('hdf')) if item.get('hdf') and item.get('hdf') != 'null' else None,
                haf=int(item.get('haf')) if item.get('haf') and item.get('haf') != 'null' else None,
                dhf=int(item.get('dhf')) if item.get('dhf') and item.get('dhf') != 'null' else None,
                ddf=int(item.get('ddf')) if item.get('ddf') and item.get('ddf') != 'null' else None,
                daf=int(item.get('daf')) if item.get('daf') and item.get('daf') != 'null' else None,
                ahf=int(item.get('ahf')) if item.get('ahf') and item.get('ahf') != 'null' else None,
                adf=int(item.get('adf')) if item.get('adf') and item.get('adf') != 'null' else None,
                aaf=int(item.get('aaf')) if item.get('aaf') and item.get('aaf') != 'null' else None,
                goal_line=item.get('goalLine'),
                update_date=item.get('updateDate'),
                update_time=item.get('updateTime')
            )
            session.add(hafu)
        
        # 处理singleList
        print("导入单场投注信息...")
        single_list = odds_history_data.get('singleList', [])
        
        # 先删除原有记录
        session.query(TczqOddsSingle).filter_by(odds_history_id=odds_history.id).delete()
        
        for item in single_list:
            single = TczqOddsSingle(
                odds_history_id=odds_history.id,
                single=int(item.get('single')) if item.get('single') and item.get('single') != 'null' else None,
                pool_code=item.get('poolCode')
            )
            session.add(single)
        
        # 提交事务
        session.commit()
        print("\n赛果数据导入成功!")
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 体彩足球赛果数据导入测试脚本 ===")
    
    # 默认使用doc目录下的result.json文件
    json_file = "E:\\my_prog\\zqgetdata\\doc\\result.json"
    
    # 如果提供了命令行参数，则使用指定的文件
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"错误: 文件 {json_file} 不存在")
        sys.exit(1)
    
    # 执行导入
    success = import_result_from_json(json_file)
    
    if success:
        print("测试通过!")
        sys.exit(0)
    else:
        print("测试失败!")
        sys.exit(1)