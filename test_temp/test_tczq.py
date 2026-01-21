#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单独测试足球爬虫的脚本
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawler.spider_tczq import TczqSpider
from app.common.logger import log

def test_tczq_spider():
    """测试足球爬虫"""
    log.info("=== 开始测试足球爬虫 ===")
    try:
        spider = TczqSpider()
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

if __name__ == "__main__":
    test_tczq_spider()