# -*- coding: utf-8 -*-
"""
修复TCBK历史异常比赛的赛果数据
从API获取赛果并更新到服务器数据库
"""
import sys
import os
# 添加get_data目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'get_data'))

from app.crawler.jcbk_result import JcbkResultCollector
from app.database import localdb, TcbkMatch, TcbkResult
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tcbk_fix')

def fix_abnormal_matches():
    """修复异常比赛"""
    
    # 1. 查询所有需要修复的比赛（status=9或超过4天的status=0）
    cutoff_date = (datetime.now() - timedelta(days=4)).date()
    
    matches = localdb.query(TcbkMatch).filter(
        (TcbkMatch.match_status == 9) | 
        ((TcbkMatch.match_status == 0) & (TcbkMatch.match_date < str(cutoff_date)))
    ).all()
    
    logger.info(f"找到 {len(matches)} 场需要修复的比赛")
    
    if not matches:
        logger.info("没有需要修复的比赛")
        return
    
    # 2. 提取日期范围
    match_dates = [m.match_date for m in matches if m.match_date]
    if not match_dates:
        logger.warning("无法提取比赛日期")
        return
    
    min_date = min(match_dates)
    max_date = max(match_dates)
    
    logger.info(f"赛果时间范围: {min_date} 到 {max_date}")
    
    # 3. 创建赛果处理器
    processor = JcbkResultCollector()
    
    # 4. 从API获取赛果
    try:
        results = processor.api.get_basketball_match_results(
            match_begin_date=min_date,
            match_end_date=max_date
        )
    except Exception as e:
        logger.error(f"API请求失败: {e}")
        return
    
    if not results:
        logger.warning("API未返回赛果数据")
        return
    
    logger.info(f"从API获取到 {len(results)} 条赛果数据")
    
    # 5. 建立matchId索引
    api_results_by_id = {}
    for result_data in results:
        match_id = result_data.get('matchId')
        if match_id:
            try:
                api_results_by_id[int(match_id)] = result_data
            except (ValueError, TypeError):
                pass
    
    logger.info(f"建立matchId索引: {len(api_results_by_id)} 条")
    
    # 6. 匹配并保存赛果
    success_count = 0
    fail_count = 0
    
    for match in matches:
        if not match.match_id:
            logger.debug(f"比赛 {match.home_team_all_name} vs {match.away_team_all_name} 缺少match_id，跳过")
            fail_count += 1
            continue
        
        # 通过matchId查找赛果
        api_result = api_results_by_id.get(match.match_id)
        
        if not api_result:
            logger.debug(f"未找到match_id={match.match_id}的赛果")
            fail_count += 1
            continue
        
        # 检查是否有比分数据
        home_score = api_result.get('homeScore')
        away_score = api_result.get('awayScore')
        
        if home_score is None or away_score is None:
            logger.debug(f"match_id={match.match_id} 缺少比分数据")
            fail_count += 1
            continue
        
        try:
            # 创建赛果记录
            result_record = TcbkResult(
                match_id=match.match_id,
                home_score=int(home_score),
                away_score=int(away_score),
                status=api_result.get('status', 2),
                quarter_scores=api_result.get('quarterScores', ''),
                half_score=api_result.get('halfScore', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            localdb.add(result_record, close=False)
            
            # 更新比赛状态为8（已获取赛果）
            match.match_status = 8
            localdb.update(match, close=False)
            
            success_count += 1
            logger.info(f"✅ 成功: {match.home_team_all_name} {home_score}:{away_score} {match.away_team_all_name}")
            
        except Exception as e:
            logger.error(f"❌ 保存失败 match_id={match.match_id}: {e}")
            fail_count += 1
    
    logger.info(f"\n修复完成 - 成功: {success_count}, 失败: {fail_count}")
    
    # 提交事务
    localdb.session.commit()
    localdb.close()

if __name__ == '__main__':
    fix_abnormal_matches()
