# -*- coding: utf-8 -*-
"""
体育赛事爬虫自动化管理程序
功能:
1. 使用定时器随机在 5-10 分钟执行一次全面的体育赛事爬取
2. 记录赔率变化和新增赛事
3. 数字彩票只检查当天数据，不频繁爬取
"""
import os
import sys
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.crawler import (
    TczqDataCollector, TczqResultCollector,
    JcbkDataCollector, JcbkResultCollector,
    BjdcDataCollector, BjdcResultCollector,
    LotteryDataCollector
)
from app.common.logger import log as logger


class CrawlerScheduler:
    """爬虫调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.min_interval = 5  # 最小间隔 (分钟)
        self.max_interval = 10  # 最大间隔 (分钟)
        
        # 初始化爬虫实例
        self.tczq_collector = TczqDataCollector()
        self.tczq_result = TczqResultCollector()
        self.bjdc_collector = BjdcDataCollector()
        self.bjdc_result = BjdcResultCollector()
        self.jcbk_collector = JcbkDataCollector()
        self.jcbk_result = JcbkResultCollector()
        self.lottery_collector = LotteryDataCollector()
        
        # 记录上次爬取时间
        self.last_sports_crawl_time: Optional[datetime] = None
        self.last_lottery_check_time: Optional[datetime] = None
        
    def _get_random_interval(self) -> int:
        """获取随机间隔时间 (秒)"""
        minutes = random.uniform(self.min_interval, self.max_interval)
        return int(minutes * 60)
    
    def _crawl_sports_matches(self):
        """爬取体育赛事数据 (竞彩足球、北京单场、篮球竞猜)"""
        try:
            logger.info("=" * 80)
            logger.info("开始爬取体育赛事数据...")
            logger.info(f"爬取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            
            # 1. 爬取竞彩足球
            logger.info("【步骤 1】爬取竞彩足球...")
            try:
                self.tczq_collector.get_current_matches()
                logger.info("OK 竞彩足球")
            except Exception as e:
                logger.error(f"ERROR 竞彩足球：{e}")
            
            # 2. 爬取北京单场
            logger.info("【步骤 2】爬取北京单场...")
            try:
                self.bjdc_collector.collect_matches()
                logger.info("OK 北京单场")
            except Exception as e:
                logger.error(f"ERROR 北京单场：{e}")
            
            # 3. 爬取篮球竞猜
            logger.info("【步骤 3】爬取篮球竞猜...")
            try:
                self.jcbk_collector.get_matches_with_odds()
                logger.info("OK 篮球竞猜")
            except Exception as e:
                logger.error(f"ERROR 篮球竞猜：{e}")
            
            # 记录爬取时间
            self.last_sports_crawl_time = datetime.now()
            
            logger.info("体育赛事数据爬取完成!")
            logger.info(f"下次爬取：{self.min_interval}-{self.max_interval}分钟后")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"体育赛事爬取过程中发生错误：{e}")
    
    def _crawl_sports_results(self):
        """爬取体育赛事赛果 (北京单场、竞彩足球、篮球竞猜)"""
        try:
            logger.info("=" * 80)
            logger.info("开始爬取体育赛事赛果...")
            logger.info(f"爬取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            
            # 1. 获取北京单场赛果
            logger.info("【步骤 1】获取北京单场赛果...")
            try:
                self.bjdc_result.get_and_save_results()
                logger.info("OK 北京单场赛果")
            except Exception as e:
                logger.error(f"ERROR 北京单场赛果：{e}")
            
            # 2. 获取竞彩足球赛果
            logger.info("【步骤 2】获取竞彩足球赛果...")
            try:
                self.tczq_result.get_and_save_results()
                logger.info("OK 竞彩足球赛果")
            except Exception as e:
                logger.error(f"ERROR 竞彩足球赛果：{e}")
            
            # 3. 获取篮球赛果
            logger.info("【步骤 3】获取篮球赛果...")
            try:
                self.jcbk_result.get_and_save_results()
                logger.info("OK 篮球赛果")
            except Exception as e:
                logger.error(f"ERROR 篮球赛果：{e}")
            
            logger.info("体育赛事赛果爬取完成!")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"体育赛事赛果爬取过程中发生错误：{e}")
    
    def _check_digital_lottery(self):
        """检查数字彩票数据 (仅当天数据)"""
        try:
            # 只在距离上次检查超过 1 小时后才检查
            if self.last_lottery_check_time:
                time_since_last = datetime.now() - self.last_lottery_check_time
                if time_since_last < timedelta(hours=1):
                    logger.debug(f"数字彩票刚检查过不久 ({time_since_last.seconds//60}分钟前),跳过本次检查")
                    return
            
            logger.info("检查数字彩票数据...")
            logger.info(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            
            # 爬取数字彩票
            logger.info("【数字彩票】")
            try:
                # 使用 update_latest_lottery_data 方法 (只获取当天数据)
                saved_count = self.lottery_collector.update_latest_lottery_data()
                logger.info(f"OK 数字彩票 (保存{saved_count}条记录)")
            except Exception as e:
                logger.error(f"ERROR 数字彩票：{e}")
            
            # 记录检查时间
            self.last_lottery_check_time = datetime.now()
            
        except Exception as e:
            logger.error(f"数字彩票检查异常：{e}")
    
    def _scheduler_loop(self):
        """调度器主循环"""
        logger.info("爬虫调度器已启动")
        logger.info(f"爬取间隔：随机 {self.min_interval}-{self.max_interval} 分钟")
        logger.info("按 Ctrl+C 停止调度器\n")
        
        while self.running:
            try:
                # 1. 爬取体育赛事 (赔率)
                self._crawl_sports_matches()
                
                # 2. 爬取体育赛事赛果 (开赛后)
                self._crawl_sports_results()
                
                # 3. 检查数字彩票 (如果距离上次检查超过 1 小时)
                self._check_digital_lottery()
                
                # 4. 等待随机间隔时间
                interval = self._get_random_interval()
                logger.info(f"\n等待 {interval//60}分{interval%60}秒后进行下一次爬取...\n")
                
                # 可中断的等待
                sleep_start = datetime.now()
                while datetime.now() - sleep_start < timedelta(seconds=interval):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"调度器循环中发生错误：{e}")
                # 即使出错也等待一段时间后继续
                time.sleep(60)
    
    def start(self, block=True):
        """
        启动调度器
        
        Args:
            block: 是否阻塞当前线程 (True 为阻塞，False 为后台运行)
        """
        if self.running:
            logger.warning("调度器已经在运行中!")
            return
        
        self.running = True
        
        if block:
            # 在当前线程直接运行
            self._scheduler_loop()
        else:
            # 在后台线程运行
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            logger.info("调度器已在后台启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)
    
    def run_once(self):
        """立即执行一次完整爬取 (用于测试)"""
        self._crawl_sports_matches()
        self._crawl_sports_results()
        self._check_digital_lottery()


def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='体育赛事爬虫自动化管理程序')
    parser.add_argument('--once', action='store_true', help='只执行一次爬取 (用于测试)')
    parser.add_argument('--min-interval', type=int, default=5, help='最小爬取间隔 (分钟),默认 5 分钟')
    parser.add_argument('--max-interval', type=int, default=10, help='最大爬取间隔 (分钟),默认 10 分钟')
    
    args = parser.parse_args()
    
    # 创建调度器
    scheduler = CrawlerScheduler()
    scheduler.min_interval = args.min_interval
    scheduler.max_interval = args.max_interval
    
    try:
        if args.once:
            # 只执行一次
            scheduler.run_once()
        else:
            # 持续运行
            scheduler.start(block=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"程序异常：{e}")
        scheduler.stop()
        sys.exit(1)


if __name__ == '__main__':
    main()
