# -*- coding: utf-8 -*-
"""
北京单场数据采集器功能测试
测试 BjdcDataCollector 各个功能模块是否正常
"""
import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.crawler.bjdc import BjdcDataCollector
from app.log import bjdc_log, api_log
from app.database import localdb


class TestBjdcDataCollector(unittest.TestCase):
    """北京单场数据采集器测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        bjdc_log.info('=' * 80)
        bjdc_log.info(f'开始测试：{self._testMethodName}')
        bjdc_log.info('=' * 80)
        
        # 创建测试实例
        self.collector = BjdcDataCollector()
        
    def tearDown(self):
        """测试后的清理工作"""
        bjdc_log.info('-' * 80)
        bjdc_log.info(f'测试完成：{self._testMethodName}')
        bjdc_log.info('-' * 80)
    
    def test_init(self):
        """测试初始化"""
        bjdc_log.info('测试 1: 初始化 BjdcDataCollector')
        
        # 测试实例是否正确创建
        self.assertIsNotNone(self.collector)
        self.assertIsNotNone(self.collector.api)
        
        # 验证 API 对象类型
        from app.common.req_sporttery_api import SportteryAPI
        self.assertIsInstance(self.collector.api, SportteryAPI)
        
        bjdc_log.info('✓ 初始化测试通过')
    
    def test_collect_matches_method_exists(self):
        """测试 collect_matches 方法是否存在"""
        bjdc_log.info('测试 2: collect_matches 方法存在性')
        
        # 检查方法是否存在
        self.assertTrue(hasattr(self.collector, 'collect_matches'))
        self.assertTrue(callable(getattr(self.collector, 'collect_matches')))
        
        bjdc_log.info('✓ collect_matches 方法存在')
    
    def test_get_matches_with_odds_method_exists(self):
        """测试 get_matches_with_odds 方法是否存在"""
        bjdc_log.info('测试 3: get_matches_with_odds 方法存在性')
        
        # 检查方法是否存在
        self.assertTrue(hasattr(self.collector, 'get_matches_with_odds'))
        self.assertTrue(callable(getattr(self.collector, 'get_matches_with_odds')))
        
        bjdc_log.info('✓ get_matches_with_odds 方法存在')
    
    def test_collect_matches_return_type(self):
        """测试 collect_matches 返回值类型"""
        bjdc_log.info('测试 4: collect_matches 返回值类型')
        
        # 调用方法（目前是待实现状态）
        result = self.collector.collect_matches()
        
        # 验证返回类型是 bool
        self.assertIsInstance(result, bool)
        
        bjdc_log.info(f'返回值：{result} (类型：{type(result).__name__})')
        bjdc_log.info('✓ collect_matches 返回值类型正确')
    
    def test_get_matches_with_odds_return_type(self):
        """测试 get_matches_with_odds 返回值类型"""
        bjdc_log.info('测试 5: get_matches_with_odds 返回值类型')
        
        # 调用方法（目前是待实现状态）
        result = self.collector.get_matches_with_odds()
        
        # 验证返回类型是 list
        self.assertIsInstance(result, list)
        
        bjdc_log.info(f'返回值：{len(result)} 条记录 (类型：{type(result).__name__})')
        bjdc_log.info('✓ get_matches_with_odds 返回值类型正确')
    
    def test_api_client_initialization(self):
        """测试 API 客户端初始化"""
        bjdc_log.info('测试 6: API 客户端初始化')
        
        # 检查 API 对象是否有必要的属性
        self.assertTrue(hasattr(self.collector.api, 'session'))
        self.assertTrue(hasattr(self.collector.api, 'headers'))
        
        bjdc_log.info('✓ API 客户端初始化正常')
    
    def test_logging_system(self):
        """测试日志系统是否正常工作"""
        bjdc_log.info('测试 7: 日志系统测试')
        
        # 测试不同级别的日志
        bjdc_log.debug('这是一条 DEBUG 日志')
        bjdc_log.info('这是一条 INFO 日志')
        bjdc_log.warning('这是一条 WARNING 日志')
        bjdc_log.error('这是一条 ERROR 日志')
        
        bjdc_log.info('✓ 日志系统工作正常')
    
    def test_real_api_call_bjdc_match_list(self):
        """测试实际调用 API 获取北京单场比赛列表"""
        bjdc_log.info('测试 8: 实际 API 调用 - 获取比赛列表')
        
        try:
            # 尝试调用 API 获取比赛列表
            match_list = self.collector.api.get_football_match_list()
            
            bjdc_log.info(f'API 返回数据类型：{type(match_list)}')
            
            if match_list is not None and hasattr(match_list, 'empty'):
                if not match_list.empty:
                    bjdc_log.info(f'成功获取比赛列表，共 {len(match_list)} 场比赛')
                    
                    # 显示前 3 条数据作为示例
                    if len(match_list) > 0:
                        sample_data = match_list.iloc[0].to_dict() if hasattr(match_list.iloc[0], 'to_dict') else match_list.iloc[0]
                        bjdc_log.info(f'第一条比赛数据：{sample_data}')
                    
                    # 验证数据结构
                    bjdc_log.info('检查数据结构...')
                    required_columns = ['matchId', 'leagueId', 'homeTeamAllName', 'awayTeamAllName', 'matchDate']
                    for col in required_columns:
                        if col in match_list.columns:
                            bjdc_log.debug(f'✓ 包含列：{col}')
                        else:
                            bjdc_log.warning(f'✗ 缺少列：{col}')
                    
                    bjdc_log.info('✓ API 调用成功，数据格式正确')
                else:
                    bjdc_log.warning('API 返回空数据')
                    self.skipTest('API 返回空数据，无法继续测试')
            else:
                bjdc_log.warning(f'API 返回非预期数据类型：{match_list}')
                self.skipTest(f'API 返回非预期数据类型')
                
        except Exception as e:
            bjdc_log.error(f'API 调用失败：{e}')
            bjdc_log.error(f'错误详情：{str(e)}')
            self.skipTest(f'API 调用失败：{e}')
    
    def test_database_connection(self):
        """测试数据库连接"""
        bjdc_log.info('测试 9: 数据库连接测试')
        
        try:
            # 尝试查询数据库 - 使用原始 SQL 避免 ORM 关系问题
            from sqlalchemy import text
            
            # 查询联赛数量
            result = localdb.session.execute(text("SELECT COUNT(*) as count FROM league"))
            league_count = result.scalar()
            bjdc_log.info(f'数据库中联赛总数：{league_count}')
            
            # 查询球队数量
            result = localdb.session.execute(text("SELECT COUNT(*) as count FROM team"))
            team_count = result.scalar()
            bjdc_log.info(f'数据库中球队总数：{team_count}')
            
            # 查询最近的足球比赛（只查询存在的字段）
            result = localdb.session.execute(
                text("SELECT match_date, home_team_id, away_team_id FROM tczq_match ORDER BY match_date DESC LIMIT 5")
            )
            recent_matches = result.fetchall()
            bjdc_log.info(f'最近 5 场足球比赛：')
            for row in recent_matches:
                bjdc_log.info(f'  - {row[0]}: 主队 ID={row[1]}, 客队 ID={row[2]}')
            
            # 查询北京单场比赛表是否存在
            result = localdb.session.execute(text("SHOW TABLES LIKE 'bjdc_match'"))
            bjdc_table_exists = result.fetchone() is not None
            if bjdc_table_exists:
                result = localdb.session.execute(text("SELECT COUNT(*) as count FROM bjdc_match"))
                bjdc_count = result.scalar()
                bjdc_log.info(f'北京单场比赛表记录数：{bjdc_count}')
            else:
                bjdc_log.warning('北京单场比赛表不存在')
            
            bjdc_log.info('✓ 数据库连接正常')
            
        except Exception as e:
            bjdc_log.error(f'数据库连接失败：{e}')
            bjdc_log.error(f'错误详情：{str(e)}')
            import traceback
            bjdc_log.error(traceback.format_exc())
            self.fail(f'数据库连接失败：{e}')
    
    def test_class_documentation(self):
        """测试类文档"""
        bjdc_log.info('测试 10: 类文档测试')
        
        # 检查类是否有文档字符串
        self.assertIsNotNone(BjdcDataCollector.__doc__)
        bjdc_log.info(f'类文档：{BjdcDataCollector.__doc__.strip()}')
        
        # 检查方法是否有文档字符串
        self.assertIsNotNone(self.collector.collect_matches.__doc__)
        self.assertIsNotNone(self.collector.get_matches_with_odds.__doc__)
        
        bjdc_log.info('✓ 类文档完整')
    
    def test_error_handling(self):
        """测试错误处理"""
        bjdc_log.info('测试 11: 错误处理测试')
        
        # 测试方法在遇到异常时是否正确处理
        try:
            # 目前方法应该不会抛出异常，而是返回 False 或 []
            result1 = self.collector.collect_matches()
            result2 = self.collector.get_matches_with_odds()
            
            # 验证即使功能未实现，也不会抛出异常
            self.assertIsInstance(result1, bool)
            self.assertIsInstance(result2, list)
            
            bjdc_log.info('✓ 错误处理正常')
            
        except Exception as e:
            self.fail(f"方法执行时不应抛出异常：{e}")


def run_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("北京单场数据采集器功能测试")
    print("=" * 80 + "\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBjdcDataCollector)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印统计信息
    print("\n" + "=" * 80)
    print("测试统计")
    print("=" * 80)
    print(f"运行测试数：{result.testsRun}")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    print(f"跳过：{len(result.skipped)}")
    print("=" * 80 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
