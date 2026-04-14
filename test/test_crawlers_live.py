# -*- coding: utf-8 -*-
"""
爬虫实战测试 - 实际执行爬虫并验证数据库记录
"""
import os
import sys
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.crawler.spider_lottery import LotterySpider
from app.crawler.spider_tczq import TczqSpider
from app.crawler.spider_jcbk import get_jcbk_data
from app.database import localdb, DigitalLotteryDraw, DigitalLotteryPrize, FootballMatch, TcbkMatch


def test_lottery_spider():
    """测试数字彩爬虫"""
    print("\n" + "="*60)
    print("🎰 测试数字彩爬虫")
    print("="*60)
    
    try:
        spider = LotterySpider()
        
        # 执行爬虫
        print("\n开始执行爬虫...")
        saved_count = spider.update_latest_lottery_data()
        
        if saved_count > 0:
            print(f"✅ 成功保存{saved_count}条新记录")
            
            # 验证数据库
            print("\n验证数据库记录:")
            for lottery_type, info in spider.lottery_mapping.items():
                count = localdb.query(DigitalLotteryDraw).filter_by(
                    lottery_code=info['code']
                ).count()
                
                prizes_count = localdb.query(DigitalLotteryPrize).join(DigitalLotteryDraw).filter(
                    DigitalLotteryDraw.lottery_code == info['code']
                ).count()
                
                print(f"  {info['lottery_name']}: {count}期，{prizes_count}条奖级记录")
            
            print("\n✅ 数字彩爬虫测试通过")
            return True
        else:
            print("⚠️ 没有保存新记录 (可能数据已存在或 API 失败)")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_tczq_spider():
    """测试传统足球爬虫"""
    print("\n" + "="*60)
    print("⚽ 测试传统足球爬虫")
    print("="*60)
    
    try:
        spider = TczqSpider()
        
        # 获取当前赛事
        print("\n获取当前赛事信息...")
        matches = spider.get_current_matches()
        
        if matches:
            print(f"✅ 成功获取{len(matches)}场比赛信息")
            
            # 验证数据库
            tczq_count = localdb.query(FootballMatch).filter_by(
                match_type='tczq'
            ).count()
            print(f"\n数据库中传统足球比赛数：{tczq_count}")
            
            # 检查赔率数据
            from app.database import SpfOdds
            spf_count = localdb.query(SpfOdds).count()
            print(f"胜平负赔率记录数：{spf_count}")
            
            print("\n✅ 传统足球爬虫测试通过")
            return True
        else:
            print("⚠️ 没有获取到比赛数据")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_basketball_spider():
    """测试篮球竞猜爬虫"""
    print("\n" + "="*60)
    print("🏀 测试篮球竞猜爬虫")
    print("="*60)
    
    try:
        spider = get_jcbk_data()
        
        # 获取比赛数据
        print("\n获取篮球比赛数据...")
        spider.get_gamedata()
        
        # 验证数据库
        tcbk_count = localdb.query(TcbkMatch).count()
        
        if tcbk_count > 0:
            print(f"✅ 数据库中篮球比赛数：{tcbk_count}")
            
            # 检查赔率数据
            from app.database import TcbkSpf
            spf_count = localdb.query(TcbkSpf).count()
            print(f"胜负赔率记录数：{spf_count}")
            
            print("\n✅ 篮球竞猜爬虫测试通过")
            return True
        else:
            print("⚠️ 没有获取到比赛数据")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🧪 爬虫实战测试")
    print("="*60)
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'lottery': False,
        'football': False,
        'basketball': False
    }
    
    # 测试各个爬虫
    results['lottery'] = test_lottery_spider()
    results['football'] = test_tczq_spider()
    results['basketball'] = test_basketball_spider()
    
    # 打印摘要
    print("\n" + "="*60)
    print("📊 测试摘要")
    print("="*60)
    print(f"数字彩爬虫：{'✅ 通过' if results['lottery'] else '❌ 失败'}")
    print(f"传统足球爬虫：{'✅ 通过' if results['football'] else '❌ 失败'}")
    print(f"篮球竞猜爬虫：{'✅ 通过' if results['basketball'] else '❌ 失败'}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\n通过率：{passed}/{total} ({passed/total*100:.1f}%)")
    print("="*60)


if __name__ == "__main__":
    main()
