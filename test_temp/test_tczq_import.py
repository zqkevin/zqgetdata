# -*- coding: utf-8 -*-
"""
体彩足球数据导入测试脚本
用于验证tczq_models.py中的模型，并测试将alldata.json数据导入到数据库
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from database.tczq_models import TczqMatch, TczqCrs, TczqHad, TczqHhad, TczqHafu, TczqTtg

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

def import_from_json(json_file_path):
    """
    从JSON文件导入数据到数据库
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"成功读取JSON文件: {json_file_path}")
        
        # 处理单个比赛对象或比赛对象数组
        if isinstance(data, list):
            match_list = data
            print(f"数据包含 {len(match_list)} 个比赛记录")
        else:
            match_list = [data]
            print("数据包含 1 个比赛记录")
        
        # 获取数据库会话
        session = get_db_session()
        
        for i, match_data in enumerate(match_list):
            try:
                print(f"\n导入第 {i+1} 个比赛记录: {match_data.get('matchNumStr', '未知')}")
                
                # 创建比赛主表记录
                match = TczqMatch(
                    match_id=match_data.get('matchId'),
                    match_num=match_data.get('matchNum'),
                    match_num_str=match_data.get('matchNumStr'),
                    match_num_date=match_data.get('matchNumDate'),
                    match_week=match_data.get('matchWeek'),
                    match_date=match_data.get('matchDate'),
                    match_time=match_data.get('matchTime'),
                    business_date=match_data.get('businessDate'),
                    tax_date_no=match_data.get('taxDateNo'),
                    
                    league_id=match_data.get('leagueId'),
                    league_code=match_data.get('leagueCode'),
                    league_all_name=match_data.get('leagueAllName'),
                    league_abb_name=match_data.get('leagueAbbName'),
                    
                    home_team_id=match_data.get('homeTeamId'),
                    home_team_code=match_data.get('homeTeamCode'),
                    home_team_all_name=match_data.get('homeTeamAllName'),
                    home_team_abb_name=match_data.get('homeTeamAbbName'),
                    home_team_abb_en_name=match_data.get('homeTeamAbbEnName'),
                    home_rank=match_data.get('homeRank'),
                    
                    away_team_id=match_data.get('awayTeamId'),
                    away_team_code=match_data.get('awayTeamCode'),
                    away_team_all_name=match_data.get('awayTeamAllName'),
                    away_team_abb_name=match_data.get('awayTeamAbbName'),
                    away_team_abb_en_name=match_data.get('awayTeamAbbEnName'),
                    away_rank=match_data.get('awayRank'),
                    
                    base_home_team_id=match_data.get('baseHomeTeamId'),
                    base_away_team_id=match_data.get('baseAwayTeamId'),
                    
                    match_name=match_data.get('matchName'),
                    group_name=match_data.get('groupName'),
                    line_num=match_data.get('lineNum'),
                    
                    match_status=match_data.get('matchStatus'),
                    sell_status=match_data.get('sellStatus'),
                    is_hot=match_data.get('isHot'),
                    is_hide=match_data.get('isHide'),
                    betting_single=match_data.get('bettingSingle'),
                    betting_all_up=match_data.get('bettingAllUp'),
                    
                    back_color=match_data.get('backColor'),
                    remark=match_data.get('remark')
                )
                
                # 处理总进球赔率 (crs)
                if 'crs' in match_data:
                    crs_data = match_data['crs']
                    match.crs = TczqCrs(
                        match_id=match_data.get('matchId'),
                        s00s00=float(crs_data.get('s00s00')) if crs_data.get('s00s00') else None,
                        s00s01=float(crs_data.get('s00s01')) if crs_data.get('s00s01') else None,
                        s00s02=float(crs_data.get('s00s02')) if crs_data.get('s00s02') else None,
                        s00s03=float(crs_data.get('s00s03')) if crs_data.get('s00s03') else None,
                        s00s04=float(crs_data.get('s00s04')) if crs_data.get('s00s04') else None,
                        s00s05=float(crs_data.get('s00s05')) if crs_data.get('s00s05') else None,
                        
                        s01s00=float(crs_data.get('s01s00')) if crs_data.get('s01s00') else None,
                        s01s01=float(crs_data.get('s01s01')) if crs_data.get('s01s01') else None,
                        s01s02=float(crs_data.get('s01s02')) if crs_data.get('s01s02') else None,
                        s01s03=float(crs_data.get('s01s03')) if crs_data.get('s01s03') else None,
                        s01s04=float(crs_data.get('s01s04')) if crs_data.get('s01s04') else None,
                        s01s05=float(crs_data.get('s01s05')) if crs_data.get('s01s05') else None,
                        
                        s02s00=float(crs_data.get('s02s00')) if crs_data.get('s02s00') else None,
                        s02s01=float(crs_data.get('s02s01')) if crs_data.get('s02s01') else None,
                        s02s02=float(crs_data.get('s02s02')) if crs_data.get('s02s02') else None,
                        s02s03=float(crs_data.get('s02s03')) if crs_data.get('s02s03') else None,
                        s02s04=float(crs_data.get('s02s04')) if crs_data.get('s02s04') else None,
                        s02s05=float(crs_data.get('s02s05')) if crs_data.get('s02s05') else None,
                        
                        s03s00=float(crs_data.get('s03s00')) if crs_data.get('s03s00') else None,
                        s03s01=float(crs_data.get('s03s01')) if crs_data.get('s03s01') else None,
                        s03s02=float(crs_data.get('s03s02')) if crs_data.get('s03s02') else None,
                        s03s03=float(crs_data.get('s03s03')) if crs_data.get('s03s03') else None,
                        
                        s04s00=float(crs_data.get('s04s00')) if crs_data.get('s04s00') else None,
                        s04s01=float(crs_data.get('s04s01')) if crs_data.get('s04s01') else None,
                        s04s02=float(crs_data.get('s04s02')) if crs_data.get('s04s02') else None,
                        
                        s05s00=float(crs_data.get('s05s00')) if crs_data.get('s05s00') else None,
                        s05s01=float(crs_data.get('s05s01')) if crs_data.get('s05s01') else None,
                        s05s02=float(crs_data.get('s05s02')) if crs_data.get('s05s02') else None,
                        
                        s1sh=float(crs_data.get('s1sh')) if crs_data.get('s1sh') else None,
                        s1sd=float(crs_data.get('s1sd')) if crs_data.get('s1sd') else None,
                        s1sa=float(crs_data.get('s1sa')) if crs_data.get('s1sa') else None,
                        
                        update_date=crs_data.get('updateDate'),
                        update_time=crs_data.get('updateTime')
                    )
                
                # 处理胜平负赔率 (had)
                if 'had' in match_data:
                    had_data = match_data['had']
                    match.had = TczqHad(
                        match_id=match_data.get('matchId'),
                        h=float(had_data.get('h')) if had_data.get('h') else None,
                        d=float(had_data.get('d')) if had_data.get('d') else None,
                        a=float(had_data.get('a')) if had_data.get('a') else None,
                        hf=int(had_data.get('hf')) if had_data.get('hf') else None,
                        df=int(had_data.get('df')) if had_data.get('df') else None,
                        af=int(had_data.get('af')) if had_data.get('af') else None,
                        update_date=had_data.get('updateDate'),
                        update_time=had_data.get('updateTime')
                    )
                
                # 处理让球胜平负赔率 (hhad)
                if 'hhad' in match_data:
                    hhad_data = match_data['hhad']
                    match.hhad = TczqHhad(
                        match_id=match_data.get('matchId'),
                        goal_line=hhad_data.get('goalLine'),
                        goal_line_value=float(hhad_data.get('goalLineValue')) if hhad_data.get('goalLineValue') else None,
                        h=float(hhad_data.get('h')) if hhad_data.get('h') else None,
                        d=float(hhad_data.get('d')) if hhad_data.get('d') else None,
                        a=float(hhad_data.get('a')) if hhad_data.get('a') else None,
                        hf=int(hhad_data.get('hf')) if hhad_data.get('hf') else None,
                        df=int(hhad_data.get('df')) if hhad_data.get('df') else None,
                        af=int(hhad_data.get('af')) if hhad_data.get('af') else None,
                        update_date=hhad_data.get('updateDate'),
                        update_time=hhad_data.get('updateTime')
                    )
                
                # 处理半全场赔率 (hafu)
                if 'hafu' in match_data:
                    hafu_data = match_data['hafu']
                    match.hafu = TczqHafu(
                        match_id=match_data.get('matchId'),
                        hh=float(hafu_data.get('hh')) if hafu_data.get('hh') else None,
                        hd=float(hafu_data.get('hd')) if hafu_data.get('hd') else None,
                        ha=float(hafu_data.get('ha')) if hafu_data.get('ha') else None,
                        
                        dh=float(hafu_data.get('dh')) if hafu_data.get('dh') else None,
                        dd=float(hafu_data.get('dd')) if hafu_data.get('dd') else None,
                        da=float(hafu_data.get('da')) if hafu_data.get('da') else None,
                        
                        ah=float(hafu_data.get('ah')) if hafu_data.get('ah') else None,
                        ad=float(hafu_data.get('ad')) if hafu_data.get('ad') else None,
                        aa=float(hafu_data.get('aa')) if hafu_data.get('aa') else None,
                        
                        hhf=int(hafu_data.get('hhf')) if hafu_data.get('hhf') else None,
                        hdf=int(hafu_data.get('hdf')) if hafu_data.get('hdf') else None,
                        ahf=int(hafu_data.get('ahf')) if hafu_data.get('ahf') else None,
                        
                        dhf=int(hafu_data.get('dhf')) if hafu_data.get('dhf') else None,
                        ddf=int(hafu_data.get('ddf')) if hafu_data.get('ddf') else None,
                        daf=int(hafu_data.get('daf')) if hafu_data.get('daf') else None,
                        
                        update_date=hafu_data.get('updateDate'),
                        update_time=hafu_data.get('updateTime')
                    )
                
                # 处理总进球数赔率 (ttg)
                if 'ttg' in match_data:
                    ttg_data = match_data['ttg']
                    match.ttg = TczqTtg(
                        match_id=match_data.get('matchId'),
                        s0=float(ttg_data.get('s0')) if ttg_data.get('s0') else None,
                        s1=float(ttg_data.get('s1')) if ttg_data.get('s1') else None,
                        s2=float(ttg_data.get('s2')) if ttg_data.get('s2') else None,
                        s3=float(ttg_data.get('s3')) if ttg_data.get('s3') else None,
                        s4=float(ttg_data.get('s4')) if ttg_data.get('s4') else None,
                        s5=float(ttg_data.get('s5')) if ttg_data.get('s5') else None,
                        s6=float(ttg_data.get('s6')) if ttg_data.get('s6') else None,
                        s7=float(ttg_data.get('s7')) if ttg_data.get('s7') else None,
                        
                        s0f=int(ttg_data.get('s0f')) if ttg_data.get('s0f') else None,
                        s1f=int(ttg_data.get('s1f')) if ttg_data.get('s1f') else None,
                        s2f=int(ttg_data.get('s2f')) if ttg_data.get('s2f') else None,
                        s3f=int(ttg_data.get('s3f')) if ttg_data.get('s3f') else None,
                        s4f=int(ttg_data.get('s4f')) if ttg_data.get('s4f') else None,
                        s5f=int(ttg_data.get('s5f')) if ttg_data.get('s5f') else None,
                        s6f=int(ttg_data.get('s6f')) if ttg_data.get('s6f') else None,
                        s7f=int(ttg_data.get('s7f')) if ttg_data.get('s7f') else None,
                        
                        update_date=ttg_data.get('updateDate'),
                        update_time=ttg_data.get('updateTime')
                    )
                
                # 添加到会话并提交
                session.add(match)
                session.commit()
                print(f"  比赛记录导入成功: {match_data.get('matchNumStr')} - {match_data.get('homeTeamAbbName')} VS {match_data.get('awayTeamAbbName')}")
                
            except Exception as e:
                print(f"  导入失败: {e}")
                session.rollback()
                continue
        
        # 关闭会话
        session.close()
        print(f"\n数据导入完成，成功导入 {len(data)} 个比赛记录")
        
    except Exception as e:
        print(f"导入数据失败: {e}")
        return False

def test_single_match_import():
    """
    测试导入单个比赛记录
    """
    try:
        # 读取单个比赛的JSON数据
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc', 'alldata.json')
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果是列表，取第一个元素；否则直接使用
        if isinstance(data, list):
            match_data = data[0]
        else:
            match_data = data
        
        print("测试单个比赛记录导入...")
        print(f"比赛信息: {match_data.get('matchNumStr')} - {match_data.get('homeTeamAbbName')} VS {match_data.get('awayTeamAbbName')}")
        
        # 获取数据库会话
        session = get_db_session()
        
        # 创建比赛主表记录
        match = TczqMatch(
            match_id=match_data.get('matchId'),
            match_num=match_data.get('matchNum'),
            match_num_str=match_data.get('matchNumStr'),
            match_num_date=match_data.get('matchNumDate'),
            match_week=match_data.get('matchWeek'),
            match_date=match_data.get('matchDate'),
            match_time=match_data.get('matchTime'),
            business_date=match_data.get('businessDate'),
            tax_date_no=match_data.get('taxDateNo'),
            
            league_id=match_data.get('leagueId'),
            league_code=match_data.get('leagueCode'),
            league_all_name=match_data.get('leagueAllName'),
            league_abb_name=match_data.get('leagueAbbName'),
            
            home_team_id=match_data.get('homeTeamId'),
            home_team_code=match_data.get('homeTeamCode'),
            home_team_all_name=match_data.get('homeTeamAllName'),
            home_team_abb_name=match_data.get('homeTeamAbbName'),
            home_team_abb_en_name=match_data.get('homeTeamAbbEnName'),
            home_rank=match_data.get('homeRank'),
            
            away_team_id=match_data.get('awayTeamId'),
            away_team_code=match_data.get('awayTeamCode'),
            away_team_all_name=match_data.get('awayTeamAllName'),
            away_team_abb_name=match_data.get('awayTeamAbbName'),
            away_team_abb_en_name=match_data.get('awayTeamAbbEnName'),
            away_rank=match_data.get('awayRank'),
            
            base_home_team_id=match_data.get('baseHomeTeamId'),
            base_away_team_id=match_data.get('baseAwayTeamId'),
            
            match_name=match_data.get('matchName'),
            group_name=match_data.get('groupName'),
            line_num=match_data.get('lineNum'),
            
            match_status=match_data.get('matchStatus'),
            sell_status=match_data.get('sellStatus'),
            is_hot=match_data.get('isHot'),
            is_hide=match_data.get('isHide'),
            betting_single=match_data.get('bettingSingle'),
            betting_all_up=match_data.get('bettingAllUp'),
            
            back_color=match_data.get('backColor'),
            remark=match_data.get('remark')
        )
        
        # 处理总进球赔率 (crs)
        if 'crs' in match_data:
            crs_data = match_data['crs']
            match.crs = TczqCrs(
                match_id=match_data.get('matchId'),
                s00s00=float(crs_data.get('s00s00')) if crs_data.get('s00s00') else None,
                s00s01=float(crs_data.get('s00s01')) if crs_data.get('s00s01') else None,
                s00s02=float(crs_data.get('s00s02')) if crs_data.get('s00s02') else None,
                s00s03=float(crs_data.get('s00s03')) if crs_data.get('s00s03') else None,
                s00s04=float(crs_data.get('s00s04')) if crs_data.get('s00s04') else None,
                s00s05=float(crs_data.get('s00s05')) if crs_data.get('s00s05') else None,
                update_date=crs_data.get('updateDate'),
                update_time=crs_data.get('updateTime')
            )
        
        # 处理胜平负赔率 (had)
        if 'had' in match_data:
            had_data = match_data['had']
            match.had = TczqHad(
                match_id=match_data.get('matchId'),
                h=float(had_data.get('h')) if had_data.get('h') else None,
                d=float(had_data.get('d')) if had_data.get('d') else None,
                a=float(had_data.get('a')) if had_data.get('a') else None,
                update_date=had_data.get('updateDate'),
                update_time=had_data.get('updateTime')
            )
        
        # 处理让球胜平负赔率 (hhad)
        if 'hhad' in match_data:
            hhad_data = match_data['hhad']
            match.hhad = TczqHhad(
                match_id=match_data.get('matchId'),
                goal_line=hhad_data.get('goalLine'),
                goal_line_value=float(hhad_data.get('goalLineValue')) if hhad_data.get('goalLineValue') else None,
                h=float(hhad_data.get('h')) if hhad_data.get('h') else None,
                d=float(hhad_data.get('d')) if hhad_data.get('d') else None,
                a=float(hhad_data.get('a')) if hhad_data.get('a') else None,
                update_date=hhad_data.get('updateDate'),
                update_time=hhad_data.get('updateTime')
            )
        
        # 处理半全场赔率 (hafu)
        if 'hafu' in match_data:
            hafu_data = match_data['hafu']
            match.hafu = TczqHafu(
                match_id=match_data.get('matchId'),
                hh=float(hafu_data.get('hh')) if hafu_data.get('hh') else None,
                hd=float(hafu_data.get('hd')) if hafu_data.get('hd') else None,
                ha=float(hafu_data.get('ha')) if hafu_data.get('ha') else None,
                dh=float(hafu_data.get('dh')) if hafu_data.get('dh') else None,
                dd=float(hafu_data.get('dd')) if hafu_data.get('dd') else None,
                da=float(hafu_data.get('da')) if hafu_data.get('da') else None,
                ah=float(hafu_data.get('ah')) if hafu_data.get('ah') else None,
                ad=float(hafu_data.get('ad')) if hafu_data.get('ad') else None,
                aa=float(hafu_data.get('aa')) if hafu_data.get('aa') else None,
                update_date=hafu_data.get('updateDate'),
                update_time=hafu_data.get('updateTime')
            )
        
        # 处理总进球数赔率 (ttg)
        if 'ttg' in match_data:
            ttg_data = match_data['ttg']
            match.ttg = TczqTtg(
                match_id=match_data.get('matchId'),
                s0=float(ttg_data.get('s0')) if ttg_data.get('s0') else None,
                s1=float(ttg_data.get('s1')) if ttg_data.get('s1') else None,
                s2=float(ttg_data.get('s2')) if ttg_data.get('s2') else None,
                s3=float(ttg_data.get('s3')) if ttg_data.get('s3') else None,
                s4=float(ttg_data.get('s4')) if ttg_data.get('s4') else None,
                s5=float(ttg_data.get('s5')) if ttg_data.get('s5') else None,
                s6=float(ttg_data.get('s6')) if ttg_data.get('s6') else None,
                s7=float(ttg_data.get('s7')) if ttg_data.get('s7') else None,
                update_date=ttg_data.get('updateDate'),
                update_time=ttg_data.get('updateTime')
            )
        
        # 添加到会话并提交
        session.add(match)
        session.commit()
        print("单个比赛记录导入成功!")
        
        # 关闭会话
        session.close()
        
        return True
        
    except Exception as e:
        print(f"单个比赛记录导入失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 体彩足球数据导入测试 ===")
    
    # 测试单个比赛记录导入
    if test_single_match_import():
        print("\n测试通过! 体彩足球数据库模型工作正常")
    else:
        print("\n测试失败! 请检查错误信息")