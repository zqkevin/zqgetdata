# -*- coding: utf-8 -*-
"""
临时脚本 - 导入JSON数据到数据库
"""
import sys
from pathlib import Path
import io

# 设置stdout编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from sqlalchemy import text
from app.database import SessionLocal, Area, Position, Venue, League, Team, Player, Coach, PlayerTeam, TeamCoach


def import_areas():
    """导入国家/地区数据"""
    print("\n" + "=" * 80)
    print("📊 导入国家/地区数据")
    print("=" * 80)
    
    data_dir = Path(__file__).parent.parent.parent / "data"
    file_path = data_dir / "countries.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        countries = json.load(f)
    
    print(f"📂 加载数据: {len(countries)} 个国家/地区")
    
    db = SessionLocal()
    try:
        # 临时禁用外键检查
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        insert_count = 0
        for country in countries:
            area_type = 'COUNTRY'
            if country['name_en'] in ['World', '世界']:
                area_type = 'WORLD'
            elif country['name_en'] in ['Asia', 'Europe', 'Africa', 'South America', 'N/C America', 'Oceania']:
                area_type = 'CONTINENT'
            
            area = Area(
                id=country['id'],
                name_en=country['name_en'],
                name_zh=country.get('name_zh'),
                code=country.get('code'),
                flag_url=country.get('flag'),
                parent_area_id=country.get('parent_area_id'),
                area_type=area_type
            )
            
            # 使用merge避免重复
            db.merge(area)
            insert_count += 1
        
        db.commit()
        # 恢复外键检查
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print(f"✅ 成功导入 {insert_count} 条记录")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
        raise
    finally:
        db.close()


def import_leagues():
    """导入联赛数据"""
    print("\n" + "=" * 80)
    print("📊 导入联赛数据")
    print("=" * 80)
    
    data_dir = Path(__file__).parent.parent.parent / "data"
    file_path = data_dir / "leagues.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        leagues = json.load(f)
    
    print(f"📂 加载数据: {len(leagues)} 个联赛")
    
    db = SessionLocal()
    try:
        # 临时禁用外键检查
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        insert_count = 0
        for league_data in leagues:
            current_season = league_data.get('current_season', {})
            
            league = League(
                id=league_data['id'],
                name_en_full=league_data.get('name_en_full', league_data.get('name_en')),
                name_en_short=league_data.get('name_en_short'),
                name_zh_full=league_data.get('name_zh_full'),
                name_zh_short=league_data.get('name_zh_short'),
                code=league_data.get('code'),
                type=league_data.get('type', 'LEAGUE'),
                emblem_url=league_data.get('emblem'),
                logo_url=league_data.get('emblem'),
                area_id=league_data.get('area_id'),
                current_season_start=datetime.strptime(current_season.get('start_date'), '%Y-%m-%d') if current_season.get('start_date') else None,
                current_season_end=datetime.strptime(current_season.get('end_date'), '%Y-%m-%d') if current_season.get('end_date') else None,
                current_matchday=current_season.get('current_matchday'),
                source_platform='FOOTBALL_DATA',
                source_id=str(league_data['id'])
            )
            
            db.merge(league)
            insert_count += 1
        
        db.commit()
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print(f"✅ 成功导入 {insert_count} 条记录")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
        raise
    finally:
        db.close()


def import_teams_and_players():
    """导入球队和球员数据"""
    print("\n" + "=" * 80)
    print("📊 导入球队和球员数据")
    print("=" * 80)
    
    data_dir = Path(__file__).parent.parent.parent / "data"
    file_path = data_dir / "teams_with_players.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
    
    print(f"📂 加载数据: {len(teams_data)} 支球队")
    
    db = SessionLocal()
    try:
        # 临时禁用外键检查
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        team_count = 0
        player_count = 0
        coach_count = 0
        
        # 第一步：收集所有教练
        all_coaches = {}
        for team_data in teams_data:
            coach_data = team_data.get('coach')
            if coach_data:
                all_coaches[coach_data['id']] = coach_data
        
        # 第二步：插入所有教练
        print(f"   📝 处理 {len(all_coaches)} 名教练...")
        for coach_id, coach_data in all_coaches.items():
            # 跳过没有名字的教练
            if not coach_data.get('name_en'):
                continue
            
            coach = Coach(
                id=coach_data['id'],
                name_en=coach_data.get('name_en'),
                name_zh=coach_data.get('name_zh'),
                nationality=coach_data.get('nationality')
            )
            db.merge(coach)
            coach_count += 1
        
        # 第三步：插入球队和球员
        for team_data in teams_data:
            # 插入球队
            team = Team(
                id=team_data['id'],
                name_en_full=team_data.get('name_en_full', team_data.get('name_en')),
                name_en_short=team_data.get('name_en_short'),
                name_zh_full=team_data.get('name_zh_full'),
                name_zh_short=team_data.get('name_zh_short'),
                short_code=team_data.get('short_code'),
                tla=team_data.get('tla'),
                founded_year=team_data.get('founded'),
                club_colors=team_data.get('club_colors'),
                website=team_data.get('website'),
                crest_url=team_data.get('crest'),
                badge_url=team_data.get('crest'),
                logo_url=team_data.get('crest'),
                area_id=team_data.get('area_id'),
                source_platform='FOOTBALL_DATA'
            )
            db.merge(team)
            team_count += 1
            
            # 插入球队-教练关联（教练已在前面插入）
            coach_data = team_data.get('coach')
            if coach_data:
                team_coach = TeamCoach(
                    team_id=team_data['id'],
                    coach_id=coach_data['id'],
                    is_current=1,
                    role='HEAD_COACH'
                )
                db.merge(team_coach)
                coach_count += 1
            
            # 插入球员
            players = team_data.get('players', [])
            for player_data in players:
                player = Player(
                    id=player_data['id'],
                    name_en_full=player_data.get('name_en_full', player_data.get('name_en')),
                    first_name_en=player_data.get('first_name_en'),
                    last_name_en=player_data.get('last_name_en'),
                    name_zh_full=player_data.get('name_zh_full'),
                    first_name_zh=player_data.get('first_name_zh'),
                    last_name_zh=player_data.get('last_name_zh'),
                    date_of_birth=datetime.strptime(player_data['date_of_birth'], '%Y-%m-%d') if player_data.get('date_of_birth') else None,
                    nationality=player_data.get('nationality'),
                    position_detail=player_data.get('position'),
                    shirt_number=player_data.get('shirt_number'),
                    source_platform='FOOTBALL_DATA'
                )
                db.merge(player)
                
                # 插入球员-球队关联
                player_team = PlayerTeam(
                    player_id=player_data['id'],
                    team_id=team_data['id'],
                    shirt_number=player_data.get('shirt_number'),
                    is_current=1
                )
                db.merge(player_team)
                player_count += 1
        
        db.commit()
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print(f"✅ 成功导入:")
        print(f"   • 球队: {team_count} 支")
        print(f"   • 教练: {coach_count} 名")
        print(f"   • 球员: {player_count} 名")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
        raise
    finally:
        db.close()


def verify_data():
    """验证数据"""
    print("\n" + "=" * 80)
    print("🔍 验证数据")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        tables = [
            (Area, '国家/地区'),
            (Position, '位置字典'),
            (League, '联赛'),
            (Team, '球队'),
            (Player, '球员'),
            (Coach, '教练'),
            (PlayerTeam, '球员-球队关联'),
            (TeamCoach, '球队-教练关联'),
        ]
        
        for model, name in tables:
            count = db.query(model).count()
            print(f"   ✅ {name}: {count} 条记录")
        
    finally:
        db.close()


if __name__ == '__main__':
    print("=" * 80)
    print("  🚀 数据导入工具")
    print("=" * 80)
    print("\n开始导入数据...\n")
    
    # 导入
    import_areas()
    import_leagues()
    import_teams_and_players()
    
    # 验证
    verify_data()
    
    print("\n" + "=" * 80)
    print("  ✅ 数据导入完成")
    print("=" * 80)
