#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试北京单场爬虫功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bjdc import get_bjdc_data

def test_bjdc_spider():
    """
    测试北京单场爬虫功能
    """
    print("开始测试北京单场爬虫功能...")
    
    try:
        # 创建爬虫实例
        bjdc_spider = get_bjdc_data()
        
        # 调用获取比赛数据的方法
        bjdc_spider.get_gamedata()
        
        print("北京单场爬虫功能测试完成!")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bjdc_spider()