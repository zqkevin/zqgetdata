# -*- coding: utf-8 -*-
"""
配置模块单元测试
测试顺序：main.py 启动 -> 配置加载
"""
import pytest


class TestConfig:
    """配置加载测试"""
    
    def test_config_exists(self):
        """测试配置文件存在"""
        from config import config
        assert config is not None
    
    def test_config_has_local_section(self):
        """测试配置包含 local 部分"""
        from config import config
        assert 'local' in config
    
    def test_local_config_structure(self):
        """测试 local 配置结构完整"""
        from config import config
        local = config['local']
        
        required_keys = ['host', 'port', 'user', 'password', 'database']
        for key in required_keys:
            assert key in local, f"配置缺少 {key}"
    
    def test_local_config_values(self):
        """测试 local 配置值类型正确"""
        from config import config
        local = config['local']
        
        assert isinstance(local['host'], str)
        assert isinstance(local['port'], int)
        assert isinstance(local['user'], str)
        assert isinstance(local['password'], str)
        assert isinstance(local['database'], str)
    
    def test_env_var_override(self, monkeypatch):
        """测试环境变量可以覆盖配置"""
        monkeypatch.setenv('DB_HOST', 'test_host')
        monkeypatch.setenv('DB_PORT', '3307')
        monkeypatch.setenv('DB_USER', 'test_user')
        monkeypatch.setenv('DB_PASSWORD', 'test_pass')
        monkeypatch.setenv('DB_NAME', 'test_db')
        
        # 重新导入配置
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        assert config_module.DB_HOST == 'test_host'
        assert config_module.DB_PORT == 3307
        assert config_module.DB_USER == 'test_user'
        assert config_module.DB_PASSWORD == 'test_pass'
        assert config_module.DB_NAME == 'test_db'
