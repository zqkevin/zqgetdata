# -*- coding: utf-8 -*-
"""
爬虫模块单元测试
测试顺序：main.py -> job() -> 各爬虫采集器
"""
import pytest


class TestTczqCollector:
    """体彩足球采集器测试"""
    
    def test_collector_creation(self, tczq_collector):
        """测试采集器可以创建"""
        assert tczq_collector is not None
    
    def test_has_required_methods(self, tczq_collector):
        """测试采集器包含必要的方法"""
        assert hasattr(tczq_collector, 'get_current_matches')
        assert hasattr(tczq_collector, '_process_league_info')
        assert hasattr(tczq_collector, '_process_match_info')


class TestJcbkCollector:
    """竞彩篮球采集器测试"""
    
    def test_collector_creation(self, jcbk_collector):
        """测试采集器可以创建"""
        assert jcbk_collector is not None
    
    def test_has_required_methods(self, jcbk_collector):
        """测试采集器包含必要的方法"""
        assert hasattr(jcbk_collector, 'get_matches_with_odds')
        assert hasattr(jcbk_collector, '_process_league_info')
        assert hasattr(jcbk_collector, '_process_match_data')


class TestBjdcCollector:
    """北京单场采集器测试"""
    
    def test_collector_creation(self, bjdc_collector):
        """测试采集器可以创建"""
        assert bjdc_collector is not None
    
    def test_has_required_methods(self, bjdc_collector):
        """测试采集器包含必要的方法"""
        assert hasattr(bjdc_collector, 'collect_matches')


class TestLotteryCollector:
    """数字彩采集器测试"""
    
    def test_collector_creation(self, lottery_collector):
        """测试采集器可以创建"""
        assert lottery_collector is not None
    
    def test_has_required_methods(self, lottery_collector):
        """测试采集器包含必要的方法"""
        assert hasattr(lottery_collector, 'update_latest_lottery_data')


class TestResultCollectors:
    """赛果获取器测试"""
    
    def test_tczq_result_collector_exists(self):
        """测试体彩足球赛果获取器存在"""
        from app.crawler.tczq_result import TczqResultCollector
        collector = TczqResultCollector()
        assert collector is not None
        assert hasattr(collector, 'get_and_save_results')
    
    def test_jcbk_result_collector_exists(self):
        """测试竞彩篮球赛果获取器存在"""
        from app.crawler.jcbk_result import JcbkResultCollector
        collector = JcbkResultCollector()
        assert collector is not None
        assert hasattr(collector, 'get_and_save_results')
    
    def test_bjdc_result_collector_exists(self):
        """测试北京单场赛果获取器存在"""
        from app.crawler.bjdc_result import BjdcResultCollector
        collector = BjdcResultCollector()
        assert collector is not None
        assert hasattr(collector, 'get_and_save_results')
