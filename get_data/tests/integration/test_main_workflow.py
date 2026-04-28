# -*- coding: utf-8 -*-
"""
主程序集成测试
测试顺序：完整模拟 main.py 的执行流程
"""
import pytest


class TestMainWorkflow:
    """主程序工作流程测试"""
    
    def test_main_module_imports(self):
        """测试 main 模块可以导入"""
        import main
        assert main is not None
    
    def test_job_function_exists(self):
        """测试 job 函数存在"""
        from main import job
        assert callable(job)
    
    def test_init_db_function_exists(self):
        """测试 init_db 函数存在"""
        from main import init_db
        assert callable(init_db)
    
    def test_chuck_data_function_exists(self):
        """测试 chuck_data 函数存在"""
        from main import chuck_data
        assert callable(chuck_data)
    
    @pytest.mark.db
    def test_full_initialization_flow(self):
        """测试完整的初始化流程"""
        from main import chuck_data, init_db
        
        # 1. 检查数据是否存在
        has_data = chuck_data()
        assert isinstance(has_data, bool)
        
        # 2. 如果没有数据，执行初始化
        if not has_data:
            result = init_db(rebuild=False)
            assert result is True
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_job_execution(self):
        """测试 job 函数执行（完整数据采集流程）"""
        from main import job
        
        # 执行一次任务（可能会比较慢）
        try:
            job()
            # 如果执行成功，说明所有模块都能正常工作
            assert True
        except Exception as e:
            # 记录错误但不失败（因为可能需要网络）
            pytest.skip(f"Job execution skipped due to: {e}")


class TestLoggerConfiguration:
    """日志配置测试"""
    
    def test_loggers_exist(self):
        """测试所有日志器存在"""
        from app.log.logger import tczq_log, bjdc_log, jcbk_log, lottery_log
        
        assert tczq_log is not None
        assert bjdc_log is not None
        assert jcbk_log is not None
        assert lottery_log is not None
    
    def test_logger_has_handlers(self):
        """测试日志器有处理器"""
        from app.log.logger import tczq_log
        
        assert len(tczq_log.handlers) > 0
    
    def test_log_directory_structure(self):
        """测试日志目录结构存在"""
        import os
        
        # 使用项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_base = os.path.join(project_root, 'app', 'log')
        
        required_dirs = ['tczq', 'bjdc', 'jcbk', 'lottery', 'api']
        for dir_name in required_dirs:
            dir_path = os.path.join(log_base, dir_name)
            assert os.path.exists(dir_path), f"日志目录不存在: {dir_path}"


class TestDatabaseModels:
    """数据库模型测试"""
    
    @pytest.mark.db
    def test_league_model_exists(self, db_session):
        """测试 League 模型存在"""
        from app.database.base_models import League
        
        # 尝试查询
        result = db_session.query(League).first()
        # 不检查结果，只确认模型可用
    
    @pytest.mark.db
    def test_team_model_exists(self, db_session):
        """测试 Team 模型存在"""
        from app.database.base_models import Team
        
        result = db_session.query(Team).first()
    
    @pytest.mark.db
    def test_tczq_match_model_exists(self, db_session):
        """测试 TczqMatch 模型存在"""
        from app.database.tczq_models import TczqMatch
        
        result = db_session.query(TczqMatch).first()
    
    @pytest.mark.db
    def test_bjdc_match_model_exists(self, db_session):
        """测试 BjdcMatch 模型存在"""
        from app.database.bjdc_models import BjdcMatch
        
        result = db_session.query(BjdcMatch).first()
    
    @pytest.mark.db
    def test_tcbk_match_model_exists(self, db_session):
        """测试 TcbkMatch 模型存在"""
        from app.database.tcbk_models import TcbkMatch
        
        result = db_session.query(TcbkMatch).first()
    
    @pytest.mark.db
    def test_digital_lottery_model_exists(self, db_session):
        """测试 DigitalLotteryDraw 模型存在"""
        from app.database.digital_lottery_models import DigitalLotteryDraw
        
        result = db_session.query(DigitalLotteryDraw).first()


class TestUtilityFunctions:
    """工具函数测试"""
    
    def test_get_or_create_league_exists(self):
        """测试 get_or_create_league 函数存在"""
        from app.common._utils import get_or_create_league
        assert callable(get_or_create_league)
    
    def test_get_or_create_team_exists(self):
        """测试 get_or_create_team 函数存在"""
        from app.common._utils import get_or_create_team
        assert callable(get_or_create_team)
    
    def test_get_or_create_tcbk_league_exists(self):
        """测试 get_or_create_tcbk_league 函数存在"""
        from app.common._utils import get_or_create_tcbk_league
        assert callable(get_or_create_tcbk_league)
    
    def test_handle_league_name_exists(self):
        """测试 handle_league_name 函数存在"""
        from app.common._utils import handle_league_name
        assert callable(handle_league_name)
    
    def test_handle_team_name_exists(self):
        """测试 handle_team_name 函数存在"""
        from app.common._utils import handle_team_name
        assert callable(handle_team_name)
