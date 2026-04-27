# -*- coding: utf-8 -*-
"""
数据库核心操作类
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from config import settings
import time
import logging

# 获取日志记录器
logger = logging.getLogger('db_core')


class QueryWrapper:
    """
    查询包装器，自动处理MySQL连接断开问题
    拦截 .first(), .all(), .one() 等方法的调用，在连接断开时自动重试
    """
    
    def __init__(self, query_obj, db_instance, retry_count=3, retry_delay=2):
        self._query = query_obj
        self._db = db_instance
        self._retry_count = retry_count
        self._retry_delay = retry_delay
    
    def _is_connection_error(self, e):
        """判断是否为连接断开错误"""
        error_msg = str(e).lower()
        return 'mysql server has gone away' in error_msg or 'connectionabortederror' in error_msg
    
    def _reconnect(self):
        """重新连接数据库"""
        try:
            if self._db.session:
                try:
                    self._db.session.rollback()
                except:
                    pass
                try:
                    self._db.session.close()
                except:
                    pass
        except:
            pass
        self._db.session = None
        # 重建会话
        self._db.session = self._db.Session()
        logger.warning("数据库连接已重建")
    
    def _execute_with_retry(self, func, *args, **kwargs):
        """带重试机制的执行方法"""
        last_error = None
        for attempt in range(self._retry_count):
            try:
                # 确保会话有效
                if not self._db.session or not self._db.session.is_active:
                    self._reconnect()
                
                # 重新构建查询对象（因为会话可能已重建）
                if attempt > 0:
                    # 注意：这里需要重新创建查询，但保持相同的过滤条件
                    # 由于SQLAlchemy的query对象是不可变的，我们需要从原始query复制
                    pass
                
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_error = e
                if self._is_connection_error(e):
                    logger.warning(f"检测到连接断开，尝试重连 ({attempt+1}/{self._retry_count})...")
                    self._reconnect()
                    time.sleep(self._retry_delay * (2 ** attempt))  # 指数退避
                    continue
                else:
                    raise e
        
        # 所有重试都失败
        raise last_error
    
    def first(self):
        """拦截 .first() 方法"""
        return self._execute_with_retry(self._query.first)
    
    def all(self):
        """拦截 .all() 方法"""
        return self._execute_with_retry(self._query.all)
    
    def one(self):
        """拦截 .one() 方法"""
        return self._execute_with_retry(self._query.one)
    
    def scalar(self):
        """拦截 .scalar() 方法"""
        return self._execute_with_retry(self._query.scalar)
    
    def count(self):
        """拦截 .count() 方法"""
        return self._execute_with_retry(self._query.count)
    
    def __getattr__(self, name):
        """其他方法直接代理到原始查询对象"""
        attr = getattr(self._query, name)
        if callable(attr):
            # 如果是可调用对象，包装它以支持链式调用
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                # 如果返回的是查询对象，继续包装
                if hasattr(result, 'first') and hasattr(result, 'all'):
                    return QueryWrapper(result, self._db, self._retry_count, self._retry_delay)
                return result
            return wrapper
        return attr


class DataDB():
    """
    体育数据数据库操作类（soccer_data）
    用于查询比赛、赔率等数据（只读）
    """
    
    def __init__(self):
        """
        初始化数据库连接
        """
        self.engine = create_engine(
            f"mysql+pymysql://{settings.DATA_DB_USER}:{settings.DATA_DB_PASSWORD}@{settings.DATA_DB_HOST}:{settings.DATA_DB_PORT}/{settings.DATA_DB_NAME}",
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=15,
            max_overflow=30,
            pool_timeout=30,
            connect_args={
                'connect_timeout': 30,
                'read_timeout': 60,
                'write_timeout': 60,
                'charset': 'utf8mb4'
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

    def query(self, obj, close=False, retry_count=3, retry_delay=2):
        """
        查询数据库（返回智能包装的查询对象，自动处理连接断开）
        
        Args:
            obj: 要查询的对象类型
            close: 是否在操作后关闭会话
            retry_count: 重试次数
            retry_delay: 重试间隔（秒）
            
        Returns:
            QueryWrapper: 包装后的查询对象，支持 .first(), .all() 等方法，自动重试
        """
        # 检查会话是否有效，如果无效则创建新会话
        if not self.session or not self.session.is_active:
            self.session = self.Session()
        
        # 创建原始查询对象
        query_obj = self.session.query(obj)
        
        # 返回包装后的查询对象，自动处理连接断开
        return QueryWrapper(query_obj, self, retry_count, retry_delay)

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
    
    def rollback(self):
        """
        回滚当前事务
        """
        try:
            if self.session and self.session.is_active:
                self.session.rollback()
        except Exception as e:
            # 如果回滚失败，关闭会话并重建
            if self.session:
                try:
                    self.session.close()
                except:
                    pass
                self.session = None


class SelfDB():
    """
    API 服务数据库操作类（soccer_server）
    用于用户管理、查询日志等 API 服务相关数据
    """
    
    def __init__(self):
        """
        初始化数据库连接
        """
        self.engine = create_engine(
            f"mysql+pymysql://{settings.SERVER_DB_USER}:{settings.SERVER_DB_PASSWORD}@{settings.SERVER_DB_HOST}:{settings.SERVER_DB_PORT}/{settings.SERVER_DB_NAME}",
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=5,  # API 服务数据库连接数可以小一些
            max_overflow=10,
            pool_timeout=30,
            connect_args={
                'connect_timeout': 30,
                'read_timeout': 60,
                'write_timeout': 60,
                'charset': 'utf8mb4'
            }
        )
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
    
    # 复用 DataDB 的所有方法（add, query, delete, update, close, commit, rollback）
    # 这里直接复制相同的方法实现
    
    def add(self, obj, close=True, retry_count=5, retry_delay=2):
        """添加对象到数据库"""
        for attempt in range(retry_count):
            try:
                if not self.session or not self.session.is_active:
                    self.session = self.Session()
                    
                self.session.add(obj)
                self.session.commit()
                return obj
            except OperationalError as e:
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
                    time.sleep(retry_delay * (2 ** attempt))
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

    def query(self, obj, close=False, retry_count=3, retry_delay=2):
        """查询数据库"""
        if not self.session or not self.session.is_active:
            self.session = self.Session()
        
        query_obj = self.session.query(obj)
        return QueryWrapper(query_obj, self, retry_count, retry_delay)

    def delete(self, obj, close=True, retry_count=5, retry_delay=2):
        """从数据库中删除对象"""
        for attempt in range(retry_count):
            try:
                if not self.session or not self.session.is_active:
                    self.session = self.Session()
                    
                self.session.delete(obj)
                self.session.commit()
                return
            except OperationalError as e:
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
                    time.sleep(retry_delay * (2 ** attempt))
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
        """更新数据库中的对象"""
        for attempt in range(retry_count):
            try:
                if not self.session or not self.session.is_active:
                    self.session = self.Session()
                    
                self.session.add(obj)
                self.session.commit()
                return
            except OperationalError as e:
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
                    time.sleep(retry_delay * (2 ** attempt))
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
        """关闭数据库会话"""
        if self.session:
            self.session.close()
            self.session = None
    
    def commit(self):
        """提交当前事务"""
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
    
    def rollback(self):
        """回滚当前事务"""
        try:
            if self.session and self.session.is_active:
                self.session.rollback()
        except Exception as e:
            if self.session:
                try:
                    self.session.close()
                except:
                    pass
                self.session = None


# 为了向后兼容，保留 mydb 别名（指向 DataDB）
mydb = DataDB

# 不再创建全局数据库实例，用户需要在使用时动态创建