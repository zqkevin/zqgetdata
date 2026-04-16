# -*- coding: utf-8 -*-
"""
数据库初始化单元测试
测试顺序：main.py -> chuck_data() -> init_db()
"""
import pytest


class TestDatabaseInit:
    """数据库初始化测试"""
    
    def test_init_db_module_import(self):
        """测试 init_db 模块可以导入"""
        from app.common.init_db import init_all_databases
        assert callable(init_all_databases)
    
    def test_init_restructured_module_import(self):
        """测试 init_restructured_db 模块可以导入"""
        from app.common.init_restructured_db import init_restructured_database
        assert callable(init_restructured_database)
    
    def test_init_db_has_required_functions(self):
        """测试 init_db 包含必要的函数"""
        from app.common import init_db
        
        assert hasattr(init_db, 'init_all_databases')
        assert hasattr(init_db, 'init_digital_lottery_database')
        assert hasattr(init_db, 'init_tcbk_database')
        assert hasattr(init_db, 'init_tczq_database')
        assert hasattr(init_db, 'init_league_data')
        assert hasattr(init_db, 'init_team_data')
    
    def test_init_restructured_has_required_functions(self):
        """测试 init_restructured_db 包含必要的函数"""
        from app.common import init_restructured_db
        
        assert hasattr(init_restructured_db, 'init_restructured_database')
        assert hasattr(init_restructured_db, 'check_table_exists')


class TestDatabaseConnection:
    """数据库连接测试"""
    
    @pytest.mark.db
    def test_database_connection(self, db_engine):
        """测试数据库连接成功"""
        from sqlalchemy import text
        result = db_engine.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
    
    @pytest.mark.db
    def test_database_has_required_tables(self, db_session):
        """测试数据库包含必要的表"""
        from sqlalchemy import inspect
        
        inspector = inspect(db_session.bind)
        tables = inspector.get_table_names()
        
        # 基础表
        assert 'league' in tables
        assert 'team' in tables
        
        # 体彩足球表
        assert any(t.startswith('tczq_') for t in tables)
        
        # 北京单场表
        assert any(t.startswith('bjdc_') for t in tables)
        
        # 体彩篮球表
        assert any(t.startswith('tcbk_') for t in tables)
        
        # 数字彩表
        assert any(t.startswith('digital_') for t in tables)


class TestMainInitLogic:
    """main.py 初始化逻辑测试"""
    
    def test_chuck_data_function_exists(self):
        """测试 chuck_data 函数存在"""
        from main import chuck_data
        assert callable(chuck_data)
    
    def test_init_db_function_exists(self):
        """测试 init_db 函数存在"""
        from main import init_db
        assert callable(init_db)
    
    def test_init_db_accepts_rebuild_parameter(self):
        """测试 init_db 接受 rebuild 参数"""
        from main import init_db
        import inspect
        
        sig = inspect.signature(init_db)
        assert 'rebuild' in sig.parameters
    
    @pytest.mark.db
    def test_chuck_data_returns_boolean(self):
        """测试 chuck_data 返回布尔值"""
        from main import chuck_data
        result = chuck_data()
        assert isinstance(result, bool)
