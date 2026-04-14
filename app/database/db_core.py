# -*- coding: utf-8 -*-
"""
数据库核心操作类
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from config import config
import time


class mydb():
    """
    数据库操作类，封装了基本的CRUD操作
    """
    
    def __init__(self):
        """
        初始化数据库连接
        """
        db_config = config['local']
        self.engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
            pool_pre_ping=True,  # 增加连接保活，提升稳定性
            pool_recycle=1800,   # 缩短连接回收时间，从3600秒改为1800秒
            pool_size=15,        # 增加连接池大小，从10改为15
            max_overflow=30,     # 增加最大溢出连接数，从20改为30
            pool_timeout=30,     # 增加连接超时时间
            connect_args={
                'connect_timeout': 30,  # 连接超时时间
                'read_timeout': 60,     # 读取超时时间
                'write_timeout': 60,    # 写入超时时间
                'charset': 'utf8mb4'    # 字符集
            }
        )
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def add(self, obj, close=True, retry_count=5, retry_delay=2):
        """
        添加对象到数据库
        
        Args:
            obj: 要添加的对象
            close: 是否在操作后关闭会话
            retry_count: 重试次数
            retry_delay: 重试间隔（秒）
        
        Returns:
            添加后的对象（包含自增ID）
        """
        for attempt in range(retry_count):
            try:
                # 检查会话是否有效，如果无效则创建新会话
                if not self.session or not self.session.is_active:
                    self.session = self.Session()
                    
                self.session.add(obj)
                self.session.commit()
                return obj
            except OperationalError as e:
                # 捕获连接错误，重试
                if self.session is not None:
                    try:
                        self.session.rollback()
                    except:
                        pass
                    try:
                        self.session.close()
                    except:
                        pass
                self.session = None
                if attempt < retry_count - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避策略
                    continue
                else:
                    raise e
            except Exception as e:
                if self.session is not None:
                    try:
                        self.session.rollback()
                    except:
                        pass
                raise e
            finally:
                if close and self.session is not None:
                    try:
                        self.session.close()
                        self.session = None
                    except:
                        self.session = None

    def query(self, obj, close=False, retry_count=5, retry_delay=2):
        """
        查询数据库
        
        Args:
            obj: 要查询的对象类型
            close: 是否在操作后关闭会话
            retry_count: 重试次数
            retry_delay: 重试间隔（秒）
            
        Returns:
            查询结果
        """
        for attempt in range(retry_count):
            try:
                # 检查会话是否有效，如果无效则创建新会话
                if not self.session or not self.session.is_active:
                    self.session = self.Session()
                    
                da = self.session.query(obj)
                return da
            except OperationalError as e:
                # 捕获连接错误，重试
                if self.session is not None:
                    try:
                        self.session.close()
                    except:
                        pass
                    self.session = None
                if attempt < retry_count - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避策略
                    continue
                else:
                    raise e
            except Exception as e:
                if self.session is not None and close:
                    try:
                        self.session.close()
                        self.session = None
                    except:
                        self.session = None
                raise e
            finally:
                if close and self.session is not None:
                    try:
                        self.session.close()
                        self.session = None
                    except:
                        self.session = None

    def delete(self, obj, close=True, retry_count=5, retry_delay=2):
        """
        从数据库中删除对象
        
        Args:
            obj: 要删除的对象
            close: 是否在操作后关闭会话
            retry_count: 重试次数
            retry_delay: 重试间隔（秒）
        """
        for attempt in range(retry_count):
            try:
                # 检查会话是否有效，如果无效则创建新会话
                if not self.session or not self.session.is_active:
                    self.session = self.Session()
                    
                self.session.delete(obj)
                self.session.commit()
                return
            except OperationalError as e:
                # 捕获连接错误，重试
                if self.session is not None:
                    try:
                        self.session.rollback()
                    except:
                        pass
                    try:
                        self.session.close()
                    except:
                        pass
                self.session = None
                if attempt < retry_count - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避策略
                    continue
                else:
                    raise e
            except Exception as e:
                if self.session is not None:
                    try:
                        self.session.rollback()
                    except:
                        pass
                raise e
            finally:
                if close and self.session is not None:
                    try:
                        self.session.close()
                        self.session = None
                    except:
                        self.session = None

    def update(self, obj, close=True, retry_count=5, retry_delay=2):
        """
        更新数据库中的对象
        
        Args:
            obj: 要更新的对象
            close: 是否在操作后关闭会话
            retry_count: 重试次数
            retry_delay: 重试间隔（秒）
        """
        for attempt in range(retry_count):
            try:
                # 检查会话是否有效，如果无效则创建新会话
                if not self.session or not self.session.is_active:
                    self.session = self.Session()
                    
                self.session.add(obj)
                self.session.commit()
                return
            except OperationalError as e:
                # 捕获连接错误，重试
                if self.session is not None:
                    try:
                        self.session.rollback()
                    except:
                        pass
                    try:
                        self.session.close()
                    except:
                        pass
                self.session = None
                if attempt < retry_count - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避策略
                    continue
                else:
                    raise e
            except Exception as e:
                if self.session is not None:
                    try:
                        self.session.rollback()
                    except:
                        pass
                raise e
            finally:
                if close and self.session is not None:
                    try:
                        self.session.close()
                        self.session = None
                    except:
                        self.session = None

    def close(self):
        """
        关闭数据库会话
        """
        if self.session:
            self.session.close()
            self.session = None
    
    def commit(self):
        """
        提交当前事务
        """
        try:
            if self.session and self.session.is_active:
                self.session.commit()
        except Exception as e:
            if self.session:
                try:
                    self.session.rollback()
                except:
                    pass
            raise e


# 不再创建全局数据库实例，用户需要在使用时动态创建