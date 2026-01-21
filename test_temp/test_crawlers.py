#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫功能的临时脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.common.logger import log
from app.crawler.spider_tczq import TczqSpider
from app.crawler.spider_jcbk import get_jcbk_data
from app.crawler.spider_lottery import LotterySpider

def test_tczq_spider():
    """测试足球爬虫"""
    log.info("=== 测试足球爬虫开始 ===")
    try:
        spider = TczqSpider()
        # 只获取最近的一些比赛数据，避免过多请求
        matches = spider.get_current_matches()
        log.info(f"成功获取 {len(matches)} 场足球比赛数据")
        return True
    except Exception as e:
        log.error(f"足球爬虫测试失败: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False
    finally:
        log.info("=== 测试足球爬虫结束 ===")

def test_jcbk_spider():
    """测试篮球爬虫"""
    log.info("=== 测试篮球爬虫开始 ===")
    try:
        spider = get_jcbk_data()
        # 获取篮球比赛数据
        spider.get_gamedata()
        log.info("成功获取篮球比赛数据")
        return True
    except Exception as e:
        log.error(f"篮球爬虫测试失败: {str(e)}")
        return False
    finally:
        log.info("=== 测试篮球爬虫结束 ===")

def test_lottery_spider():
    """测试数字彩爬虫"""
    log.info("=== 测试数字彩爬虫开始 ===")
    try:
        spider = LotterySpider()
        # 测试获取所有彩票最新数据
        saved_count = spider.fetch_and_save_lottery_data()
        log.info(f"成功获取并保存{saved_count}条彩票数据")
        return True
    except Exception as e:
        log.error(f"数字彩爬虫测试失败: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False
    finally:
        log.info("=== 测试数字彩爬虫结束 ===")

if __name__ == "__main__":
    log.info("开始测试所有爬虫功能")
    
    test_results = {
        "足球爬虫": test_tczq_spider(),
        "篮球爬虫": test_jcbk_spider(),
        "数字彩爬虫": test_lottery_spider()
    }
    
    log.info("\n=== 测试结果总结 ===")
    for name, result in test_results.items():
        status = "成功" if result else "失败"
        log.info(f"{name}: {status}")
    
    # 检查是否有测试失败
    if all(test_results.values()):
        log.info("所有爬虫测试均成功！")
        sys.exit(0)
    else:
        log.error("部分爬虫测试失败！")
        sys.exit(1)