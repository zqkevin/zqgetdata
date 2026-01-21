#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试足球比赛数据爬虫功能
"""

import sys
import os
from datetime import datetime
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.database import localdb
from app.database.tczq_models import TczqMatch, TczqHad, TczqHhad, TczqHafu, TczqTtg, TczqCrs

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_db_models():
    """
    测试数据库模型是否正确定义
    """
    logger.info("测试数据库模型开始")
    
    # 检查模型是否包含update_time字段，不包含update_date和update_time
    models_to_check = [TczqHad, TczqHhad, TczqHafu, TczqTtg, TczqCrs]
    
    for model in models_to_check:
        model_name = model.__name__
        logger.info(f"检查模型: {model_name}")
        
        # 检查字段
        columns = [col.name for col in model.__table__.columns]
        
        if 'update_time' in columns:
            logger.info(f"✓ {model_name} 包含 update_time 字段")
        else:
            logger.error(f"✗ {model_name} 缺少 update_time 字段")
            return False
        
        if 'update_date' in columns:
            logger.error(f"✗ {model_name} 不应该包含 update_date 字段")
            return False
    
    logger.info("测试数据库模型完成")
    return True


def test_odds_change_detection():
    """
    测试赔率变化检测逻辑
    """
    logger.info("测试赔率变化检测开始")
    
    from datetime import datetime
    
    # 创建测试比赛
    test_match = TczqMatch(
        match_id=999999,
        league_id=1,
        home_team_id=1,
        away_team_id=2,
        match_time="2024-01-01 15:00:00",
        status=0
    )
    
    try:
        localdb.add(test_match)
        logger.info("✓ 创建测试比赛成功")
    except Exception as e:
        logger.error(f"✗ 创建测试比赛失败: {e}")
        return False
    
    # 创建第一次赔率记录
    from datetime import datetime
    now = datetime.now()
    
    test_had_1 = TczqHad(
        match_id=999999,
        h=1.5,
        d=3.5,
        a=4.5,
        hf=1.8,
        df=3.3,
        af=3.8,
        update_time=now
    )
    
    try:
        localdb.add(test_had_1)
        logger.info("✓ 创建第一次赔率记录成功")
    except Exception as e:
        logger.error(f"✗ 创建第一次赔率记录失败: {e}")
        # 清理测试数据
        try:
            localdb.delete(test_match)
        except:
            pass
        return False
    
    # 模拟爬虫处理相同赔率的情况
    from app.crawler.spider_tczq import TczqSpider
    spider = TczqSpider()
    
    # 模拟比赛数据（相同赔率）
    match_data_same = {
        'had': {
            'h': 1.5,
            'd': 3.5,
            'a': 4.5,
            'hf': 1.8,
            'df': 3.3,
            'af': 3.8
        }
    }
    
    try:
        spider._process_match_odds(999999, match_data_same)
        logger.info("✓ 处理相同赔率成功")
    except Exception as e:
        logger.error(f"✗ 处理相同赔率失败: {e}")
        # 清理测试数据
        try:
            localdb.delete(test_had_1)
            localdb.delete(test_match)
        except:
            pass
        return False
    
    # 检查是否只创建了一条记录
    had_records = localdb.query(TczqHad).filter_by(match_id=999999).all()
    if len(had_records) == 1:
        logger.info("✓ 相同赔率未创建新记录")
    else:
        logger.error(f"✗ 相同赔率创建了{len(had_records)}条记录，应为1条")
        # 清理测试数据
        try:
            for record in had_records:
                localdb.delete(record)
            localdb.delete(test_match)
        except:
            pass
        return False
    
    # 模拟赔率变化
    match_data_changed = {
        'had': {
            'h': 1.6,
            'd': 3.6,
            'a': 4.4,
            'hf': 1.9,
            'df': 3.2,
            'af': 3.7
        }
    }
    
    try:
        spider._process_match_odds(999999, match_data_changed)
        logger.info("✓ 处理变化赔率成功")
    except Exception as e:
        logger.error(f"✗ 处理变化赔率失败: {e}")
        # 清理测试数据
        try:
            for record in had_records:
                localdb.delete(record)
            localdb.delete(test_match)
        except:
            pass
        return False
    
    # 检查是否创建了新记录
    had_records = localdb.query(TczqHad).filter_by(match_id=999999).all()
    if len(had_records) == 2:
        logger.info("✓ 赔率变化成功创建新记录")
    else:
        logger.error(f"✗ 赔率变化创建了{len(had_records)}条记录，应为2条")
        # 清理测试数据
        try:
            for record in had_records:
                localdb.delete(record)
            localdb.delete(test_match)
        except:
            pass
        return False
    
    # 清理测试数据
    try:
        for record in had_records:
            localdb.delete(record)
        localdb.delete(test_match)
        logger.info("✓ 清理测试数据成功")
    except Exception as e:
        logger.error(f"✗ 清理测试数据失败: {e}")
        return False
    
    logger.info("测试赔率变化检测完成")
    return True


if __name__ == "__main__":
    logger.info("开始测试爬虫功能")
    
    # 运行测试
    db_test_result = test_db_models()
    odds_test_result = test_odds_change_detection()
    
    # 汇总结果
    if db_test_result and odds_test_result:
        logger.info("✓ 所有测试通过")
        sys.exit(0)
    else:
        logger.error("✗ 部分测试失败")
        sys.exit(1)