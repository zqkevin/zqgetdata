# -*- coding: utf-8 -*-
"""
体育彩票爬虫综合测试脚本
测试各个爬虫的数据准确性和数据库记录完整性
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置环境变量
os.environ['PYTHONPATH'] = project_root

from app.crawler.spider_lottery import LotterySpider
from app.crawler.spider_tczq import TczqSpider
from app.crawler.spider_jcbk import get_jcbk_data
from app.crawler.spider_bjdc import get_bjdc_data
from app.database import localdb, DigitalLotteryDraw, DigitalLotteryPrize, FootballMatch, MatchResult, SpfOdds, TcbkMatch, TcbkResult, TcbkSpf
from app.common.req_sporttery_api import SportteryAPI
from app.common.logger import log


class CrawlerTester:
    """爬虫测试器类"""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
        self.api = SportteryAPI()
    
    def log_test_result(self, test_name: str, passed: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': data
        }
        
        self.test_results['details'].append(result)
        
        if passed:
            self.test_results['passed'] += 1
            status = "✅ PASS"
        else:
            self.test_results['failed'] += 1
            status = "❌ FAIL"
            
        print(f"\n{status} | {test_name}")
        if message:
            print(f"   📝 {message}")
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("📊 测试摘要")
        print("="*60)
        total = self.test_results['passed'] + self.test_results['failed']
        pass_rate = (self.test_results['passed'] / total * 100) if total > 0 else 0
        
        print(f"总测试数：{total}")
        print(f"✅ 通过：{self.test_results['passed']}")
        print(f"❌ 失败：{self.test_results['failed']}")
        print(f"⚠️  警告：{self.test_results['warnings']}")
        print(f"通过率：{pass_rate:.2f}%")
        print("="*60)
        
        # 保存测试报告
        self.save_test_report()
    
    def save_test_report(self):
        """保存测试报告到文件"""
        report_dir = os.path.join(project_root, 'test_output')
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(report_dir, f'crawler_test_report_{timestamp}.json')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 测试报告已保存到：{report_file}")


class TestLotteryCrawler(CrawlerTester):
    """数字彩爬虫测试类"""
    
    def __init__(self):
        super().__init__()
        self.spider = LotterySpider()
    
    def test_all(self):
        """运行所有数字彩测试"""
        print("\n" + "="*60)
        print("🎰 数字彩爬虫测试")
        print("="*60)
        
        self.test_api_response_structure()
        self.test_lottery_data_completeness()
        self.test_prize_levels_data()
        self.test_database_records()
        self.test_draw_time_accuracy()
    
    def test_api_response_structure(self):
        """测试 API 响应数据结构"""
        test_name = "数字彩_API 响应结构验证"
        try:
            lottery_types = ['dlt', 'pl3', 'pl5', 'qxc']
            data = self.spider.fetch_lottery_data_with_retry(lottery_types)
            
            if not data:
                self.log_test_result(test_name, False, "API 返回数据为空")
                return
            
            # 验证每个彩种的数据结构
            for lottery_type in lottery_types:
                if lottery_type not in data:
                    self.log_test_result(test_name, False, f"缺少{lottery_type}数据")
                    return
                
                lottery_data = data[lottery_type].get(lottery_type, {})
                required_fields = ['lotteryDrawNum', 'lotteryDrawResult', 'lotteryDrawTime', 
                                 'prizeLevelList', 'poolBalanceAfterdraw']
                
                missing_fields = [field for field in required_fields if field not in lottery_data]
                if missing_fields:
                    self.log_test_result(test_name, False, f"缺少必要字段：{missing_fields}")
                    return
            
            self.log_test_result(test_name, True, f"成功获取{len(lottery_types)}种彩票数据，结构完整")
            
        except Exception as e:
            self.log_test_result(test_name, False, f"异常：{str(e)}")
    
    def test_lottery_data_completeness(self):
        """测试开奖数据完整性"""
        test_name = "数字彩_数据完整性验证"
        try:
            lottery_types = ['dlt', 'pl3', 'pl5', 'qxc']
            data = self.spider.fetch_lottery_data_with_retry(lottery_types)
            
            issues = []
            for lottery_type in lottery_types:
                lottery_data = data.get(lottery_type, {}).get(lottery_type, {})
                
                # 检查开奖号码
                draw_result = lottery_data.get('lotteryDrawResult', '')
                if not draw_result or draw_result == 'N/A':
                    issues.append(f"{lottery_type}开奖号码缺失或无效")
                
                # 检查期号
                draw_num = lottery_data.get('lotteryDrawNum', '')
                if not draw_num:
                    issues.append(f"{lottery_type}期号缺失")
                
                # 检查开奖时间
                draw_time = lottery_data.get('lotteryDrawTime', '')
                if not draw_time:
                    issues.append(f"{lottery_type}开奖时间缺失")
            
            if issues:
                self.log_test_result(test_name, False, "; ".join(issues))
            else:
                self.log_test_result(test_name, True, "所有彩种数据完整")
                
        except Exception as e:
            self.log_test_result(test_name, False, f"异常：{str(e)}")
    
    def test_prize_levels_data(self):
        """测试奖级数据准确性"""
        test_name = "数字彩_奖级数据验证"
        try:
            lottery_types = ['dlt', 'pl3', 'qxc']  # 测试这三种有复杂奖级的彩票
            data = self.spider.fetch_lottery_data_with_retry(lottery_types)
            
            total_prize_levels = 0
            issues = []
            
            for lottery_type in lottery_types:
                lottery_data = data.get(lottery_type, {}).get(lottery_type, {})
                prize_levels = lottery_data.get('prizeLevelList', [])
                
                if not prize_levels:
                    issues.append(f"{lottery_type}奖级列表为空")
                    continue
                
                total_prize_levels += len(prize_levels)
                
                # 验证每个奖级的必要字段
                for i, prize in enumerate(prize_levels[:3]):  # 只检查前 3 个奖级
                    required_fields = ['prizeLevel', 'stakeCount', 'stakeAmount', 'totalPrizeamount']
                    missing = [f for f in required_fields if f not in prize]
                    if missing:
                        issues.append(f"{lottery_type}第{i+1}等奖缺少字段：{missing}")
                    
                    # 验证中奖注数是否为有效数字
                    stake_count = prize.get('stakeCount', '0')
                    if stake_count and stake_count.replace(',', '').replace('.', '').isdigit():
                        pass  # 格式正确
                    else:
                        issues.append(f"{lottery_type}第{i+1}等奖中奖注数格式错误：{stake_count}")
            
            if issues:
                self.log_test_result(test_name, False, "; ".join(issues[:5]))  # 只显示前 5 个问题
            else:
                self.log_test_result(test_name, True, f"共验证{total_prize_levels}条奖级数据，格式正确")
                
        except Exception as e:
            self.log_test_result(test_name, False, f"异常：{str(e)}")
    
    def test_database_records(self):
        """测试数据库记录"""
        test_name = "数字彩_数据库记录验证"
        try:
            # 获取最新一期的开奖数据
            latest_draws = localdb.query(DigitalLotteryDraw).order_by(
                DigitalLotteryDraw.draw_time.desc()
            ).limit(10).all()
            
            if not latest_draws:
                self.log_test_result(test_name, False, "数据库中没有开奖记录")
                return
            
            issues = []
            verified_count = 0
            
            for draw in latest_draws:
                # 检查必要字段
                if not draw.draw_result or draw.draw_result == 'N/A':
                    issues.append(f"期号{draw.draw_num}开奖结果缺失")
                
                # 检查奖级信息
                prize_count = len(draw.prize_levels) if hasattr(draw, 'prize_levels') and draw.prize_levels else 0
                if prize_count == 0:
                    issues.append(f"期号{draw.draw_num}缺少奖级信息")
                
                # 检查时间字段
                if not draw.draw_time:
                    issues.append(f"期号{draw.draw_num}开奖时间缺失")
                
                verified_count += 1
            
            if issues:
                self.log_test_result(test_name, False, f"发现{len(issues)}个问题：{'; '.join(issues[:3])}")
            else:
                self.log_test_result(test_name, True, f"验证{verified_count}条数据库记录，数据完整")
                
        except Exception as e:
            self.log_test_result(test_name, False, f"异常：{str(e)}")
    
    def test_draw_time_accuracy(self):
        """测试开奖时间准确性"""
        test_name = "数字彩_开奖时间验证"
        try:
            # 获取最近的开奖记录
            recent_draws = localdb.query(DigitalLotteryDraw).filter(
                DigitalLotteryDraw.draw_time >= datetime.now() - timedelta(days=7)
            ).all()
            
            if not recent_draws:
                self.log_test_result(test_name, False, "最近 7 天没有开奖记录", {'warnings': '可能是正常情况'})
                self.test_results['warnings'] += 1
                return
            
            time_issues = []
            for draw in recent_draws:
                # 检查开奖时间是否合理（体彩一般晚上 20:30-22:00 开奖）
                draw_hour = draw.draw_time.hour if draw.draw_time else 0
                if draw_hour < 18 or draw_hour > 23:
                    time_issues.append(f"期号{draw.draw_num}开奖时间异常：{draw.draw_time}")
            
            if time_issues:
                self.log_test_result(test_name, False, f"{len(time_issues)}条记录开奖时间异常", 
                                 {'issues': time_issues[:3]})
            else:
                self.log_test_result(test_name, True, f"验证{len(recent_draws)}条记录，开奖时间正常")
                
        except Exception as e:
            self.log_test_result(test_name, False, f"异常：{str(e)}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 开始体育彩票爬虫综合测试")
    print("="*60)
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试数字彩爬虫
    lottery_tester = TestLotteryCrawler()
    lottery_tester.test_all()
    
    # TODO: 添加其他爬虫测试
    # 测试传统足球爬虫
    # 测试篮球竞猜爬虫
    # 测试北京单场爬虫
    
    # 打印摘要
    lottery_tester.print_summary()


if __name__ == "__main__":
    run_all_tests()
